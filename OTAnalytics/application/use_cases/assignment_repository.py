from OTAnalytics.application.analysis.road_user_assignment import (
    RoadUserAssignment,
    RoadUserAssignmentRepository,
    RoadUserAssignmentRepositoryEvent,
    RoadUserAssignments,
)
from OTAnalytics.application.use_cases.create_road_user_assignments import (
    CreateRoadUserAssignments,
)
from OTAnalytics.domain.event import EventRepository, EventRepositoryEvent
from OTAnalytics.domain.flow import FlowId, FlowListObserver


class GetRoadUserAssignments:
    """Provide the road user assignments, creating them when there are none.

    Creating assignments may find none, e.g. if no track crosses the sections of a
    flow. The empty result is kept until the repository changes. Otherwise every
    read would create the assignments again, and each creation notifies the
    observers of events, which read the assignments again.
    """

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
        self._is_created = False
        assignment_repository.register_observer(self._on_repository_changed)

    def _on_repository_changed(self, _: RoadUserAssignmentRepositoryEvent) -> None:
        """Changes by others, e.g. clearing outdated assignments, require creating
        the assignments again."""
        if not self._is_creating:
            self._is_created = False

    def get_as_list(self) -> list[RoadUserAssignment]:
        self.__check_update()
        return self._assignment_repository.get_all_as_list()

    def get(self) -> RoadUserAssignments:
        self.__check_update()
        return self._assignment_repository.get_all()

    def __check_update(self) -> None:
        if (
            not self._is_creating
            and not self._is_created
            and self._enable_assignment_creation
            and self._assignment_repository.is_empty()
        ):
            self._is_creating = True
            try:
                self._create_assignments()
                self._is_created = True
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


class ClearAssignmentsOnChangedFlows(FlowListObserver):
    """Clear all assignments.

    Args:
        assignment_repository (RoadUserAssignmentRepository): the repository
            holding the assignments to clear.
    """

    def __init__(self, assignment_repository: RoadUserAssignmentRepository) -> None:
        self._assignment_repository = assignment_repository

    def notify_flows(self, flows: list[FlowId]) -> None:
        """Clear all assignments after flows have been changed.

        Args:
            flows (list[FlowId]): the added or updated flows, empty if flows
                have been removed.
        """
        self._assignment_repository.clear()
