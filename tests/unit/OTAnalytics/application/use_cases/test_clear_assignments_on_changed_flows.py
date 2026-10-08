from unittest.mock import Mock

from OTAnalytics.application.analysis.road_user_assignment import (
    RoadUserAssignmentRepository,
)
from OTAnalytics.application.use_cases.assignment_repository import (
    ClearAssignmentsOnChangedFlows,
)
from OTAnalytics.domain.flow import FlowId


class TestClearAssignmentsOnChangedFlows:
    def test_clear_on_changed_flow(self) -> None:
        assignment_repository = Mock(spec=RoadUserAssignmentRepository)
        target = ClearAssignmentsOnChangedFlows(assignment_repository)

        target.notify_flows([FlowId("1")])

        assignment_repository.clear.assert_called_once()

    def test_clear_on_added_flows(self) -> None:
        assignment_repository = Mock(spec=RoadUserAssignmentRepository)
        target = ClearAssignmentsOnChangedFlows(assignment_repository)

        target.notify_flows([FlowId("1"), FlowId("2")])

        assignment_repository.clear.assert_called_once()

    def test_clear_on_removed_flows(self) -> None:
        assignment_repository = Mock(spec=RoadUserAssignmentRepository)
        target = ClearAssignmentsOnChangedFlows(assignment_repository)

        target.notify_flows([])

        assignment_repository.clear.assert_called_once()
