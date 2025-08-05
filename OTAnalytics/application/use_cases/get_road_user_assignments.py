from OTAnalytics.application.analysis.road_user_assignment import (
    RoadUserAssignment,
    RoadUserAssignmentRepository,
    RoadUserAssignments,
)
from OTAnalytics.application.use_cases.create_road_user_assignments import (
    CreateRoadUserAssignments,
)


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

    def get_as_list(self) -> list[RoadUserAssignment]:
        self.__check_update()
        return self._assignment_repository.get_all_as_list()

    def get(self) -> RoadUserAssignments:
        self.__check_update()
        return self._assignment_repository.get_all()

    def __check_update(self) -> None:
        if self._assignment_repository.is_empty() and self._enable_assignment_creation:
            self._create_assignments()
