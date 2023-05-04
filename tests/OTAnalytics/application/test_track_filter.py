from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from OTAnalytics.application.track_filter import (
    NoOpTrackFilter,
    TrackEndsBeforeOrAtDate,
    TrackFilter,
    TrackFilterBuilder,
    TrackHasClassifications,
    TrackPredicate,
    TrackStartsAtOrAfterDate,
)
from OTAnalytics.domain.track import Track
from tests.conftest import TrackBuilder


@pytest.fixture
def track(track_builder: TrackBuilder) -> Track:
    track_builder.add_occurrence(2000, 1, 2, 0, 0, 0, 0)
    track_builder.append_detection()
    track_builder.append_detection()
    track_builder.append_detection()
    track_builder.append_detection()
    track_builder.append_detection()
    return track_builder.build_track()


class TestTrackStartsAtOrAfterDate:
    def test_starts_at_or_after_date(self, track: Track) -> None:
        start_date = datetime(2000, 1, 1)

        predicate = TrackStartsAtOrAfterDate(start_date)
        result = predicate.test(track)
        assert result is True

    def test_date_outside_range(self, track: Track) -> None:
        start_date = datetime(2000, 1, 5)

        predicate = TrackStartsAtOrAfterDate(start_date)
        result = predicate.test(track)
        assert result is False


class TestTrackEndBeforeOrAtDate:
    def test_ends_before_or_at_date(self, track: Track) -> None:
        end_date = datetime(2000, 1, 3)

        predicate = TrackEndsBeforeOrAtDate(end_date)
        result = predicate.test(track)
        assert result is True

    def test_date_outside_range(self, track: Track) -> None:
        end_date = datetime(2000, 1, 1)

        predicate = TrackEndsBeforeOrAtDate(end_date)
        result = predicate.test(track)
        assert result is False


class TestTrackHasClassifications:
    def test_has_same_class(self, track: Track) -> None:
        predicate = TrackHasClassifications(["car", "truck"])
        result = predicate.test(track)
        assert result is True

    def test_has_not_same_class(self, track: Track) -> None:
        predicate = TrackHasClassifications(["bicycle", "truck"])
        result = predicate.test(track)
        assert result is False


class TestTrackPredicateConjunction:
    def test_conjunct_predicate_fulfilled(self, track: Track) -> None:
        start_date = datetime(2000, 1, 1)
        starts_at_or_after_date = TrackStartsAtOrAfterDate(start_date)
        has_classifications = TrackHasClassifications(["truck", "car"])
        has_class_and_within_date = starts_at_or_after_date.conjunct_with(
            has_classifications
        )
        result = has_class_and_within_date.test(track)
        assert result is True

    def test_conjunct_predicate_not_fulfilled(self, track: Track) -> None:
        start_date = datetime(2000, 1, 1)
        starts_at_or_after_date = TrackStartsAtOrAfterDate(start_date)
        has_classifications = TrackHasClassifications(["truck", "bicycle"])
        has_class_and_within_date = starts_at_or_after_date.conjunct_with(
            has_classifications
        )
        result = has_class_and_within_date.test(track)
        assert result is False


class TestTrackFilter:
    @patch("OTAnalytics.application.track_filter.TrackPredicate")
    def test_filter_tracks_fulfill_all(
        self, mock_predicate: Mock, track: Track
    ) -> None:
        tracks = [track, track]

        predicate = mock_predicate.return_value
        predicate.test.return_value = True

        track_filter = TrackFilter(predicate)
        result = track_filter.apply(tracks)

        predicate.test.assert_any_call(track)
        assert predicate.test.call_count == 2
        assert result == tracks

    @patch("OTAnalytics.application.track_filter.TrackPredicate")
    def test_filter_some_tracks_fulfill_predicate(
        self, mock_predicate: Mock, track: Track
    ) -> None:
        tracks = [track, track]

        predicate = mock_predicate.return_value
        predicate.test.side_effect = [True, False]

        track_filter = TrackFilter(predicate)
        result = track_filter.apply(tracks)

        predicate.test.assert_any_call(track)
        assert predicate.test.call_count == 2
        assert result == [track]


class TestNoOpTrackFilter:
    def test_apply(self) -> None:
        track_filter = NoOpTrackFilter()
        iterable = [Mock()]
        result = track_filter.apply(iterable)
        assert result == iterable


class TestTrackFilterBuilder:
    def test_add_starts_at_or_after_date_predicate(self) -> None:
        start_date = datetime(2000, 1, 1)

        builder = TrackFilterBuilder()
        builder.add_starts_at_or_after_date_predicate(start_date)

        track_filter = builder.build()
        assert hasattr(track_filter, "_predicate")
        assert type(track_filter._predicate) == TrackStartsAtOrAfterDate
        assert track_filter._predicate._start_date == start_date

    def test_add_ends_before_or_at_predicate(self) -> None:
        end_date = datetime(2000, 1, 3)

        builder = TrackFilterBuilder()
        builder.add_ends_before_or_at_date_predicate(end_date)

        track_filter = builder.build()
        assert hasattr(track_filter, "_predicate")
        assert type(track_filter._predicate) == TrackEndsBeforeOrAtDate
        assert track_filter._predicate._end_date == end_date

    def test_add_has_classifications_predicate(self) -> None:
        classifications = ["car", "truck"]
        builder = TrackFilterBuilder()
        builder.add_has_classifications_predicate(classifications)

        track_filter = builder.build()
        assert hasattr(track_filter, "_predicate")
        assert type(track_filter._predicate) == TrackHasClassifications
        assert track_filter._predicate._classifications == classifications

    def test_add_multiple_predicates_fulfills(self, track: Track) -> None:
        start_date = datetime(2000, 1, 1)
        classifications = ["car", "truck"]

        builder = TrackFilterBuilder()
        builder.add_has_classifications_predicate(classifications)
        builder.add_starts_at_or_after_date_predicate(start_date)
        track_filter = builder.build()

        result = track_filter.apply([track])
        assert result == [track]

    def test_add_multiple_predicates_not_fulfilled(self, track: Track) -> None:
        start_date = datetime(2000, 1, 1)
        classifications = ["bicycle", "truck"]

        builder = TrackFilterBuilder()
        builder.add_has_classifications_predicate(classifications)
        builder.add_starts_at_or_after_date_predicate(
            start_date,
        )
        track_filter = builder.build()

        result = track_filter.apply([track])
        assert result == []

    def test_conjunct_first_predicate_added(self) -> None:
        predicate = Mock(spec=TrackPredicate)
        builder = TrackFilterBuilder()
        builder._conjunct(predicate)

        assert builder._complex_predicate == predicate

    def test_conjunct_complex_predicate(self) -> None:
        first_predicate = Mock(spec=TrackPredicate)
        second_predicate = Mock(spec=TrackPredicate)
        complex_predicate = Mock(spec=TrackPredicate)
        first_predicate.conjunct_with.return_value = complex_predicate

        builder = TrackFilterBuilder()
        builder._conjunct(first_predicate)
        builder._conjunct(second_predicate)

        assert builder._complex_predicate == complex_predicate

    def test_create_noop_filter_if_no_predicate_added(self) -> None:
        builder = TrackFilterBuilder()
        track_filter = builder.build()

        assert type(track_filter) == NoOpTrackFilter
