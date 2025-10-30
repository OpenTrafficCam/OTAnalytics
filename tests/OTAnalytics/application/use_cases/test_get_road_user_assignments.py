from unittest.mock import Mock, call

import pytest

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

events = [Mock(), Mock()]
flows = [Mock(), Mock()]
assignments_as_list = [Mock(), Mock()]


@pytest.fixture
def flow_repository() -> Mock:
    repository = Mock()
    repository.get_all.return_value = flows
    return repository


@pytest.fixture
def event_repository() -> Mock:
    repository = Mock()
    repository.get_all.return_value = events
    repository.get.return_value = events
    return repository


@pytest.fixture
def assignments() -> Mock:
    assignments = Mock()
    assignments.as_list.return_value = assignments_as_list
    return assignments


@pytest.fixture
def road_user_assigner(assignments: Mock) -> Mock:
    assigner = Mock()
    assigner.assign.return_value = assignments
    return assigner


class TestGetRoadUserAssignments:
    def test_get(
        self,
        flow_repository: Mock,
        event_repository: Mock,
        road_user_assigner: Mock,
        assignments: Mock,
    ) -> None:
        mock_factory = Mock(spec=TrackIdSetFactory)
        rua_repo = RoadUserAssignmentRepository(mock_factory)
        create_events = Mock(spec=CreateEvents)

        create_assignments = CreateRoadUserAssignments(
            GetAllFlows(flow_repository),
            GetAllEnterSectionEvents(event_repository),
            create_events,
            road_user_assigner,
            rua_repo,
        )

        get_assignments = GetRoadUserAssignments(rua_repo, create_assignments, True)
        actual = get_assignments.get_as_list()
        assert actual == assignments_as_list

        args = call(event_types=[EventType.SECTION_ENTER])
        event_repository.get.assert_has_calls([args])
        event_repository.get_all.assert_not_called()

        flow_repository.get_all.assert_called_once()
        road_user_assigner.assign.assert_called_once_with(events, flows)
        assignments.as_list.assert_called_once()
