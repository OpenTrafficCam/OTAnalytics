from abc import ABC, abstractmethod
from typing import Any, Iterator, Sequence


class ProgressbarBuildError(Exception):
    pass


class Progressbar(ABC, Iterator):
    """Interface defining a Progressbar which implements the iterator interface."""

    @abstractmethod
    def __iter__(self) -> Iterator:
        return self

    @abstractmethod
    def __next__(self) -> Any:
        raise NotImplementedError


class ProgressbarBuilder(ABC):
    """Interface defining a Progressbar builder.

    ProgressbarBuilder is a Callable. The `__call__` method acts as the builder method
    providing new `Progressbar` instances.
    """

    @abstractmethod
    def __call__(self, sequence: Sequence, description: str, unit: str) -> Iterator:
        """Acts as the build method providing new Progressbar instances.

        Args:
            sequence (Sequence): the sequence to be iterated over
            description (str): the description
            unit (str): the unit

        Returns:
            Progressbar: a new Progressbar instance
        """
        raise NotImplementedError


class NoProgressbarBuilder(ProgressbarBuilder):
    def __call__(self, sequence: Sequence, description: str, unit: str) -> Iterator:
        return iter(sequence)
