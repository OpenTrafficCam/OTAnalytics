from datetime import timedelta
from pathlib import Path
from typing import Iterable

from pandas import DataFrame

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
from OTAnalytics.application.logger import logger


class CsvExport(Exporter):
    def __init__(self, output_file: str) -> None:
        self._output_file = output_file

    def export(self, counts: Count) -> None:
        logger().info(f"Exporting counts to {self._output_file}")
        dataframe = self.__create_data_frame(counts)
        dataframe = self._set_column_order(dataframe)
        dataframe = dataframe.sort_values(
            by=[LEVEL_START_TIME, LEVEL_END_TIME, LEVEL_CLASSIFICATION]
        )
        dataframe.to_csv(self.__create_path(), index=False)

    @staticmethod
    def _set_column_order(dataframe: DataFrame) -> DataFrame:
        desired_columns_order = [
            LEVEL_START_TIME,
            LEVEL_END_TIME,
            LEVEL_CLASSIFICATION,
            LEVEL_FLOW,
            LEVEL_FROM_SECTION,
            LEVEL_TO_SECTION,
        ]
        dataframe = dataframe[
            desired_columns_order
            + [col for col in dataframe.columns if col not in desired_columns_order]
        ]

        return dataframe

    @staticmethod
    def __create_data_frame(counts: Count) -> DataFrame:
        transformed = counts.to_dict()
        indexed: list[dict] = []
        for key, value in transformed.items():
            result_dict: dict = key.as_dict()
            result_dict["count"] = value
            indexed.append(result_dict)
        return DataFrame.from_dict(indexed)

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

    def export(self, counts: Count) -> None:
        tags = self._tag_exploder.explode()
        self._other.export(FillEmptyCount(counts, tags))


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

    def export(self, counts: Count) -> None:
        flow_info_dict = {
            flow_dto.name: flow_dto for flow_dto in self._specification.flow_name_info
        }
        self._other.export(AddSectionInformation(counts, flow_info_dict))


class AddSectionInformationExporterFactory(ExporterFactory):
    def __init__(self, other: ExporterFactory) -> None:
        self.other = other

    def get_supported_formats(self) -> Iterable[ExportFormat]:
        return self.other.get_supported_formats()

    def create_exporter(self, specification: ExportSpecificationDto) -> Exporter:
        return AddSectionInformationExporter(
            self.other.create_exporter(specification), specification
        )
