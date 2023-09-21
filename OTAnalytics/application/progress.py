from typing import Any, Callable, Iterator, Optional, Sequence

from OTAnalytics.application.config import DEFAULT_PROGRESSBAR_STEP_PERCENTAGE
from OTAnalytics.domain.progress import Counter, Progressbar


class SimpleCounter(Counter):
    def __init__(self) -> None:
        self._value = 0

    def increment(self, value: int = 1) -> None:
        self._value += value

    def reset(self) -> None:
        self._value = 0

    def get_value(self) -> int:
        return self._value


class AutoIncrementingProgressbar(Progressbar):
    def __init__(
        self,
        sequence: Sequence,
        counter: Counter,
        notify: Optional[Callable[[], None]] = None,
        step_percentage: int = DEFAULT_PROGRESSBAR_STEP_PERCENTAGE,
    ) -> None:
        self.__validate(step_percentage)
        self._sequence = sequence
        self._counter = counter
        self._notify = notify
        self._step_percentage = step_percentage
        self._iterator = iter(self._sequence)
        self._counter.reset()

    def __validate(self, step_percentage: int) -> None:
        if 1 <= step_percentage <= 100:
            return
        raise ValueError("Step percentage must be between 1 and 100.")

    def __iter__(self) -> Iterator:
        total_elements = len(self._sequence)
        step_size = self.__get_step_size(total_elements)
        self._counter.reset()
        self._iterator = iter(self._sequence)
        while True:
            try:
                yield next(self._iterator)
                self._counter.increment(1)
                counter_value = self._counter.get_value()
                if counter_value == total_elements or counter_value % step_size == 0:
                    if self._notify:
                        self._notify()
            except StopIteration:
                return

    def __get_step_size(self, total_elements: int) -> int:
        step_size = int(total_elements * (self._step_percentage / 100))
        return step_size or 1


class ManualIncrementingProgressbar(Progressbar):
    def __init__(
        self,
        sequence: Sequence,
        counter: Counter,
        notify: Optional[Callable[[], None]] = None,
    ) -> None:
        self._sequence = sequence
        self._counter = counter
        self._notify = notify
        self._iterator = iter(self._sequence)
        self._counter.reset()

    def __iter__(self) -> Iterator:
        self._counter.reset()
        self._iterator = iter(self._sequence)
        return self

    def __next__(self) -> Any:
        next_element = next(self._iterator)
        if self._notify:
            self._notify()
        return next_element

    def update(self, progress: int) -> None:
        """Update the progressbar by passed value.

        Args:
            value (int): value to update the progressbar by.
        """
        self._counter.increment(progress)
        if self._notify:
            self._notify()
