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

    interval_in_minutes: int
    start: datetime
    end: datetime
    format: str
    output_file: str


class ExportCounts(ABC):
    def export(self, specification: CountingSpecificationDto) -> None:
        raise NotImplementedError

    def get_supported_formats(self) -> Iterable[ExportFormat]:
        raise NotImplementedError
