from abc import ABC, abstractmethod
from typing import Optional

from OTAnalytics.domain.progress import Counter


class AbstractPopupProgressbar(ABC):
    def update_progress(self) -> None:
        raise NotImplementedError


class ProgressbarPopupBuilder(ABC):
    def __init__(self) -> None:
        self._counter: Optional[Counter] = None
        self._total: Optional[int] = None
        self._description = ""
        self._unit = ""

    def add_counter(self, counter: Counter) -> None:
        self._counter = counter

    def add_description(self, description: str) -> None:
        self._description = description

    def add_unit(self, unit: str) -> None:
        self._unit = unit

    def add_total(self, value: int) -> None:
        self._total = value

    @abstractmethod
    def build(self) -> AbstractPopupProgressbar:
        raise NotImplementedError
