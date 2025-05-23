from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

from OTAnalytics.application.export_formats.export_mode import ExportMode


@dataclass(frozen=True)
class ExportFormat:
    name: str
    file_extension: str


@dataclass(frozen=True)
class CountingSpecificationDto:
    """
    Data transfer object to represent the counting.
    """

    start: datetime
    end: datetime
    interval_in_minutes: int
    modes: list[str]
    output_format: str
    output_file: str
    export_mode: ExportMode
    count_all_events: bool = False


@dataclass(frozen=True)
class FlowNameDto:
    name: str
    from_section: str
    to_section: str


@dataclass(frozen=True)
class ExportSpecificationDto:
    """
    Data transfer object to represent the counting.
    """

    counting_specification: CountingSpecificationDto
    flow_name_info: list[FlowNameDto]

    @property
    def format(self) -> str:
        return self.counting_specification.output_format

    @property
    def output_file(self) -> str:
        return self.counting_specification.output_file


class ExportCounts(ABC):
    def export(self, specification: CountingSpecificationDto) -> None:
        raise NotImplementedError

    def get_supported_formats(self) -> Iterable[ExportFormat]:
        raise NotImplementedError
