from abc import ABC, abstractmethod
from datetime import datetime
from typing import Callable, Generic, Iterable, Optional, TypeVar

T = TypeVar("T")
S = TypeVar("S")


class Predicate(ABC, Generic[T, S]):
    """Represents a predicate to test values against.

    The predicate function taking input data of type `T` and evaluate to any sort of
    boolean like type `S`.

    Args:
        predicate (Optional[Callable[[T], S]]): Optional to supply a complex predicate.
            If none is supplied, the predicate implemented in this class will be used.
    """

    def __init__(self, predicate: Optional[Callable[[T], S]]) -> None:
        if not predicate:
            self._predicate: Callable[[T], S] = self.test
        else:
            self._predicate = predicate

    def test(self, to_test: T) -> S:
        """Test value against this predicate.

        Args:
            to_test (T): the value under test

        Returns:
            S: whether the value fulfills the predicate.
        """
        return self._predicate(to_test)

    @abstractmethod
    def conjunct_with(self, other: "Predicate[T,S]") -> "Predicate[T, S]":
        """Creates a conjunction of this predicate with another one and returning it.


        Args:
            other (Predicate[T,S]): the other predicate to conjunct with this predicate


        Returns:
            Predicate[T, S]: the conjunction
        """
        pass


class Filter(ABC, Generic[T, S]):
    """Filter out elements of an iterable that don't fulfill the predicate.

    Args:
        predicate (Predicate[T, S]): the predicate which is used to test the elements
            against.
    """

    def __init__(self, predicate: Predicate[T, S]) -> None:
        self._predicate = predicate

    @abstractmethod
    def apply(self, iterable: Iterable[T]) -> Iterable[T]:
        """Apply the filter on elements of the iterable.

        Args:
            iterable (Iterable[T]): the iterable to apply the filter on

        Returns:
            Iterable[T]: all elements in the iterable that fulfill the predicate
        """
        pass


class FilterBuildError(Exception):
    pass


class FilterBuilder:
    """Class to build `Filter`s."""

    @abstractmethod
    def build(self) -> Filter:
        """Builds a filter.

        Returns:
            Filter: the built filter
        """
        pass

    @abstractmethod
    def add_is_within_date_predicate(
        self, start_date: datetime, end_date: datetime
    ) -> None:
        """Add is within date predicate.

        Args:
            start_date (datetime): the start date
            end_date (datetime): the end date
        """
        pass

    @abstractmethod
    def add_has_classifications_predicate(self, classifications: list[str]) -> None:
        """Add has classifications predicate.

        Args:
            classifications (list[str]): the classifications
        """
        pass


class FilterElement:
    """Contains all filter information.

    Args:
        start_date (Optional[datetime]): the start date to filter
        end_date (Optional[datetime]): the end date to filter
        classifications (list[str]): the classifications to filter
    """

    def __init__(
        self, start_date: datetime, end_date: datetime, classifications: list[str]
    ) -> None:
        self.start_date = start_date
        self.end_date = end_date
        self.classifications = classifications

    def build_filter(self, filter_builder: FilterBuilder) -> Filter:
        """Build filter.

        Args:
            filter_builder (FilterBuilder): the builder to be used to create the filter

        Returns:
            Filter: the filter
        """
        if self.classifications:
            filter_builder.add_has_classifications_predicate(self.classifications)

        if self.start_date and self.end_date:
            filter_builder.add_is_within_date_predicate(self.start_date, self.end_date)
        return filter_builder.build()
