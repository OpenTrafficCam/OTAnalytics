from unittest.mock import Mock

import pytest

from OTAnalytics.application.analysis.road_user_assignment import (
    RoadUserAssignmentRepository,
)
from OTAnalytics.application.use_cases.create_events import CreateEvents
from OTAnalytics.application.use_cases.create_road_user_assignments import (
    CreateRoadUserAssignments,
)
from OTAnalytics.application.use_cases.get_road_user_assignments import (
    GetRoadUserAssignments,
)

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

        rua_repo = RoadUserAssignmentRepository()
        create_events = Mock(spec=CreateEvents)

        create_assignments = CreateRoadUserAssignments(
            flow_repository,
            event_repository,
            create_events,
            road_user_assigner,
            rua_repo,
        )

        get_assignments = GetRoadUserAssignments(rua_repo, create_assignments, True)
        actual = get_assignments.get_as_list()
        assert actual == assignments_as_list

        event_repository.get_all.assert_called_once()
        flow_repository.get_all.assert_called_once()
        road_user_assigner.assign.assert_called_once_with(events, flows)
        assignments.as_list.assert_called_once()
