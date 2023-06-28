from OTAnalytics.application.analysis.traffic_counting import (
    CountingSpecificationDto,
    Exporter,
    ExporterFactory,
)
from OTAnalytics.plugin_parser.otvision_parser import CsvExport


class SimpleExporterFactory(ExporterFactory):
    def create_exporter(self, specification: CountingSpecificationDto) -> Exporter:
        factories = {"csv": lambda: CsvExport(specification.output_file)}
        return factories[specification.format.lower()]()
