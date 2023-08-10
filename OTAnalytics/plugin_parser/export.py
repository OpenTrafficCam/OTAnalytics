from pathlib import Path
from typing import Iterable

from pandas import DataFrame

from OTAnalytics.application.analysis.traffic_counting import (
    Count,
    Exporter,
    ExporterFactory,
    FillEmptyCount,
    Tag,
)
from OTAnalytics.application.analysis.traffic_counting_specification import (
    ExportFormat,
    ExportSpecificationDto,
)


class CsvExport(Exporter):
    def __init__(self, output_file: str) -> None:
        self._output_file = output_file

    def export(self, counts: Count) -> None:
        print(f"Exporting counts {counts} to {self._output_file}")
        dataframe = self.__create_data_frame(counts)
        dataframe.to_csv(self.__create_path(), index=False)

    def __create_data_frame(self, counts: Count) -> DataFrame:
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


class FillZerosExporter(Exporter):
    def __init__(self, other: Exporter, specification: ExportSpecificationDto) -> None:
        self._other = other
        self._specification = specification

    def export(self, counts: Count) -> None:
        tags = self.__create_tags()
        self._other.export(FillEmptyCount(counts, tags))

    def __create_tags(self) -> list[Tag]:
        return []


class FillZerosExporterFactory(ExporterFactory):
    def __init__(self, other: ExporterFactory) -> None:
        self.other = other

    def get_supported_formats(self) -> Iterable[ExportFormat]:
        return self.other.get_supported_formats()

    def create_exporter(self, specification: ExportSpecificationDto) -> Exporter:
        return FillZerosExporter(
            self.other.create_exporter(specification), specification
        )
