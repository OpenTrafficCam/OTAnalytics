from abc import ABC, abstractmethod
from dataclasses import dataclass


class CliParseError(Exception):
    pass


@dataclass(frozen=True)
class CliArguments:
    start_cli: bool
    debug: bool
    config_file: str | None
    track_files: list[str] | None
    otflow_file: str | None
    save_name: str
    save_suffix: str
    event_formats: str | None
    count_interval: int | None
    num_processes: int | None
    log_file: str | None
    logfile_overwrite: bool


class CliParser(ABC):
    @abstractmethod
    def parse(self) -> CliArguments:
        raise NotImplementedError
