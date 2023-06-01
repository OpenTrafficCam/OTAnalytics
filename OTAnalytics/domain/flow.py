from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable, Optional

from OTAnalytics.domain.section import SectionId

FLOWS: str = "flows"
FLOW_ID: str = "id"
FLOW_NAME: str = "name"
START: str = "start"
END: str = "end"
DISTANCE: str = "distance"


@dataclass(frozen=True)
class FlowId:
    id: str

    def serialize(self) -> str:
        return self.id


class Flow:
    """
    A `Flow` describes a segment of road that is defined by a start and end section as
    well as a distance between the start and end section.

    Args:
        id (FlowId): unique id of the flow
        start (Section): section to start the flow at
        end (Section): section to end the flow at
        distance (float): distance between start and end

    Raises:
        ValueError: if distance is negative
    """

    id: FlowId
    name: str
    start: SectionId
    end: SectionId
    distance: float

    def __init__(
        self,
        id: FlowId,
        name: str,
        start: SectionId,
        end: SectionId,
        distance: float,
    ) -> None:
        if distance < 0:
            raise ValueError(
                f"Distance must be equal or greater then 0, but is {distance}"
            )
        self.id: FlowId = id
        self.name = name
        self.start: SectionId = start
        self.end: SectionId = end
        self.distance: float = distance

    def to_dict(self) -> dict:
        return {
            FLOW_ID: self.id.serialize(),
            FLOW_NAME: self.name,
            START: self.start.serialize(),
            END: self.end.serialize(),
            DISTANCE: self.distance,
        }

    def is_using(self, section: SectionId) -> bool:
        return (self.start == section) or (self.end == section)


class FlowListObserver(ABC):
    """
    Interface to listen to changes to a list of flows.
    """

    @abstractmethod
    def notify_flows(self, flows: list[FlowId]) -> None:
        """
        Notifies that the given flows have been added or removed.

        Args:
            flows (list[FlowId]): list of added or removed flows
        """
        pass


class FlowListSubject:
    """
    Helper class to handle and notify observers
    """

    def __init__(self) -> None:
        self.observers: list[FlowListObserver] = []

    def register(self, observer: FlowListObserver) -> None:
        """
        Listen to events.

        Args:
            observer (FlowListObserver): listener to add
        """
        self.observers.append(observer)

    def notify(self, flows: list[FlowId]) -> None:
        """
        Notifies observers about the list of flows.

        Args:
            tracks (list[FlowId]): list of added flows
        """
        [observer.notify_flows(flows) for observer in self.observers]


class FlowRepository:
    def __init__(self) -> None:
        self._flows: dict[FlowId, Flow] = {}
        self._current_id = 0
        self._observers: FlowListSubject = FlowListSubject()

    def register_flows_observer(self, observer: FlowListObserver) -> None:
        self._observers.register(observer)

    def get_id(self) -> FlowId:
        """
        Get an id for a new flow
        """
        self._current_id += 1
        candidate = FlowId(str(self._current_id))
        return self.get_id() if candidate in self._flows.keys() else candidate

    def add(self, flow: Flow) -> None:
        self.__internal_add(flow)
        self._observers.notify([flow.id])

    def __internal_add(self, flow: Flow) -> None:
        self._flows[flow.id] = flow

    def is_flow_using_section(self, section: SectionId) -> bool:
        """
        Checks if the section id is used by flows.

        Args:
            section (SectionId): section to check

        Returns:
            bool: true if the section is used by at least one flow
        """
        return any(flow.is_using(section) for flow in self._flows.values())

    def flows_using_section(self, section: SectionId) -> list[FlowId]:
        """
        Returns a list of flows using the section as start or end.

        Args:
            section (SectionId): section to search flows for

        Returns:
            list[FlowId]: flows using the section
        """
        return list(
            {flow.id for flow in self._flows.values() if flow.is_using(section)}
        )

    def add_all(self, flows: Iterable[Flow]) -> None:
        for flow in flows:
            self.__internal_add(flow)
        self._observers.notify([flow.id for flow in flows])

    def remove(self, flow_id: FlowId) -> None:
        if flow_id in self._flows:
            del self._flows[flow_id]
            self._observers.notify([flow_id])

    def update(self, flow: Flow) -> None:
        self._flows[flow.id] = flow

    def get(self, flow_id: FlowId) -> Optional[Flow]:
        return self._flows.get(flow_id)

    def get_all(self) -> list[Flow]:
        return list(self._flows.values())
