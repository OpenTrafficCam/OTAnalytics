from dataclasses import dataclass
from unittest.mock import Mock, call

from OTAnalytics.application.analysis.road_user_assignment import (
    RoadUserAssignmentRepository,
)
from OTAnalytics.application.use_cases.assignment_repository import (
    GetRoadUserAssignments,
)
from OTAnalytics.application.use_cases.create_events import CreateEvents
from OTAnalytics.application.use_cases.create_road_user_assignments import (
    CreateRoadUserAssignments,
)
from OTAnalytics.application.use_cases.event_repository import GetAllEnterSectionEvents
from OTAnalytics.application.use_cases.flow_repository import GetAllFlows
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
        given.assignments.as_list.assert_called_once()


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
    )


def create_target(given: Given) -> GetRoadUserAssignments:
    create_assignments = CreateRoadUserAssignments(
        GetAllFlows(given.flow_repository),
        GetAllEnterSectionEvents(given.event_repository),
        given.create_events,
        given.road_user_assigner,
        given.assignment_repository,
    )

    return GetRoadUserAssignments(given.assignment_repository, create_assignments, True)
