from abc import ABC, abstractmethod
from dataclasses import dataclass

from OTAnalytics.application.use_cases.export_events import EventListExporter


class CliParseError(Exception):
    pass


@dataclass(frozen=True)
class CliArguments:
    start_cli: bool
    debug: bool
    track_files: list[str]
    sections_file: str
    save_name: str
    save_suffix: str
    event_list_exporter: EventListExporter
    count_interval: int
    num_processes: int
    log_file: str
    logfile_overwrite: bool


class CliParser(ABC):
    @abstractmethod
    def parse(self) -> CliArguments:
        raise NotImplementedError
