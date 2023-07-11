from typing import Any, Callable, Iterator, Optional, Sequence

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


class NotifyableProgressbar(Progressbar):
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
        try:
            next_element = next(self._iterator)
            if self._notify:
                self._notify()
            self._counter.increment(1)
            return next_element
        except StopIteration:
            if self._notify:
                self._notify()
            raise StopIteration

    def update(self, progress: int) -> None:
        self._counter.increment(progress)
