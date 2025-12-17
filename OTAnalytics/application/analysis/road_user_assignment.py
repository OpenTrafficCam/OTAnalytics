import itertools
from abc import ABC, abstractmethod
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Iterable

from OTAnalytics.application.logger import logger as logging
from OTAnalytics.domain.event import Event
from OTAnalytics.domain.flow import Flow, FlowId
from OTAnalytics.domain.observer import OBSERVER, Subject
from OTAnalytics.domain.track_dataset.track_dataset import TrackIdSet, TrackIdSetFactory

logger = logging()


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
        track_id_set_factory: TrackIdSetFactory,
        subject: Subject[RoadUserAssignmentRepositoryEvent] = Subject[
            RoadUserAssignmentRepositoryEvent
        ](),
    ):
        self._track_id_set_factory = track_id_set_factory
        self._subject = subject
        self._assignments: dict[str, dict[FlowId, RoadUserAssignment]] = defaultdict(
            dict
        )
        self._observed_flows: Counter[FlowId] = Counter()

    def register_observer(
        self, observer: OBSERVER[RoadUserAssignmentRepositoryEvent]
    ) -> None:
        """
        Register an observer to be notified about changes in the repository.

        Args:
            observer: The observer to register.
        """
        self._subject.register(observer)

    def add(self, assignment: RoadUserAssignment) -> None:
        """
        Add a single road user assignment to the repository and notify observers.

        Args:
            road_user_assignment: The road user assignment to be added.
        """
        self.__do_add(assignment)
        self._subject.notify(
            RoadUserAssignmentRepositoryEvent.create_added([assignment])
        )

    def add_all(self, assignments: Iterable[RoadUserAssignment]) -> None:
        """
        Add multiple road user assignments to the repository and notify observers.

        Args:
            assignments: The road user assignments to be added.
        """
        for assignment in assignments:
            self.__do_add(assignment)
        self._subject.notify(
            RoadUserAssignmentRepositoryEvent.create_added(assignments)
        )

    def __do_add(self, assignment: RoadUserAssignment) -> None:
        flow = assignment.assignment.id
        self._assignments[assignment.road_user][flow] = assignment
        self._observed_flows[flow] += 1

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

    def get_all(self) -> "RoadUserAssignments":
        """
        Get all road user assignments as a RoadUserAssignments object.

        Returns:
            A RoadUserAssignments object containing all assignments in the repository.
        """
        return RoadUserAssignments(self.get_all_as_list(), self._track_id_set_factory)

    def get_all_as_list(
        self,
    ) -> list[RoadUserAssignment]:
        """
        Get all road user assignments as a list.

        Returns:
            A list of all RoadUserAssignment objects in the repository.
        """
        return list(
            itertools.chain.from_iterable(
                track.values() for track in self._assignments.values()
            )
        )

    def clear(self) -> None:
        """
        Remove all road user assignments from the repository and notify observers.
        """
        removed = frozenset(self.get_all_as_list())
        self._assignments.clear()
        self._observed_flows.clear()
        self._subject.notify(RoadUserAssignmentRepositoryEvent.create_removed(removed))

    def remove_assignments_of_event(self, event: Event) -> None:
        user_assignments = self._assignments[event.road_user_id]
        removed = []
        flows_to_remove = []
        for flow, assignment in user_assignments.items():
            events = assignment.events
            if event == events.start or event == events.end:
                flows_to_remove.append(flow)
                self._observed_flows[flow] -= 1
                removed.append(assignment)

        for flow in flows_to_remove:
            del user_assignments[flow]

        if not user_assignments:
            del self._assignments[event.road_user_id]

        for flow in list(self._observed_flows):
            count = self._observed_flows[flow]
            if count <= 0:
                if count < 0:
                    logger.warn(
                        "Tracking count of assignments by flow"
                        + f"turned negative while removing {event}"
                    )
                del self._observed_flows[flow]

        self._subject.notify(RoadUserAssignmentRepositoryEvent.create_removed(removed))

    def remove_assignments_of_flow(self, flow: FlowId) -> None:
        removed = [
            user.pop(flow) for user in self._assignments.values() if flow in user
        ]

        del self._observed_flows[flow]
        self._subject.notify(RoadUserAssignmentRepositoryEvent.create_removed(removed))

    def is_empty(self) -> bool:
        """
        Check whether the repository is empty.

        Returns:
            True if the repository contains no assignments, False otherwise.
        """
        return not self._assignments

    def get_observed_flows(self) -> set[FlowId]:
        return set(self._observed_flows)


class RoadUserAssignments:
    """
    Represents a group of RoadUserAssignment objects.
    """

    @property
    def road_user_ids(self) -> TrackIdSet:
        """Returns a sorted list of all road user ids within this group of assignments.

        Returns:
            list[str]: the road user ids.
        """
        return self._track_id_set_factory.create(
            {assignment.road_user for assignment in self._assignments}
        )

    def __init__(
        self,
        assignments: list[RoadUserAssignment],
        track_id_set_factory: TrackIdSetFactory,
    ) -> None:
        self._assignments = assignments.copy()
        self._track_id_set_factory = track_id_set_factory

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
