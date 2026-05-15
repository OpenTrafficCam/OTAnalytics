from datetime import datetime, timedelta, timezone
from unittest import mock
from unittest.mock import Mock, call

import pytest

from OTAnalytics.application.analysis.road_user_assignment import (
    EventPair,
    RoadUserAssigner,
    RoadUserAssignment,
    RoadUserAssignmentRepository,
    RoadUserAssignments,
)
from OTAnalytics.application.export_formats import road_user_assignments as ras
from OTAnalytics.application.export_formats.export_mode import OVERWRITE
from OTAnalytics.application.use_cases.assignment_repository import (
    GetRoadUserAssignments,
)
from OTAnalytics.application.use_cases.create_road_user_assignments import (
    CreateRoadUserAssignments,
)
from OTAnalytics.application.use_cases.event_repository import GetAllEnterSectionEvents
from OTAnalytics.application.use_cases.flow_repository import GetAllFlows
from OTAnalytics.application.use_cases.road_user_assignment_export import (
    ExportRoadUserAssignments,
    RoadUserAssignmentBuilder,
    RoadUserAssignmentBuildError,
    RoadUserAssignmentExporter,
    RoadUserAssignmentExporterFactory,
    compute_road_user_assignment_flow_metrics,
)
from OTAnalytics.domain.flow import Flow, FlowId
from OTAnalytics.domain.section import Section
from OTAnalytics.domain.track_dataset.track_dataset import TrackIdSetFactory
from OTAnalytics.domain.types import EventType
from tests.utils.builders.event_builder import EventBuilder
from tests.utils.builders.road_user_assignment import create_road_user_assignment


@pytest.fixture
def _builder() -> RoadUserAssignmentBuilder:
    return RoadUserAssignmentBuilder()


class TestRoadUserAssignmentBuilder:
    def test_add_start_section(self, _builder: RoadUserAssignmentBuilder) -> None:
        section = Mock()
        _builder.add_start_section(section)
        assert _builder._start_section == section

    def test_add_end_section(self, _builder: RoadUserAssignmentBuilder) -> None:
        section = Mock()
        _builder.add_end_section(section)
        assert _builder._end_section == section

    def test_add_max_confidence(self, _builder: RoadUserAssignmentBuilder) -> None:
        confidence = 0.8
        _builder.add_max_confidence(confidence)
        assert _builder._max_confidence == confidence

    def test_build(
        self,
        _builder: RoadUserAssignmentBuilder,
        first_line_section: Section,
        second_line_section: Section,
        first_road_user_assignment: RoadUserAssignment,
    ) -> None:
        _builder.add_start_section(first_line_section)
        _builder.add_end_section(second_line_section)
        _builder.add_max_confidence(0.9)
        result = _builder.build(first_road_user_assignment)
        assert result == create_road_user_assignment(
            first_road_user_assignment, first_line_section, second_line_section
        )

    def test_build_with_start_section_missing(
        self, _builder: RoadUserAssignmentBuilder
    ) -> None:
        _builder.add_end_section(Mock())
        _builder.add_max_confidence(0.9)
        with pytest.raises(RoadUserAssignmentBuildError, match="Start section not set"):
            _builder.build(Mock())

    def test_build_with_end_section_missing(
        self, _builder: RoadUserAssignmentBuilder
    ) -> None:
        _builder.add_start_section(Mock())
        _builder.add_max_confidence(0.9)
        with pytest.raises(RoadUserAssignmentBuildError, match="End section not set"):
            _builder.build(Mock())

    def test_build_with_max_confidence_missing(
        self, _builder: RoadUserAssignmentBuilder
    ) -> None:
        _builder.add_start_section(Mock())
        _builder.add_end_section(Mock())
        with pytest.raises(
            RoadUserAssignmentBuildError, match="Max confidence not set"
        ):
            _builder.build(Mock())

    def test_build_avg_speed_when_flow_distance_and_positive_duration(
        self,
        _builder: RoadUserAssignmentBuilder,
        first_line_section: Section,
        second_line_section: Section,
    ) -> None:
        t0 = datetime(2020, 1, 1, tzinfo=timezone.utc)
        t1 = t0 + timedelta(seconds=10)
        start_event = EventBuilder(
            section_id=first_line_section.id.id,
            interpolated_occurrence=t0,
        ).build_section_event()
        end_event = EventBuilder(
            section_id=second_line_section.id.id,
            interpolated_occurrence=t1,
        ).build_section_event()
        flow = Flow(
            FlowId("f-speed"),
            "f-speed",
            first_line_section.id,
            second_line_section.id,
            distance=25.0,
        )
        assignment = RoadUserAssignment(
            "1", "car", flow, EventPair(start_event, end_event)
        )
        _builder.add_start_section(first_line_section)
        _builder.add_end_section(second_line_section)
        _builder.add_max_confidence(0.9)
        result = _builder.build(assignment)
        assert result[ras.FLOW_DISTANCE_M] == 25.0
        assert result[ras.TRAVEL_TIME_S] == 10.0
        assert result[ras.AVG_SPEED_MPS] == 2.5

    def test_build_no_avg_speed_when_zero_travel_time(
        self,
        _builder: RoadUserAssignmentBuilder,
        first_line_section: Section,
        second_line_section: Section,
    ) -> None:
        t0 = datetime(2020, 1, 1, tzinfo=timezone.utc)
        start_event = EventBuilder(
            section_id=first_line_section.id.id,
            interpolated_occurrence=t0,
        ).build_section_event()
        end_event = EventBuilder(
            section_id=second_line_section.id.id,
            interpolated_occurrence=t0,
        ).build_section_event()
        flow = Flow(
            FlowId("f-zero"),
            "f-zero",
            first_line_section.id,
            second_line_section.id,
            distance=10.0,
        )
        assignment = RoadUserAssignment(
            "1", "car", flow, EventPair(start_event, end_event)
        )
        _builder.add_start_section(first_line_section)
        _builder.add_end_section(second_line_section)
        _builder.add_max_confidence(0.9)
        result = _builder.build(assignment)
        assert result[ras.FLOW_DISTANCE_M] == 10.0
        assert result[ras.TRAVEL_TIME_S] == 0.0
        assert result[ras.AVG_SPEED_MPS] is None

    def test_build_avg_speed_zero_when_flow_distance_is_zero(
        self,
        _builder: RoadUserAssignmentBuilder,
        first_line_section: Section,
        second_line_section: Section,
    ) -> None:
        t0 = datetime(2020, 1, 1, tzinfo=timezone.utc)
        t1 = t0 + timedelta(seconds=4)
        start_event = EventBuilder(
            section_id=first_line_section.id.id,
            interpolated_occurrence=t0,
        ).build_section_event()
        end_event = EventBuilder(
            section_id=second_line_section.id.id,
            interpolated_occurrence=t1,
        ).build_section_event()
        flow = Flow(
            FlowId("f-zero-dist"),
            "f-zero-dist",
            first_line_section.id,
            second_line_section.id,
            distance=0.0,
        )
        assignment = RoadUserAssignment(
            "1", "car", flow, EventPair(start_event, end_event)
        )
        _builder.add_start_section(first_line_section)
        _builder.add_end_section(second_line_section)
        _builder.add_max_confidence(0.9)
        result = _builder.build(assignment)
        assert result[ras.FLOW_DISTANCE_M] == 0.0
        assert result[ras.TRAVEL_TIME_S] == 4.0
        assert result[ras.AVG_SPEED_MPS] == 0.0


class TestComputeRoadUserAssignmentFlowMetrics:
    def test_no_distance_leaves_speed_none(self) -> None:
        t0 = datetime(2020, 1, 1, tzinfo=timezone.utc)
        t1 = t0 + timedelta(seconds=2)
        d, dt, v = compute_road_user_assignment_flow_metrics(None, t0, t1)
        assert d is None
        assert dt == 2.0
        assert v is None

    def test_distance_and_positive_time_gives_speed(self) -> None:
        t0 = datetime(2020, 1, 1, tzinfo=timezone.utc)
        t1 = t0 + timedelta(seconds=4)
        d, dt, v = compute_road_user_assignment_flow_metrics(8.0, t0, t1)
        assert d == 8.0
        assert dt == 4.0
        assert v == 2.0

    def test_zero_distance_with_positive_time_gives_zero_speed(self) -> None:
        t0 = datetime(2020, 1, 1, tzinfo=timezone.utc)
        t1 = t0 + timedelta(seconds=2)
        d, dt, v = compute_road_user_assignment_flow_metrics(0.0, t0, t1)
        assert d == 0.0
        assert dt == 2.0
        assert v == 0.0


class TestExportRoadUserAssignments:
    def test_export(self) -> None:
        event_repository = Mock()
        flow_repository = Mock()
        create_events = Mock()
        road_user_assigner = Mock(spec=RoadUserAssigner)
        exporter_factory = Mock(spec=RoadUserAssignmentExporterFactory)

        events = Mock()
        event_repository.get.return_value = events

        flows = Mock()
        flow_repository.get_all.return_value = flows

        mock_factory = Mock(spec=TrackIdSetFactory)
        assignments = Mock(spec=RoadUserAssignments)
        assignment_list: list[RoadUserAssignment] = []
        assignments.as_list.return_value = assignment_list
        road_user_assigner.assign.return_value = assignments

        exporter = Mock(spec=RoadUserAssignmentExporter)
        exporter_factory.create.return_value = exporter

        rua_repo = RoadUserAssignmentRepository(mock_factory)

        with mock.patch.object(RoadUserAssignmentRepository, "get_all") as get_all_mock:
            get_all_mock.return_value = assignments

            create_assignments = CreateRoadUserAssignments(
                GetAllFlows(flow_repository),
                GetAllEnterSectionEvents(event_repository),
                create_events,
                road_user_assigner,
                rua_repo,
            )
            get_assignments = GetRoadUserAssignments(rua_repo, create_assignments)

            export_road_user_assignments = ExportRoadUserAssignments(
                get_assignments,
                exporter_factory,
            )
            specification = Mock()
            specification.save_path = Mock()
            specification.format = "csv"
            specification.mode = OVERWRITE

            export_road_user_assignments.export(specification)

        args = call(event_types=[EventType.SECTION_ENTER])
        event_repository.get.assert_has_calls([args])
        event_repository.get_all.assert_not_called()

        flow_repository.get_all.assert_called_once()
        road_user_assigner.assign.assert_called_once_with(events, flows)
        exporter_factory.create.assert_called_once_with(specification)
        exporter.export.assert_called_once_with(assignments, OVERWRITE)
