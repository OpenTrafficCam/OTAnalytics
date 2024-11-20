from collections import defaultdict

from OTAnalytics.application.use_cases.get_road_user_assignments import (
    GetRoadUserAssignments,
)
from OTAnalytics.domain.flow import FlowId, FlowRepository


class NumberOfTracksAssignedToEachFlow:
    def __init__(
        self, get_assignments: GetRoadUserAssignments, flow_repository: FlowRepository
    ) -> None:
        self._get_assignments = get_assignments
        self._flow_repository = flow_repository

    def get(self) -> dict[FlowId, int]:
        result = self._initialize_flow_track_counts()
        for road_user_assignment in self._get_assignments.get():
            flow_id = road_user_assignment.assignment.id
            result[flow_id] += 1
        return result

    def _initialize_flow_track_counts(self) -> dict[FlowId, int]:
        flows = defaultdict(lambda: 0)
        for flow in self._flow_repository.get_all():
            flows[flow.id] = 0
        return flows
