from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from OTAnalytics.application.config_specification import OtConfigDefaultValueProvider

DEFAULT_LOG_FILE = Path("DEFAULT_LOG_FILE.log")
DEFAULT_SAVE_SUFFIX = "DEFAULT_SAVE_SUFFIX"
DEFAULT_SAVE_NAME = "DEFAULT_SAVE_NAME"


class CliParseError(Exception):
    pass


@dataclass(frozen=True)
class CliArguments:
    start_cli: bool
    debug: bool
    logfile_overwrite: bool
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


class CliValueProvider(OtConfigDefaultValueProvider):
    def __init__(self, cli_args: CliArguments) -> None:
        self._cli_args = cli_args

    @property
    def do_events(self) -> bool:
        return False

    @property
    def do_counting(self) -> bool:
        return False

    @property
    def track_files(self) -> set[Path]:
        if self._cli_args.track_files:
            return {Path(path) for path in self._cli_args.track_files}
        return set()

    @property
    def event_formats(self) -> set[str]:
        return (
            set(self._cli_args.event_formats) if self._cli_args.event_formats else set()
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
            else set()
        )

    @property
    def num_processes(self) -> int:
        return self._cli_args.num_processes if self._cli_args.num_processes else 1

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
