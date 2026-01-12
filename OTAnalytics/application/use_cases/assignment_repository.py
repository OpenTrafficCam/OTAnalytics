from OTAnalytics.application.analysis.road_user_assignment import (
    RoadUserAssignment,
    RoadUserAssignmentRepository,
    RoadUserAssignments,
)
from OTAnalytics.application.use_cases.create_road_user_assignments import (
    CreateRoadUserAssignments,
)
from OTAnalytics.application.use_cases.flow_repository import GetAllFlows
from OTAnalytics.domain.event import EventRepository, EventRepositoryEvent
from OTAnalytics.domain.flow import FlowId, FlowListObserver


class GetRoadUserAssignments:
    def __init__(
        self,
        assignment_repository: RoadUserAssignmentRepository,
        create_assignments: CreateRoadUserAssignments,
        enable_assignment_creation: bool = True,
    ) -> None:
        self._assignment_repository = assignment_repository
        self._create_assignments = create_assignments
        self._enable_assignment_creation = enable_assignment_creation
        self._is_creating = False

    def get_as_list(self) -> list[RoadUserAssignment]:
        self.__check_update()
        return self._assignment_repository.get_all_as_list()

    def get(self) -> RoadUserAssignments:
        self.__check_update()
        return self._assignment_repository.get_all()

    def __check_update(self) -> None:
        if (
            not self._is_creating
            and self._enable_assignment_creation
            and self._assignment_repository.is_empty()
        ):
            self._is_creating = True
            try:
                self._create_assignments()
            finally:
                self._is_creating = False


class ClearAllAssignments:
    def __init__(self, assignment_repository: RoadUserAssignmentRepository) -> None:
        self._assignment_repository = assignment_repository

    def __call__(self) -> None:
        self._assignment_repository.clear()


class RemoveAssignmentsOfRemovedEvents:
    def __init__(
        self,
        assignment_repository: RoadUserAssignmentRepository,
        event_repository: EventRepository,
    ) -> None:
        self._assignment_repository = assignment_repository
        self._event_repository = event_repository

    def __call__(self, repo_event: EventRepositoryEvent) -> None:
        if self._event_repository.is_empty():
            self._assignment_repository.clear()
            return

        for event in repo_event.removed:
            self._assignment_repository.remove_assignments_of_event(event)


class RemoveAssignmentsOfChangedFlow:  # is a FlowChangedObserver
    def __init__(self, assignment_repository: RoadUserAssignmentRepository) -> None:
        self._assignment_repository = assignment_repository

    def __call__(self, flow: FlowId) -> None:
        self._assignment_repository.remove_assignments_of_flow(flow)


class RemoveAssignmentsOfRemovedFlows(FlowListObserver):
    def __init__(
        self,
        assignment_repository: RoadUserAssignmentRepository,
        get_all_flows: GetAllFlows,
    ) -> None:
        self._assignment_repository = assignment_repository
        self._get_all_flows = get_all_flows

    def notify_flows(self, flows: list[FlowId]) -> None:
        # TODO notification [] means flow is removed or all are removed!
        # FlowRepositoryEvent would be helpful here
        if not flows:
            observed_flows = self._assignment_repository.get_observed_flows()
            current_flows = [flow.id for flow in self._get_all_flows.get()]

            if len(current_flows) == 0:
                self._assignment_repository.clear()
                return

            gen = (flow for flow in observed_flows if flow not in current_flows)
            for flow in gen:
                self._assignment_repository.remove_assignments_of_flow(flow)
