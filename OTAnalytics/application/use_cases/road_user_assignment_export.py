from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable, Iterable, Protocol, Self

from OTAnalytics.application.analysis.traffic_counting import (
    RoadUserAssigner,
    RoadUserAssignment,
    RoadUserAssignments,
)
from OTAnalytics.application.analysis.traffic_counting_specification import ExportFormat
from OTAnalytics.application.export_formats import road_user_assignments as ras
from OTAnalytics.application.use_cases.create_events import CreateEvents
from OTAnalytics.application.use_cases.track_repository import GetAllTracks
from OTAnalytics.domain.event import EventRepository
from OTAnalytics.domain.flow import FlowRepository
from OTAnalytics.domain.section import Section, SectionId, SectionRepository

MaxConfidenceLookupTable = dict[str, float]
MaxConfidenceProvider = Callable[[list[str]], MaxConfidenceLookupTable]


class RoadUserAssignmentBuildError(Exception):
    pass


class RoadUserAssignmentBuilder:
    def __init__(self) -> None:
        self._start_section: Section | None = None
        self._end_section: Section | None = None
        self._max_confidence: float | None = None

    def add_start_section(self, start: Section) -> Self:
        self._start_section = start
        return self

    def add_end_section(self, end: Section) -> Self:
        self._end_section = end
        return self

    def add_max_confidence(self, max_confidence: float) -> Self:
        self._max_confidence = max_confidence
        return self

    def build(self, assignment: RoadUserAssignment) -> dict:
        result = self.__create(assignment)
        self.reset()
        return result

    def __create(self, assignment: RoadUserAssignment) -> dict:
        if self._start_section is None:
            raise RoadUserAssignmentBuildError("Start section not set")
        if self._end_section is None:
            raise RoadUserAssignmentBuildError("End section not set")
        if self._max_confidence is None:
            raise RoadUserAssignmentBuildError("Max confidence not set")
        assigned_flow = assignment.assignment
        start = assignment.events.start
        end = assignment.events.end
        return {
            ras.FLOW_ID: assigned_flow.id.id,
            ras.FLOW_NAME: assigned_flow.name,
            ras.ROAD_USER_ID: assignment.road_user,
            ras.MAX_CONFIDENCE: self._max_confidence,
            ras.START_OCCURRENCE: start.occurrence.strftime(ras.DATE_TIME_FORMAT),
            ras.START_OCCURRENCE_DATE: start.occurrence.strftime(ras.DATE_FORMAT),
            ras.START_OCCURRENCE_TIME: start.occurrence.strftime(ras.TIME_FORMAT),
            ras.END_OCCURRENCE: end.occurrence.strftime(ras.DATE_TIME_FORMAT),
            ras.END_OCCURRENCE_DATE: end.occurrence.strftime(ras.DATE_FORMAT),
            ras.END_OCCURRENCE_TIME: end.occurrence.strftime(ras.TIME_FORMAT),
            ras.START_FRAME: start.frame_number,
            ras.END_FRAME: end.frame_number,
            ras.START_VIDEO_NAME: start.video_name,
            ras.END_VIDEO_NAME: end.video_name,
            ras.START_SECTION_ID: self._start_section.id.id,
            ras.END_SECTION_ID: self._end_section.id.id,
            ras.START_SECTION_NAME: self._start_section.name,
            ras.END_SECTION_NAME: self._end_section.name,
            ras.START_EVENT_COORDINATE_X: start.event_coordinate.x,
            ras.START_EVENT_COORDINATE_Y: start.event_coordinate.y,
            ras.END_EVENT_COORDINATE_X: end.event_coordinate.x,
            ras.END_EVENT_COORDINATE_Y: end.event_coordinate.y,
            ras.START_DIRECTION_VECTOR_X: start.direction_vector.x1,
            ras.START_DIRECTION_VECTOR_Y: start.direction_vector.x2,
            ras.END_DIRECTION_VECTOR_X: end.direction_vector.x1,
            ras.END_DIRECTION_VECTOR_Y: end.direction_vector.x2,
            ras.HOSTNAME: start.hostname,
        }

    def reset(self) -> None:
        self._start_section = None
        self._end_section = None
        self._max_confidence = None


class RoadUserAssignmentExportError(Exception):
    pass


class RoadUserAssignmentExporter(ABC):
    @property
    @abstractmethod
    def format(self) -> ExportFormat:
        raise NotImplementedError

    def __init__(
        self,
        section_repository: SectionRepository,
        get_all_tracks: GetAllTracks,
        builder: RoadUserAssignmentBuilder,
        output_file: Path,
    ) -> None:
        self._section_repository = section_repository
        self._get_all_tracks = get_all_tracks
        self._builder = builder
        self._outputfile = output_file

    def export(self, assignments: RoadUserAssignments) -> None:
        dtos = self._convert(assignments)
        self._serialize(dtos)

    @abstractmethod
    def _serialize(self, dtos: list[dict]) -> None:
        """Hook for implementations to serialize in their respective save format.

        Args:
            dtos (list[dict]): the vehicle flow assignments as dtos.
        """
        raise NotImplementedError

    def _convert(self, assignments: RoadUserAssignments) -> list[dict]:
        vehicle_flow_assignments = []
        look_up_table = self._get_max_conf_lookup_table_for(assignments)
        for assignment in assignments.as_list():
            start_section = self._get_section_by_id(assignment.assignment.start)
            end_section = self._get_section_by_id(assignment.assignment.end)
            max_confidence = look_up_table[assignment.road_user]
            vehicle_flow_assignments.append(
                self._builder.add_start_section(start_section)
                .add_end_section(end_section)
                .add_max_confidence(max_confidence)
                .build(assignment)
            )
        return vehicle_flow_assignments

    def _get_max_conf_lookup_table_for(
        self, assignments: RoadUserAssignments
    ) -> MaxConfidenceLookupTable:
        return self._get_all_tracks.as_dataset().get_max_confidences_for(
            assignments.road_user_ids
        )

    def _get_section_by_id(self, section_id: SectionId) -> Section:
        result = self._section_repository.get(section_id)
        if not result:
            raise RoadUserAssignmentExportError(
                f"No section found with id '{section_id.id}'"
            )
        return result


class ExportSpecification(Protocol):
    save_path: Path
    format: str


class RoadUserAssignmentExporterFactory(Protocol):
    def get_supported_formats(self) -> Iterable[ExportFormat]:
        """
        Returns an iterable of the supported export formats.

        Returns:
            Iterable[ExportFormat]: supported export formats.
        """
        ...

    def create(self, specification: ExportSpecification) -> RoadUserAssignmentExporter:
        """
        Create the exporter for the given road user assignment export specification.

        Args:
            specification (ExportSpecification): specification of the Exporter.

        Returns:
            RoadUserAssignmentExporter: Exporter to export road user assignments.
        """
        ...


class ExportRoadUserAssignments:
    """Use case to export_formats vehicle flow assignments."""

    def __init__(
        self,
        event_repository: EventRepository,
        flow_repository: FlowRepository,
        create_events: CreateEvents,
        assigner: RoadUserAssigner,
        exporter_factory: RoadUserAssignmentExporterFactory,
    ) -> None:
        self._event_repository = event_repository
        self._flow_repository = flow_repository
        self._create_events = create_events
        self._assigner = assigner
        self._exporter_factory = exporter_factory

    def export(self, specification: ExportSpecification) -> None:
        if self._event_repository.is_empty():
            self._create_events()
        events = self._event_repository.get_all()
        flows = self._flow_repository.get_all()
        road_user_assignments = self._assigner.assign(events, flows)
        exporter = self._exporter_factory.create(specification)
        exporter.export(road_user_assignments)
