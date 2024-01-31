from abc import ABC, abstractmethod
from pathlib import Path


class OtConfigDefaultValueProvider(ABC):
    @property
    @abstractmethod
    def do_events(self) -> bool:
        raise NotImplementedError

    @property
    @abstractmethod
    def do_counting(self) -> bool:
        raise NotImplementedError

    @property
    @abstractmethod
    def track_files(self) -> set[Path]:
        raise NotImplementedError

    @property
    @abstractmethod
    def event_formats(self) -> set[str]:
        raise NotImplementedError

    @property
    @abstractmethod
    def save_name(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def save_suffix(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def count_intervals(self) -> set[int]:
        raise NotImplementedError

    @property
    @abstractmethod
    def num_processes(self) -> int:
        raise NotImplementedError

    @property
    @abstractmethod
    def log_file(self) -> Path:
        raise NotImplementedError

    @property
    @abstractmethod
    def debug(self) -> bool:
        raise NotImplementedError
