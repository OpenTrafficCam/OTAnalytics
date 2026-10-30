from dataclasses import dataclass
from unittest.mock import Mock

from OTAnalytics.application.analysis.road_user_assignment import (
    EventPair,
    FlowMetrics,
    RoadUserAssignment,
    RoadUserAssignmentRepository,
)
from OTAnalytics.domain.flow import Flow, FlowId
from OTAnalytics.domain.section import SectionId
from tests.utils.builders.road_user_assignment import create_assignment


class TestRoadUserAssignmentRepository:

    def test_remove_assignment_of_event(self) -> None:
        """
        Fix bug OP#8926 - dictionary changed size during iteration
        """
        given = setup()

        given.repository.remove_assignments_of_event(given.start_event)

        assert given.repository.get_all().as_list() == []


class TestFlowMetrics:
    def test_flow_metrics_returns_speed_from_distance_and_travel_time(self) -> None:
        assignment = create_assignment(distance=100.0, start_s=0.0, end_s=10.0)

        assert assignment.flow_metrics() == FlowMetrics(100.0, 10.0, 10.0)
        assert assignment.flow_metrics().avg_speed_kmh == 36.0

    def test_flow_metrics_without_distance_has_no_speed(self) -> None:
        metrics = create_assignment(
            distance=None, start_s=0.0, end_s=10.0
        ).flow_metrics()

        assert metrics.avg_speed_mps is None
        assert metrics.avg_speed_kmh is None

    def test_flow_metrics_with_zero_travel_time_has_no_speed(self) -> None:
        metrics = create_assignment(
            distance=10.0, start_s=5.0, end_s=5.0
        ).flow_metrics()

        assert metrics.travel_time_s == 0.0
        assert metrics.avg_speed_mps is None

    def test_flow_metrics_with_zero_distance_has_zero_speed(self) -> None:
        metrics = create_assignment(distance=0.0, start_s=0.0, end_s=4.0).flow_metrics()

        assert metrics.avg_speed_mps == 0.0
        assert metrics.avg_speed_kmh == 0.0


@dataclass
class Given:
    start_event: Mock
    end_event: Mock
    assignment: RoadUserAssignment
    repository: RoadUserAssignmentRepository


def setup() -> Given:
    start_event = Mock()
    start_event.road_user_id = "road_user_1"
    end_event = Mock()
    end_event.road_user_id = "road_user_1"
    assignment = RoadUserAssignment(
        road_user="road_user_1",
        road_user_type="car",
        assignment=Flow(
            id=FlowId("flow_1"),
            name="Flow 1",
            start=SectionId("0"),
            end=SectionId("1"),
        ),
        events=EventPair(start=start_event, end=end_event),
    )
    repository = RoadUserAssignmentRepository(track_id_set_factory=Mock())
    repository.add(assignment)
    return Given(
        start_event=start_event,
        end_event=end_event,
        assignment=assignment,
        repository=repository,
    )
