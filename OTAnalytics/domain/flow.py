from dataclasses import dataclass
from typing import Optional

from OTAnalytics.domain.section import Section


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

    def __init__(
        self,
        id: FlowId,
        start: Section,
        end: Section,
        distance: float,
    ) -> None:
        if distance < 0:
            raise ValueError(
                f"Distance must be equal or greater then 0, but is {distance}"
            )
        self.id: FlowId = id
        self.start: Section = start
        self.end: Section = end
        self._distance: float = distance

    def distance(self) -> float:
        return self._distance


class FlowRepository:
    def __init__(self) -> None:
        self._flows: dict[FlowId, Flow] = {}

    def add(self, flow: Flow) -> None:
        self._flows[flow.id] = flow

    def get(self, flow_id: FlowId) -> Optional[Flow]:
        return self._flows.get(flow_id)

    def get_all(self) -> list[Flow]:
        return list(self._flows.values())
