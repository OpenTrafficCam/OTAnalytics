import asyncio
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
            progress (int): progress value to update the progressbar by.
        """
        self._counter.increment(progress)
        if self._notify:
            self._notify()


class Cancellation:
    """A signal that a long running operation should be abandoned.

    The signal can be polled via `is_cancelled` from synchronous code and
    awaited via `wait` from the event loop.
    """

    def __init__(self) -> None:
        self._cancelled = False
        self._event = asyncio.Event()

    @property
    def is_cancelled(self) -> bool:
        """Whether cancellation has been requested."""
        return self._cancelled

    def cancel(self) -> None:
        """Request cancellation. Cancelling an already cancelled signal is a no-op."""
        self._cancelled = True
        self._event.set()

    async def wait(self) -> None:
        """Wait until cancellation is requested."""
        await self._event.wait()


class ProgressState:
    """The progress of a long running operation, independent of any UI toolkit.

    Progress is tracked by a `Counter`, so it can be advanced either by iterating a
    sequence in order or by reporting completions as they arrive, which for
    concurrent work is not the order of the sequence.
    """

    def __init__(
        self,
        description: str,
        unit: str,
        total: int,
        counter: Counter,
        on_change: Optional[Callable[[], None]] = None,
    ) -> None:
        self._description = description
        self._unit = unit
        self._total = total
        self._counter = counter
        self._on_change = on_change
        self._current_item = ""

    @property
    def description(self) -> str:
        return self._description

    @property
    def current_item(self) -> str:
        """The item most recently reported as completed."""
        return self._current_item

    @property
    def fraction(self) -> float:
        """The share of items completed, between 0.0 and 1.0."""
        if not self._total:
            return 1.0
        return min(self._counter.get_value() / self._total, 1.0)

    @property
    def message(self) -> str:
        return (
            f"{self._description} {self._counter.get_value()}"
            f" / {self._total} {self._unit}"
        )

    @property
    def finished(self) -> bool:
        return self._counter.get_value() >= self._total

    def complete(self, item: str) -> None:
        """Report one item as completed.

        Args:
            item (str): the name of the completed item.
        """
        self._current_item = item
        self._counter.increment(1)
        self.notify()

    def notify(self) -> None:
        """Report progress made through the counter."""
        if self._on_change:
            self._on_change()
