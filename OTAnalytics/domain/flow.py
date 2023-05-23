from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable, Optional

from OTAnalytics.domain.section import Section

FLOWS: str = "flows"
FLOW_ID: str = "id"
START: str = "start"
END: str = "end"
DISTANCE: str = "distance"


@dataclass(frozen=True)
class FlowId:
    id: str

    def serialize(self) -> str:
        return self.id


@dataclass
class Flow:
    id: FlowId
    start: Section
    end: Section
    distance: float

    def __eq__(self, __value: object) -> bool:
        return self.id == __value.id if isinstance(__value, Flow) else False

    def to_dict(self) -> dict:
        return {
            FLOW_ID: self.id.serialize(),
            START: self.start.id.serialize(),
            END: self.end.id.serialize(),
            DISTANCE: self.distance,
        }


class FlowListObserver(ABC):
    """
    Interface to listen to changes to a list of flows.
    """

    @abstractmethod
    def notify_flows(self, flows: list[FlowId]) -> None:
        """
        Notifies that the given flows have been added.

        Args:
            flows (list[FlowId]): list of added flows
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
        self._observers: FlowListSubject = FlowListSubject()

    def register_flows_observer(self, observer: FlowListObserver) -> None:
        self._observers.register(observer)

    def add(self, flow: Flow) -> None:
        self.__internal_add(flow)
        self._observers.notify([flow.id])

    def __internal_add(self, flow: Flow) -> None:
        self._flows[flow.id] = flow

    def add_all(self, flows: Iterable[Flow]) -> None:
        for flow in flows:
            self.__internal_add(flow)
        self._observers.notify([flow.id for flow in flows])

    def remove(self, flow_id: FlowId) -> None:
        if flow_id in self._flows:
            del self._flows[flow_id]
            self._observers.notify([flow_id])

    def get(self, flow_id: FlowId) -> Optional[Flow]:
        return self._flows.get(flow_id)

    def get_all(self) -> list[Flow]:
        return list(self._flows.values())
