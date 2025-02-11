from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from OTAnalytics.application.config import (
    DEFAULT_COUNTING_INTERVAL_IN_MINUTES,
    DEFAULT_EVENTLIST_FILE_TYPE,
    DEFAULT_NUM_PROCESSES,
)
from OTAnalytics.application.config_specification import OtConfigDefaultValueProvider
from OTAnalytics.application.logger import DEFAULT_LOG_FILE

DEFAULT_SAVE_SUFFIX = ""
DEFAULT_SAVE_NAME = ""
BULK = "bulk"
STREAM = "stream"


class CliMode(Enum):
    BULK = BULK
    STREAM = STREAM

    def __str__(self) -> str:
        return self.value


class CliParseError(Exception):
    pass


@dataclass(frozen=True)
class CliArguments:
    start_cli: bool
    cli_mode: CliMode
    cli_chunk_size: int
    debug: bool
    logfile_overwrite: bool
    track_export: bool
    track_statistics_export: bool
    start_webui: bool = False
    show_svz: bool = False
    config_file: str | None = None
    track_files: list[str] | None = None
    otflow_file: str | None = None
    save_dir: str | None = None
    save_name: str | None = None
    save_suffix: str | None = None
    event_formats: list[str] | None = None
    count_intervals: list[int] | None = None
    num_processes: int | None = None
    log_file: str | None = None
    include_classes: list[str] | None = None
    exclude_classes: list[str] | None = None


class CliValueProvider(OtConfigDefaultValueProvider):
    def __init__(self, cli_args: CliArguments) -> None:
        self._cli_args = cli_args

    @property
    def do_events(self) -> bool:
        return True

    @property
    def do_counting(self) -> bool:
        return True

    @property
    def track_files(self) -> set[Path]:
        if self._cli_args.track_files:
            return {Path(path) for path in self._cli_args.track_files}
        return set()

    @property
    def event_formats(self) -> set[str]:
        return (
            set(self._cli_args.event_formats)
            if self._cli_args.event_formats
            else {DEFAULT_EVENTLIST_FILE_TYPE}
        )

    @property
    def save_name(self) -> str:
        return (
            self._cli_args.save_name if self._cli_args.save_name else DEFAULT_SAVE_NAME
        )

    @property
    def save_suffix(self) -> str:
        return (
            self._cli_args.save_suffix
            if self._cli_args.save_suffix
            else DEFAULT_SAVE_SUFFIX
        )

    @property
    def count_intervals(self) -> set[int]:
        return (
            set(self._cli_args.count_intervals)
            if self._cli_args.count_intervals
            else {DEFAULT_COUNTING_INTERVAL_IN_MINUTES}
        )

    @property
    def num_processes(self) -> int:
        return (
            self._cli_args.num_processes
            if self._cli_args.num_processes
            else DEFAULT_NUM_PROCESSES
        )

    @property
    def log_file(self) -> Path:
        return (
            Path(self._cli_args.log_file)
            if self._cli_args.log_file
            else DEFAULT_LOG_FILE
        )

    @property
    def debug(self) -> bool:
        return self._cli_args.debug


class CliParser(ABC):
    @abstractmethod
    def parse(self) -> CliArguments:
        raise NotImplementedError
