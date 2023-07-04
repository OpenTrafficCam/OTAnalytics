from typing import Iterable

from OTAnalytics.application.analysis.traffic_counting import (
    CountingSpecificationDto,
    Exporter,
    ExporterFactory,
    ExportFormat,
)
from OTAnalytics.plugin_parser.otvision_parser import CsvExport


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
