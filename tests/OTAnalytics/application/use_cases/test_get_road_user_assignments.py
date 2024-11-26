from unittest.mock import Mock

import pytest

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
        get_assignments = GetRoadUserAssignments(
            flow_repository, event_repository, road_user_assigner
        )
        actual = get_assignments.get()
        assert actual == assignments_as_list
        event_repository.get_all.assert_called_once()
        flow_repository.get_all.assert_called_once()
        road_user_assigner.assign.assert_called_once_with(events, flows)
        assignments.as_list.assert_called_once()
