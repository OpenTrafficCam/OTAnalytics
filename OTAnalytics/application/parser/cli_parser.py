from abc import ABC, abstractmethod
from dataclasses import dataclass


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
    save_name: str | None = None
    save_suffix: str | None = None
    event_formats: str | None = None
    count_interval: int | None = None
    num_processes: int | None = None
    log_file: str | None = None


class CliParser(ABC):
    @abstractmethod
    def parse(self) -> CliArguments:
        raise NotImplementedError
