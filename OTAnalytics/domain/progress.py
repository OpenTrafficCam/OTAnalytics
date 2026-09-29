from abc import ABC, abstractmethod
from typing import Iterable, Iterator, Sequence


class ProgressbarBuildError(Exception):
    pass


class Counter(ABC):
    """Counter interface."""

    @abstractmethod
    def increment(self, value: int) -> None:
        """Increment the counter by passed value.

        Args:
            value (int): the value to increment the counter by.
        """
        raise NotImplementedError

    @abstractmethod
    def reset(self) -> None:
        """Resets the counter to zero."""
        raise NotImplementedError

    @abstractmethod
    def get_value(self) -> int:
        """Get current counter value.

        Returns:
            int: the current value.
        """
        raise NotImplementedError


class Progressbar(ABC, Iterable):
    """Interface defining a Progressbar which implements the iterable interface."""

    @abstractmethod
    def __iter__(self) -> Iterator:
        raise NotImplementedError


class RunningProgressbar(ABC):
    """A progressbar shown for as long as the caller keeps it open.

    Work handed to a worker thread cannot be tracked by iterating a sequence,
    because only the thread doing the work would advance it. Such a caller opens
    a progressbar, does the work, and closes it again.
    """

    @abstractmethod
    def close(self) -> None:
        """Stop showing the progress."""
        raise NotImplementedError


class NoRunningProgressbar(RunningProgressbar):
    """A progressbar showing nothing, for builders that only decorate sequences."""

    def close(self) -> None:
        pass


class ProgressbarBuilder(ABC):
    """Interface defining a Progressbar builder.

    ProgressbarBuilder is a Callable. The `__call__` method acts as the builder method
    providing new `Progressbar` instances.
    """

    @abstractmethod
    def __call__(self, sequence: Sequence, description: str, unit: str) -> Iterable:
        """Acts as the build method providing new Progressbar instances.

        Args:
            sequence (Sequence): the sequence to be iterated over
            description (str): the description
            unit (str): the unit

        Returns:
            Progressbar: a new Progressbar instance
        """
        raise NotImplementedError

    def start(self, description: str, unit: str, total: int) -> RunningProgressbar:
        """Show progress of work that is not driven by iterating a sequence.

        Builders that can only decorate a sequence show nothing, which is what a
        command line run wants: its output is already a log.

        Args:
            description (str): what the operation being tracked is doing.
            unit (str): the unit of the counted items.
            total (int): the number of items expected to complete.

        Returns:
            RunningProgressbar: the progressbar to close once the work is done.
        """
        return NoRunningProgressbar()


class NoProgressbarBuilder(ProgressbarBuilder):
    def __call__(self, sequence: Sequence, description: str, unit: str) -> Iterable:
        return iter(sequence)


class LazyProgressbarBuilder(ABC):
    @abstractmethod
    def __call__(self, iterator: Iterator, description: str, unit: str) -> Iterable:
        """Acts as the build method providing new Progressbar instances.

        Args:
            iterator(Iterator): the iterator to be decorated with the progressbar.
            description (str): the description.
            unit (str): the unit.

        Returns:
            Iterable: the progressbar-decorated iterator.
        """
        raise NotImplementedError
