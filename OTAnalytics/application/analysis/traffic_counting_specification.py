from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable


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
    output_format: str
    output_file: str


@dataclass(frozen=True)
class ExportSpecificationDto:
    """
    Data transfer object to represent the counting.
    """

    counting_specification: CountingSpecificationDto
    flow_names: list[str]

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
