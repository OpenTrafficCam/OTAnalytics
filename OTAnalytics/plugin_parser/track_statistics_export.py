from pathlib import Path
from typing import Iterable

from pandas import DataFrame

from OTAnalytics.application.export_formats.export_mode import ExportMode
from OTAnalytics.application.logger import logger
from OTAnalytics.application.use_cases.track_statistics_export import (
    ExportFormat,
    TrackStatisticsBuilder,
    TrackStatisticsExporter,
    TrackStatisticsExporterFactory,
    TrackStatisticsExportSpecification,
)

CSV_FORMAT = ExportFormat("CSV", ".csv")


class TrackStatisticsCsvExporter(TrackStatisticsExporter):

    @property
    def format(self) -> ExportFormat:
        return ExportFormat("csv", ".csv")

    def _serialize(self, dtos: dict) -> None:
        logger().info(f"Exporting track statistics to {self._outputfile}")

        DataFrame([dtos]).to_csv(self._outputfile, index=False)

        logger().info(f"Track statistics saved at {self._outputfile}")


class SimpleTrackStatisticsExporterFactory(TrackStatisticsExporterFactory):
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


class CacheTrackStatisticsException(Exception):

    def __init__(
        self,
        message: str,
        save_path: Path,
        format: str,
        export_mode: ExportMode,
    ) -> None:
        super().__init__(
            message
            + f"Error occurred when exporting {format} to {save_path} using"
            + " export mode {export_mode}"
        )


class CachedTrackStatisticsExporterFactory(TrackStatisticsExporterFactory):

    def __init__(self, other: TrackStatisticsExporterFactory) -> None:
        self.other = other
        self._cache: dict[tuple[Path, str], TrackStatisticsExporter] = dict()

    def get_supported_formats(self) -> Iterable[ExportFormat]:
        return self.other.get_supported_formats()

    def create(
        self, specification: TrackStatisticsExportSpecification
    ) -> TrackStatisticsExporter:
        export_mode = specification.export_mode

        key = (specification.save_path, specification.format)
        key_exists = key in self._cache.keys()

        exporter: TrackStatisticsExporter
        if export_mode.is_first_write():
            if key_exists:
                raise CacheTrackStatisticsException(
                    "TrackStatisticsExporter already exists for format+file"
                    + " upon first write!"
                    + " Maybe previous export was not finished or cache was not"
                    + "cleared properly.",
                    specification.save_path,
                    specification.format,
                    export_mode,
                )

            exporter = self.other.create(specification)
            self._cache[key] = exporter

        else:
            if not key_exists:
                raise CacheTrackStatisticsException(
                    "TrackStatisticsExporter missing in cache for format+file"
                    + " upon subsequent write!"
                    + "Maybe the cache was cleared too early.",
                    specification.save_path,
                    specification.format,
                    export_mode,
                )
            exporter = self._cache[key]

        if export_mode.is_final_write():
            del self._cache[key]

        return exporter
