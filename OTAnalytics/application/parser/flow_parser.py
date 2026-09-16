from abc import ABC, abstractmethod
from collections.abc import Iterable, Sequence
from pathlib import Path

from OTAnalytics.domain.flow import Flow
from OTAnalytics.domain.section import Section


class FlowParser(ABC):
    @abstractmethod
    def parse(self, file: Path) -> tuple[Sequence[Section], Sequence[Flow]]:
        pass

    @abstractmethod
    def parse_content(
        self,
        section_content: list[dict],
        flow_content: list[dict],
    ) -> tuple[Sequence[Section], Sequence[Flow]]:
        pass

    @abstractmethod
    def parse_section(self, entry: dict) -> Section:
        pass

    @abstractmethod
    def serialize(
        self,
        sections: Iterable[Section],
        flows: Iterable[Flow],
        file: Path,
    ) -> None:
        pass

    @abstractmethod
    def convert(
        self,
        sections: Iterable[Section],
        flows: Iterable[Flow],
    ) -> dict[str, list[dict]]:
        pass
