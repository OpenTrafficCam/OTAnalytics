from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Iterable

from OTAnalytics.application.export_formats.export_mode import ExportMode


class CountingEvent(Enum):
    START = "start"
    END = "end"

    def __str__(self) -> str:
        return self.value

    @staticmethod
    def parse(value: "CountingEvent | str") -> "CountingEvent":
        if isinstance(value, CountingEvent):
            return value
        normalized = value.lower()
        for event in CountingEvent:
            if event.value == normalized:
                return event
        valid = ", ".join(sorted(event.value for event in CountingEvent))
        raise ValueError(f"Invalid counting event '{value}'. Use one of: {valid}.")


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
    export_directory: Path
    export_filename_stem: str
    export_mode: ExportMode
    count_all_events: bool = False
    counting_event: CountingEvent = CountingEvent.START

    def with_end(self, end: datetime) -> "CountingSpecificationDto":
        return CountingSpecificationDto(
            start=self.start,
            end=end,
            interval_in_minutes=self.interval_in_minutes,
            modes=self.modes,
            output_format=self.output_format,
            export_directory=self.export_directory,
            export_filename_stem=self.export_filename_stem,
            export_mode=self.export_mode,
            count_all_events=self.count_all_events,
            counting_event=self.counting_event,
        )


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
    def export_directory(self) -> Path:
        return self.counting_specification.export_directory

    @property
    def export_filename_stem(self) -> str:
        return self.counting_specification.export_filename_stem


class ExportCounts(ABC):
    def export(self, specification: CountingSpecificationDto) -> Path:
        raise NotImplementedError

    def get_supported_formats(self) -> Iterable[ExportFormat]:
        raise NotImplementedError
