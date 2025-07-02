from dataclasses import dataclass
from typing import Iterable

from OTAnalytics.domain.event import Event
from OTAnalytics.domain.flow import Flow
from OTAnalytics.domain.observer import OBSERVER, Subject


@dataclass(frozen=True)
class EventPair:
    """
    Pair of events of one track to find a matching flow.
    """

    start: Event
    end: Event


@dataclass(frozen=True)
class RoadUserAssignment:
    """
    Assignment of a road user to a flow.
    """

    road_user: str
    road_user_type: str
    assignment: Flow
    events: EventPair


@dataclass(frozen=True)
class RoadUserAssignmentRepositoryEvent:
    added: Iterable[RoadUserAssignment]


class RoadUserAssignmentRepository:
    """The repository to store assignments."""

    def __init__(
        self,
        subject: Subject[RoadUserAssignmentRepositoryEvent] = Subject[
            RoadUserAssignmentRepositoryEvent
        ](),
    ):
        self._subject = subject
        self._assignments: list[RoadUserAssignment] = []

    def register_observer(
        self, observer: OBSERVER[RoadUserAssignmentRepositoryEvent]
    ) -> None:
        self._subject.register(observer)

    def add(self, road_user_assignment: RoadUserAssignment) -> None:
        self._assignments.append(road_user_assignment)
        self._subject.notify(
            RoadUserAssignmentRepositoryEvent(added=[road_user_assignment])
        )

    def add_all(self, assignments: Iterable[RoadUserAssignment]) -> None:
        self._assignments.extend(assignments)
        self._subject.notify(RoadUserAssignmentRepositoryEvent(added=list(assignments)))

    def add_road_user_assignments(
        self, road_user_assignments: "RoadUserAssignments"
    ) -> None:
        self.add_all(road_user_assignments.as_list())

    def clear(self) -> None:
        self._assignments = []

    def get_all(self) -> "RoadUserAssignments":
        return RoadUserAssignments(self._assignments)

    def get_all_as_list(self) -> list[RoadUserAssignment]:
        return list(self._assignments)

    def is_empty(self) -> bool:
        """Whether repository is empty."""
        return not self._assignments


class RoadUserAssignments:
    """
    Represents a group of RoadUserAssignment objects.
    """

    @property
    def road_user_ids(self) -> list[str]:
        """Returns a sorted list of all road user ids within this group of assignments.

        Returns:
            list[str]: the road user ids.
        """
        return sorted([assignment.road_user for assignment in self._assignments])

    def __init__(self, assignments: list[RoadUserAssignment]) -> None:
        self._assignments = assignments.copy()

    def as_list(self) -> list[RoadUserAssignment]:
        """
        Retrieves a copy of the contained assignments.

        Returns:
            list[RoadUserAssignment]: a copy of the assignments
        """
        return self._assignments.copy()

    def __hash__(self) -> int:
        return hash(self._assignments)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, RoadUserAssignments):
            return self._assignments == other._assignments
        return False

    def __repr__(self) -> str:
        return RoadUserAssignments.__name__ + repr(self._assignments)
