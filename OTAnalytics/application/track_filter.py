from datetime import datetime
from typing import Iterable, Optional

from OTAnalytics.domain.filter import Conjunction, Filter, FilterBuilder, Predicate
from OTAnalytics.domain.track import Track


class TrackConjunction(Conjunction[Track, bool]):
    def __init__(
        self,
        first_predicate: Predicate[Track, bool],
        second_predicate: Predicate[Track, bool],
    ) -> None:
        """Represents the conjunction of two track predicates.

        Args:
            first_predicate (Predicate[Track, bool]): first predicate to conjunct with
            second_predicate (Predicate[Track, bool]): second predicate to conjunct with
        """
        super().__init__(first_predicate, second_predicate)

    def test(self, to_test: Track) -> bool:
        return self._first_predicate.test(to_test) and self._second_predicate.test(
            to_test
        )

    def conjunct_with(self, other: Predicate[Track, bool]) -> Predicate[Track, bool]:
        return TrackConjunction(self, other)


class TrackPredicate(Predicate[Track, bool]):
    """A predicate that takes in a `Track` to test against."""

    def conjunct_with(self, other: Predicate[Track, bool]) -> Predicate[Track, bool]:
        return TrackConjunction(self, other)


class TrackIsWithinDate(TrackPredicate):
    """Checks if a track is within a date range.

    Args:
        start_date (datetime): start date of the date range (inclusive)
        end_date (datetime): end date of the date range (inclusive)
    """

    def __init__(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> None:
        self._start_date = start_date
        self._end_date = end_date

    def test(self, to_test: Track) -> bool:
        return self._start_date <= to_test.detections[0].occurrence <= self._end_date


class TrackHasClassifications(TrackPredicate):
    """Checks if track has classifications.

    Args:
        classification (list[str]): the classifications to be tested against
    """

    def __init__(
        self,
        classification: list[str],
    ) -> None:
        self._classifications = classification

    def test(self, to_test: Track) -> bool:
        """Test if track has classification.

        Args:
            to_test (Track): the track under test

        Returns:
            bool: `True` if track has classification. Otherwise `False`.
        """
        return to_test.classification in self._classifications


class TrackFilter(Filter[Track, bool]):
    """A `Track` filter.

    Args:
        Filter (Filter[Track, bool]): extends the `Filter` interface
        predicate (Predicate[Track, bool]): the predicate to test against during
            filtering
    """

    def __init__(self, predicate: Predicate[Track, bool]) -> None:
        self._predicate = predicate

    def apply(self, data: Iterable[Track]) -> Iterable[Track]:
        return [datum for datum in data if self._predicate.test(datum)]


class NoOpTrackFilter(Filter[Track, bool]):
    """Returns the tracks as is without any filtering."""

    def apply(self, iterable: Iterable[Track]) -> Iterable[Track]:
        return iterable


class TrackFilterBuilder(FilterBuilder):
    """A builder used to build a `TrackFilter`."""

    def __init__(self) -> None:
        self._complex_predicate: Optional[Predicate[Track, bool]] = None

    def add_has_classifications_predicate(self, classifications: list[str]) -> None:
        predicate = TrackHasClassifications(classifications)
        self._conjunct(predicate)

    def add_is_within_date_predicate(
        self, start_date: datetime, end_date: datetime
    ) -> None:
        predicate = TrackIsWithinDate(start_date, end_date)
        self._conjunct(predicate)

    def build(self) -> Filter[Track, bool]:
        if self._complex_predicate is None:
            return NoOpTrackFilter()

        return TrackFilter(self._complex_predicate)

    def _conjunct(self, predicate: Predicate[Track, bool]) -> None:
        """Conjuncts a new predicate if an existing predicate was already built by
        the builder.
        """
        if self._complex_predicate:
            self._complex_predicate = self._complex_predicate.conjunct_with(predicate)
        else:
            self._complex_predicate = predicate
