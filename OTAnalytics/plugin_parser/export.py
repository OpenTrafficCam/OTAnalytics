from pathlib import Path
from typing import Iterable

from pandas import DataFrame

from OTAnalytics.application.analysis.traffic_counting import (
    Count,
    CountingSpecificationDto,
    Exporter,
    ExporterFactory,
    ExportFormat,
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
        super().__init__()
        self._formats = {
            ExportFormat("CSV", ".csv"): lambda output_file: CsvExport(output_file)
        }
        self._factories = {
            format.name: factory for format, factory in self._formats.items()
        }

    def get_supported_formats(self) -> Iterable[ExportFormat]:
        return self._formats.keys()

    def create_exporter(self, specification: CountingSpecificationDto) -> Exporter:
        return self._factories[specification.format](specification.output_file)
