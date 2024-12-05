from typing import Iterable

from pandas import DataFrame

from OTAnalytics.application.use_cases.track_statistics_export import (
    ExportFormat,
    TrackStatisticsBuilder,
    TrackStatisticsExporter,
    TrackStatisticsExportSpecification,
)

CSV_FORMAT = ExportFormat("CSV", ".csv")


class TrackStatisticsCsvExporter(TrackStatisticsExporter):

    @property
    def format(self) -> ExportFormat:
        return ExportFormat("csv", ".csv")

    def _serialize(self, dtos: list[dict]) -> None:
        DataFrame(dtos).to_csv(self._outputfile, index=False)


class SimpleTrackStatisticsExporterFactory:
    def __init__(
        self,
    ) -> None:
        self._formats = {
            CSV_FORMAT: lambda builder, output_file: TrackStatisticsCsvExporter(
                builder, output_file
            )
        }
        self._factories = {
            export_format.name: factory
            for export_format, factory in self._formats.items()
        }

    def get_supported_formats(self) -> Iterable[ExportFormat]:
        """
        Returns an iterable of the supported export formats.

        Returns:
            Iterable[ExportFormat]: supported export formats.
        """
        return self._formats.keys()

    def create(
        self, specification: TrackStatisticsExportSpecification
    ) -> TrackStatisticsExporter:
        """
        Create the exporter for the given road user assignment export specification.

        Args:
            specification (ExportSpecification): specification of the Exporter.

        Returns:
            TrackStatisticsExporter: Exporter to export road user assignments.
        """
        return self._factories[specification.format](
            TrackStatisticsBuilder(), specification.save_path
        )
