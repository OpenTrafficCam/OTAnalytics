from collections import defaultdict
from datetime import timedelta
from pathlib import Path
from typing import Iterable

from pandas import DataFrame, to_datetime

from OTAnalytics.application.analysis.traffic_counting import (
    LEVEL_CLASSIFICATION,
    LEVEL_END_TIME,
    LEVEL_FLOW,
    LEVEL_FROM_SECTION,
    LEVEL_START_TIME,
    LEVEL_TO_SECTION,
    AddSectionInformation,
    Count,
    Exporter,
    ExporterFactory,
    FillEmptyCount,
    Tag,
    create_flow_tag,
    create_mode_tag,
    create_timeslot_tag,
)
from OTAnalytics.application.analysis.traffic_counting_specification import (
    ExportFormat,
    ExportSpecificationDto,
)
from OTAnalytics.application.export_formats.export_mode import ExportMode
from OTAnalytics.application.logger import logger

START_DATE = "start occurrence date"
START_TIME = "start occurrence time"
END_DATE = "end occurrence date"
END_TIME = "end occurrence time"

DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S"

DESIRED_COLUMNS_ORDER = [
    LEVEL_START_TIME,
    START_DATE,
    START_TIME,
    LEVEL_END_TIME,
    END_DATE,
    END_TIME,
    LEVEL_CLASSIFICATION,
    LEVEL_FLOW,
    LEVEL_FROM_SECTION,
    LEVEL_TO_SECTION,
]


def count_to_dataframe(count: Count) -> DataFrame:
    return count_dict_to_dataframe(count.to_dict())


def count_dict_to_dataframe(count_dict: dict[Tag, int]) -> DataFrame:
    # setup dataframe
    indexed: list[dict] = []
    for tag, value in count_dict.items():
        result_dict: dict = tag.as_dict()
        result_dict["count"] = value
        indexed.append(result_dict)
    dataframe = DataFrame(indexed)

    if dataframe.empty:
        return dataframe

    # add detailed date time columns
    start_occurrence = to_datetime(dataframe[LEVEL_START_TIME])
    end_occurrence = to_datetime(dataframe[LEVEL_END_TIME])
    dataframe[START_DATE] = start_occurrence.dt.strftime(DATE_FORMAT)
    dataframe[START_TIME] = start_occurrence.dt.strftime(TIME_FORMAT)
    dataframe[END_DATE] = end_occurrence.dt.strftime(DATE_FORMAT)
    dataframe[END_TIME] = end_occurrence.dt.strftime(TIME_FORMAT)

    # set column order
    dataframe = dataframe[
        [col for col in DESIRED_COLUMNS_ORDER if col in dataframe.columns]
        + [col for col in dataframe.columns if col not in DESIRED_COLUMNS_ORDER]
    ]
    dataframe = dataframe.sort_values(
        by=[LEVEL_START_TIME, LEVEL_END_TIME, LEVEL_CLASSIFICATION]
    )
    return dataframe


class CsvExport(Exporter):
    """
    A counts Exporter exporting to .csv format.
    Allows to either overwrite result file or incrementally collect count data.

    Incrementally exporting count data turns this CsvExporter
    into a stateful exporter. Counts are aggregated until ExportMode.FLUSH
    is provided.
    """

    def __init__(self, output_file: str) -> None:
        self._output_file = output_file
        self._counts: dict[Tag, int] = defaultdict(int)

    def export(self, counts: Count, export_mode: ExportMode) -> None:
        logger().info(f"Exporting counts to {self._output_file}")

        for tag, value in counts.to_dict().items():
            self._counts[tag] += value

        if export_mode.is_final_write():
            dataframe = count_dict_to_dataframe(self._counts)
            if dataframe.empty:
                logger().info("Nothing to count.")
                return

            dataframe.to_csv(self.__create_path(), index=False)
            logger().info(f"Counts saved at {self._output_file}")

            self._counts.clear()

    def __create_path(self) -> Path:
        fixed_file_ending = (
            self._output_file
            if self._output_file.lower().endswith(".csv")
            else self._output_file + ".csv"
        )
        path = Path(fixed_file_ending)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path


class SimpleExporterFactory(ExporterFactory):
    def __init__(self) -> None:
        self._formats = {
            ExportFormat("CSV", ".csv"): lambda output_file: CsvExport(output_file)
        }
        self._factories = {
            format.name: factory for format, factory in self._formats.items()
        }

    def get_supported_formats(self) -> Iterable[ExportFormat]:
        return self._formats.keys()

    def create_exporter(self, specification: ExportSpecificationDto) -> Exporter:
        return self._factories[specification.format](specification.output_file)


class TagExploder:
    """
    This class creates all combinations of tags for a given ExportSpecificationDto.
    The resulting tags are a cross product of the flows, the modes and the time
    intervals. The list of tags can then be used as the maximum set of tags in the
    export.
    """

    def __init__(self, specification: ExportSpecificationDto):
        self._specification = specification

    def explode(self) -> list[Tag]:
        tags = []
        start_without_seconds = (
            self._specification.counting_specification.start.replace(
                second=0, microsecond=0
            )
        )
        maximum = self._specification.counting_specification.end - start_without_seconds
        duration = int(maximum.total_seconds())
        interval = self._specification.counting_specification.interval_in_minutes * 60
        for flow in self._specification.flow_name_info:
            for mode in self._specification.counting_specification.modes:
                for delta in range(0, duration, interval):
                    offset = timedelta(seconds=delta)
                    start = start_without_seconds + offset
                    interval_time = timedelta(seconds=interval)
                    tag = (
                        create_flow_tag(flow.name)
                        .combine(create_mode_tag(mode))
                        .combine(create_timeslot_tag(start, interval_time))
                    )
                    tags.append(tag)
        return tags


class FillZerosExporter(Exporter):
    def __init__(self, other: Exporter, tag_exploder: TagExploder) -> None:
        self._other = other
        self._tag_exploder = tag_exploder

    def export(self, counts: Count, export_mode: ExportMode) -> None:
        tags = self._tag_exploder.explode()
        self._other.export(FillEmptyCount(counts, tags), export_mode)


class FillZerosExporterFactory(ExporterFactory):
    def __init__(self, other: ExporterFactory) -> None:
        self.other = other

    def get_supported_formats(self) -> Iterable[ExportFormat]:
        return self.other.get_supported_formats()

    def create_exporter(self, specification: ExportSpecificationDto) -> Exporter:
        return FillZerosExporter(
            self.other.create_exporter(specification),
            TagExploder(specification),
        )


class AddSectionInformationExporter(Exporter):
    def __init__(self, other: Exporter, specification: ExportSpecificationDto) -> None:
        self._other = other
        self._specification = specification

    def export(self, counts: Count, export_mode: ExportMode) -> None:
        flow_info_dict = {
            flow_dto.name: flow_dto for flow_dto in self._specification.flow_name_info
        }
        self._other.export(AddSectionInformation(counts, flow_info_dict), export_mode)


class AddSectionInformationExporterFactory(ExporterFactory):
    def __init__(self, other: ExporterFactory) -> None:
        self.other = other

    def get_supported_formats(self) -> Iterable[ExportFormat]:
        return self.other.get_supported_formats()

    def create_exporter(self, specification: ExportSpecificationDto) -> Exporter:
        return AddSectionInformationExporter(
            self.other.create_exporter(specification), specification
        )


class CacheException(Exception):

    def __init__(
        self,
        message: str,
        output_format: str,
        output_file: str,
        export_mode: ExportMode,
    ) -> None:
        super().__init__(
            message
            + f"Error occurred when exporting {output_format} to {output_file} using"
            + " export mode {export_mode}"
        )


class CachedExporterFactory(ExporterFactory):

    def __init__(self, other: ExporterFactory) -> None:
        self.other = other
        self._cache: dict[tuple[str, str], Exporter] = dict()

    def get_supported_formats(self) -> Iterable[ExportFormat]:
        return self.other.get_supported_formats()

    def create_exporter(self, specification: ExportSpecificationDto) -> Exporter:
        count_specification = specification.counting_specification
        export_mode = count_specification.export_mode

        key = (count_specification.output_format, count_specification.output_file)
        key_exists = key in self._cache.keys()

        exporter: Exporter
        if export_mode.is_first_write():
            if key_exists:
                raise CacheException(
                    "Exporter already exists for format+file upon first write!"
                    + " Maybe previous export was not finished or cache was not"
                    + "cleared properly.",
                    count_specification.output_format,
                    count_specification.output_file,
                    export_mode,
                )

            exporter = self.other.create_exporter(specification)
            self._cache[key] = exporter

        else:
            if not key_exists:
                raise CacheException(
                    "Exporter missing in cache for format+file upon subsequent write!"
                    + "Maybe the cache was cleared too early.",
                    count_specification.output_format,
                    count_specification.output_file,
                    export_mode,
                )
            exporter = self._cache[key]

        if export_mode.is_final_write():
            del self._cache[key]

        return exporter
