from datetime import datetime
from typing import Callable, Iterable, Optional

from OTAnalytics.domain.filter import Filter, FilterBuilder, FilterBuildError, Predicate
from OTAnalytics.domain.track import Track


class TrackPredicate(Predicate[Track, bool]):
    """A predicate that takes in a `Track` to test against.

    Args:
        predicate (Callable[[Track], bool] | None): Optional to supply a complex
            predicate. If none is supplied, the predicate implemented in this class
            will be used.
    """

    def __init__(self, predicate: Callable[[Track], bool] | None = None) -> None:
        super().__init__(predicate)

    def conjunct_with(self, other: Predicate[Track, bool]) -> Predicate[Track, bool]:
        combined_predicate: Callable[[Track], bool] = lambda track: self.test(
            track
        ) and other.test(track)
        return TrackPredicate(combined_predicate)


class TrackIsWithinDate(TrackPredicate):
    """Checks if a track is within a date range.

    Args:
        start_date (datetime): start date of the date range
        end_date (datetime): end date of the date range
        predicate (Callable[[Track], bool] | None, optional): Optional to supply a
            complex predicate. If none is supplied, the predicate implemented in this
            class will be used. Defaults to None.
    """

    def __init__(
        self,
        start_date: datetime,
        end_date: datetime,
        predicate: Callable[[Track], bool] | None = None,
    ) -> None:
        super().__init__(predicate)
        self._start_date = start_date
        self._end_date = end_date

    def test(self, to_test: Track) -> bool:
        return (
            self._start_date <= to_test.detections[0].occurrence
            and to_test.detections[0].occurrence < self._end_date
        )


class TrackHasClassifications(TrackPredicate):
    """Checks if track has classifications.

    Args:
        classification (list[str]): the classifications to be tested against
        predicate (Callable[[Track], bool] | None, optional): Optional to supply a
        complex predicate. If none is supplied, the predicate implemented in this
        class will be used. Defaults to None.
    """

    def __init__(
        self,
        classification: list[str],
        predicate: Callable[[Track], bool] | None = None,
    ) -> None:
        super().__init__(predicate)
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
        predicate (Predicate[Track, bool]): the predicate to test the tracks against
    """

    def __init__(self, predicate: Predicate[Track, bool]) -> None:
        super().__init__(predicate)

    def apply(self, data: Iterable[Track]) -> Iterable[Track]:
        return [datum for datum in data if self._predicate.test(datum)]


class TrackFilterBuilder(FilterBuilder):
    """A builder used to build a `TrackFilter`."""

    def __init__(self) -> None:
        self._complex_predicate: Optional[Predicate[Track, bool]] = None

    def add_has_classifications_predicate(self, classifications: list[str]) -> None:
        predicate = TrackHasClassifications(classifications)
        if self._complex_predicate:
            self._complex_predicate = self._complex_predicate.conjunct_with(predicate)
        else:
            self._complex_predicate = predicate

    def add_is_within_date_predicate(
        self, start_date: datetime, end_date: datetime
    ) -> None:
        predicate = TrackIsWithinDate(start_date, end_date)
        if self._complex_predicate:
            self._complex_predicate = self._complex_predicate.conjunct_with(predicate)
        else:
            self._complex_predicate = predicate

    def build(self) -> TrackFilter:
        if not self._complex_predicate:
            raise FilterBuildError(
                "Unable to build track filter. Builder property 'complex_predicate' is"
                " not set."
            )
        return TrackFilter(self._complex_predicate)
