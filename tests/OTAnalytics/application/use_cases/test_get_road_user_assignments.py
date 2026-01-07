from dataclasses import dataclass
from unittest.mock import Mock, call

from OTAnalytics.application.analysis.road_user_assignment import (
    RoadUserAssignmentRepository,
)
from OTAnalytics.application.use_cases.assignment_repository import (
    GetRoadUserAssignments,
)
from OTAnalytics.application.use_cases.create_events import CreateEvents
from OTAnalytics.domain.track_dataset.track_dataset import TrackIdSetFactory
from OTAnalytics.domain.types import EventType


class TestGetRoadUserAssignments:
    def test_get(self) -> None:
        given = setup()
        target = create_target(given)

        actual = target.get_as_list()

        assert actual == given.assignments_as_list
        args = call(event_types=[EventType.SECTION_ENTER])
        given.event_repository.get.assert_has_calls([args])
        given.event_repository.get_all.assert_not_called()
        given.flow_repository.get_all.assert_called_once()
        given.road_user_assigner.assign.assert_called_once_with(
            given.events, given.flows
        )
        given.create_events.assert_called_once()
        given.assignments.as_list.assert_called_once()

    def test_no_recursion_when_get_called_during_creation(self) -> None:
        """
        Fix bug OP#8949
        Test that recursive calls to get_as_list during assignment creation
        don't cause infinite recursion.
        """
        given = setup()
        target = create_target(given)

        call_count = 0

        def mock_create_events_side_effect() -> None:
            nonlocal call_count
            call_count += 1
            result = target.get_as_list()
            assert result == []

        given.create_events.side_effect = mock_create_events_side_effect

        actual = target.get_as_list()

        assert actual == given.assignments_as_list
        assert call_count == 1
        given.road_user_assigner.assign.assert_called_once_with(
            given.events, given.flows
        )
        given.create_events.assert_called_once()


@dataclass
class Given:
    events: list[Mock]
    flows: list[Mock]
    assignments: Mock
    assignments_as_list: list[Mock]
    flow_repository: Mock
    event_repository: Mock
    road_user_assigner: Mock
    create_events: Mock
    assignment_repository: RoadUserAssignmentRepository
    create_assignments: Mock


def setup() -> Given:
    events = [Mock(), Mock()]
    flows = [Mock(), Mock()]
    assignments_as_list = [Mock(), Mock()]

    flow_repository = Mock()
    flow_repository.get_all.return_value = flows

    event_repository = Mock()
    event_repository.get_all.return_value = events
    event_repository.get.return_value = events

    assignments = Mock()
    assignments.as_list.return_value = assignments_as_list

    road_user_assigner = Mock()
    road_user_assigner.assign.return_value = assignments

    create_events = Mock(spec=CreateEvents)

    mock_factory = Mock(spec=TrackIdSetFactory)
    assignment_repository = RoadUserAssignmentRepository(mock_factory)

    create_assignments = Mock()

    return Given(
        events=events,
        flows=flows,
        assignments=assignments,
        assignments_as_list=assignments_as_list,
        flow_repository=flow_repository,
        event_repository=event_repository,
        road_user_assigner=road_user_assigner,
        create_events=create_events,
        assignment_repository=assignment_repository,
        create_assignments=create_assignments,
    )


def create_target(given: Given) -> GetRoadUserAssignments:
    return GetRoadUserAssignments(
        given.assignment_repository, given.create_assignments, True
    )
