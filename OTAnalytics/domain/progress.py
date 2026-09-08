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


class CompletionProgress(ABC):
    """Progress of work whose items complete in an order of their own.

    The `Progressbar` iterator contract cannot express concurrent work, where
    completion order is not sequence order. Here the caller reports each item as
    it finishes and polls whether the user asked to stop.
    """

    @abstractmethod
    def complete(self, item: str) -> None:
        """Report one item as completed.

        Args:
            item (str): the name of the completed item.
        """
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        """Stop showing the progress, whether the work finished or not."""
        raise NotImplementedError

    @property
    @abstractmethod
    def is_cancelled(self) -> bool:
        """Whether the user asked to abandon the work."""
        raise NotImplementedError


class CompletionProgressBuilder(ABC):
    """Builds progress for work whose items complete in an order of their own."""

    @abstractmethod
    def build(self, description: str, unit: str, total: int) -> CompletionProgress:
        """Build and show progress over a known number of items.

        Args:
            description (str): what the operation is doing.
            unit (str): the unit of the counted items.
            total (int): how many items are expected to complete.

        Returns:
            CompletionProgress: the progress to report completions to.
        """
        raise NotImplementedError


class NoCompletionProgress(CompletionProgress):
    """Progress that shows nothing, for front-ends that cannot display it."""

    def complete(self, item: str) -> None:
        pass

    def close(self) -> None:
        pass

    @property
    def is_cancelled(self) -> bool:
        return False


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

    def start(self, description: str, unit: str, total: int) -> CompletionProgress:
        """Show progress of work that is not driven by iterating a sequence.

        Builders that can only decorate a sequence show nothing, which is what a
        command line run wants: its output is already a log.

        Args:
            description (str): what the operation being tracked is doing.
            unit (str): the unit of the counted items.
            total (int): the number of items expected to complete.

        Returns:
            CompletionProgress: the progress to close once the work is done.
        """
        return NoCompletionProgress()


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
