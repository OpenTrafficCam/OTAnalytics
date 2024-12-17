from unittest.mock import Mock

import pytest

from OTAnalytics.application.analysis.traffic_counting import RoadUserAssignment
from OTAnalytics.application.use_cases.flow_statistics import (
    NumberOfTracksAssignedToEachFlow,
)
from OTAnalytics.domain.flow import Flow, FlowId


def create_flow(flow_id: FlowId) -> Flow:
    flow = Mock()
    flow.id = flow_id
    return flow


def create_assignment(road_user: str, assignment: Flow) -> RoadUserAssignment:
    return RoadUserAssignment(
        road_user=road_user,
        road_user_type=road_user,
        assignment=assignment,
        events=Mock(),
    )


FIRST_FLOW = create_flow(FlowId("first flow"))
SECOND_FLOW = create_flow(FlowId("second flow"))
FLOW_WITH_NO_ASSIGNMENTS = FlowId("flow with no assignments")

FIRST_ASSIGNMENT = create_assignment("road-user-1", FIRST_FLOW)
SECOND_ASSIGNMENT = create_assignment("road-user-2", SECOND_FLOW)
THIRD_ASSIGNMENT = create_assignment("road-user-3", FIRST_FLOW)
FOURTH_ASSIGNMENT = create_assignment("road-user-3", FIRST_FLOW)


@pytest.fixture
def get_road_user_assignments() -> Mock:
    assignments = [
        FIRST_ASSIGNMENT,
        SECOND_ASSIGNMENT,
        THIRD_ASSIGNMENT,
        FOURTH_ASSIGNMENT,
    ]
    get_assignments = Mock()
    get_assignments.get.return_value = assignments
    return get_assignments


@pytest.fixture
def flow_repository() -> Mock:
    repository = Mock()
    repository.get_all.return_value = [
        FIRST_FLOW,
        SECOND_FLOW,
        FLOW_WITH_NO_ASSIGNMENTS,
    ]
    return repository


class TestNumberOfTracksAssignedToEachFlow:
    def test_get(self, get_road_user_assignments: Mock, flow_repository: Mock) -> None:
        number_of_tracks_assigned_to_each_flow = NumberOfTracksAssignedToEachFlow(
            get_road_user_assignments, flow_repository
        )
        actual = number_of_tracks_assigned_to_each_flow.get()
        assert actual == {
            FIRST_FLOW.id: 3,
            SECOND_FLOW.id: 1,
            FLOW_WITH_NO_ASSIGNMENTS.id: 0,
        }
        get_road_user_assignments.get.assert_called_once()
        flow_repository.get_all.assert_called_once()
