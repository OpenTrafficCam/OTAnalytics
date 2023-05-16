from OTAnalytics.domain.section import Section


class Flow:
    def __init__(
        self,
        name: str,
        start: Section,
        end: Section,
        distance: float,
    ) -> None:
        self.name: str = name
        self.start: Section = start
        self.end: Section = end
        self._distance: float = distance

    def distance(self) -> float:
        return self._distance


class FlowRepository:
    def __init__(self) -> None:
        self._flows: dict[str, Flow] = {}

    def add(self, flow: Flow) -> None:
        self._flows[flow.name] = flow

    def get_all(self) -> list[Flow]:
        return list(self._flows.values())
