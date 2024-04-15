from typing import Iterable

from pandas import DataFrame

from OTAnalytics.application.analysis.traffic_counting_specification import ExportFormat
from OTAnalytics.application.use_cases.road_user_assignment_export import (
    ExportSpecification,
    RoadUserAssignmentBuilder,
    RoadUserAssignmentExporter,
)
from OTAnalytics.application.use_cases.track_repository import GetAllTracks
from OTAnalytics.domain.section import SectionRepository


class RoadUserAssignmentCsvExporter(RoadUserAssignmentExporter):

    @property
    def format(self) -> ExportFormat:
        return ExportFormat("csv", ".csv")

    def _serialize(self, dtos: list[dict]) -> None:
        DataFrame(dtos).to_csv(self._outputfile, index=False)


class SimpleRoadUserAssignmentExporterFactory:
    def __init__(
        self,
        section_repository: SectionRepository,
        get_all_tracks: GetAllTracks,
    ) -> None:
        self._section_repository = section_repository
        self._get_all_tracks = get_all_tracks
        self._formats = {
            ExportFormat(
                "CSV", ".csv"
            ): lambda builder, output_file: RoadUserAssignmentCsvExporter(
                section_repository, get_all_tracks, builder, output_file
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

    def create(self, specification: ExportSpecification) -> RoadUserAssignmentExporter:
        """
        Create the exporter for the given road user assignment export specification.

        Args:
            specification (ExportSpecification): specification of the Exporter.

        Returns:
            RoadUserAssignmentExporter: Exporter to export road user assignments.
        """
        return self._factories[specification.format](
            RoadUserAssignmentBuilder(), specification.save_path
        )
