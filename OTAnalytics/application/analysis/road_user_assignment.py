from abc import ABC, abstractmethod
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
    """
    An event to notify observers about changes in the road user assignment repository.
    This event contains information about which assignments were added or removed.
    """

    added: frozenset[RoadUserAssignment]
    removed: frozenset[RoadUserAssignment]

    @staticmethod
    def create_added(
        assignments: Iterable[RoadUserAssignment],
    ) -> "RoadUserAssignmentRepositoryEvent":
        """
        Create an event for added road user assignments.

        Args:
            assignments: The road user assignments that were added.

        Returns:
            A new repository event with the added assignments.
        """
        return RoadUserAssignmentRepositoryEvent(frozenset(assignments), frozenset())

    @staticmethod
    def create_removed(
        assignments: Iterable[RoadUserAssignment],
    ) -> "RoadUserAssignmentRepositoryEvent":
        """
        Create an event for removed road user assignments.

        Args:
            assignments: The road user assignments that were removed.

        Returns:
            A new repository event with the removed assignments.
        """
        return RoadUserAssignmentRepositoryEvent(frozenset(), frozenset(assignments))


class RoadUserAssignmentRepository:
    """
    A repository to store and manage road user assignments.

    This class provides methods to add, retrieve, and clear road user assignments,
    as well as notify observers about changes to the repository.
    """

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
        """
        Register an observer to be notified about changes in the repository.

        Args:
            observer: The observer to register.
        """
        self._subject.register(observer)

    def add(self, road_user_assignment: RoadUserAssignment) -> None:
        """
        Add a single road user assignment to the repository and notify observers.

        Args:
            road_user_assignment: The road user assignment to be added.
        """
        self._assignments.append(road_user_assignment)
        self._subject.notify(
            RoadUserAssignmentRepositoryEvent.create_added([road_user_assignment])
        )

    def add_all(self, assignments: Iterable[RoadUserAssignment]) -> None:
        """
        Add multiple road user assignments to the repository and notify observers.

        Args:
            assignments: The road user assignments to be added.
        """
        self._assignments.extend(assignments)
        self._subject.notify(
            RoadUserAssignmentRepositoryEvent.create_added(assignments)
        )

    def add_road_user_assignments(
        self, road_user_assignments: "RoadUserAssignments"
    ) -> None:
        """
        Add all assignments from a RoadUserAssignments object to the repository
        and notify observers.


        Args:
            road_user_assignments:
                The RoadUserAssignments object containing assignments to be added.
        """
        self.add_all(road_user_assignments.as_list())

    def clear(self) -> None:
        """
        Remove all road user assignments from the repository and notify observers.
        """
        removed = frozenset(self._assignments)
        self._assignments = []
        self._subject.notify(RoadUserAssignmentRepositoryEvent.create_removed(removed))

    def get_all(self) -> "RoadUserAssignments":
        """
        Get all road user assignments as a RoadUserAssignments object.

        Returns:
            A RoadUserAssignments object containing all assignments in the repository.
        """
        return RoadUserAssignments(self._assignments)

    def get_all_as_list(self) -> list[RoadUserAssignment]:
        """
        Get all road user assignments as a list.

        Returns:
            A list of all RoadUserAssignment objects in the repository.
        """
        return list(self._assignments)

    def is_empty(self) -> bool:
        """
        Check whether the repository is empty.

        Returns:
            True if the repository contains no assignments, False otherwise.
        """
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
        """
        Initialize a new RoadUserAssignments object.

        Args:
            assignments: A list of RoadUserAssignment objects to store.
        """
        self._assignments = assignments.copy()

    def as_list(self) -> list[RoadUserAssignment]:
        """
        Retrieves a copy of the contained assignments.

        Returns:
            list[RoadUserAssignment]: a copy of the assignments
        """
        return self._assignments.copy()

    def __hash__(self) -> int:
        """
        Calculate the hash value for this object.

        Returns:
            The hash value based on the contained assignments.
        """
        return hash(str(self._assignments))

    def __eq__(self, other: object) -> bool:
        """
        Check if this object is equal to another object.

        Two RoadUserAssignments objects are considered equal if they contain
        the same assignments.

        Args:
            other: The object to compare with.

        Returns:
            True if the objects are equal, False otherwise.
        """
        if isinstance(other, RoadUserAssignments):
            return self._assignments == other._assignments
        return False

    def __repr__(self) -> str:
        """
        Get a string representation of this object.

        Returns:
            A string representation including the class name and the assignments.
        """
        return RoadUserAssignments.__name__ + repr(self._assignments)


class RoadUserAssigner(ABC):
    """
    Class to assign tracks to flows.
    """

    @abstractmethod
    def assign(self, events: Iterable[Event], flows: list[Flow]) -> RoadUserAssignments:
        """
        Assign each track to exactly one flow.

        Args:
            events (Iterable[Event]): events to be used during assignment
            flows (list[Flow]): flows to assign tracks to

        Returns:
            RoadUserAssignments: group of RoadUserAssignment objects
        """
        raise NotImplementedError
