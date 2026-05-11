from datetime import datetime, timezone
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
from tests.utils.builders.track_builder import TrackBuilder


@pytest.fixture
def track(track_builder: TrackBuilder) -> Track:
    track_builder.add_occurrence(2000, 1, 2, 0, 0, 0, 0)
    track_builder.append_detection()
    track_builder.append_detection()
    track_builder.append_detection()
    track_builder.append_detection()
    track_builder.append_detection()
    return track_builder.build_track()


class TestTrackPredicates:
    @pytest.mark.parametrize(
        "predicate, expected_result",
        [
            (TrackStartsAtOrAfterDate(datetime(2000, 1, 1, tzinfo=timezone.utc)), True),
            (
                TrackStartsAtOrAfterDate(datetime(2000, 1, 5, tzinfo=timezone.utc)),
                False,
            ),
            (TrackEndsBeforeOrAtDate(datetime(2000, 1, 3, tzinfo=timezone.utc)), True),
            (TrackEndsBeforeOrAtDate(datetime(2000, 1, 1, tzinfo=timezone.utc)), False),
            (TrackHasClassifications({"car", "truck"}), True),
            (TrackHasClassifications({"bicycle", "truck"}), False),
            (
                TrackStartsAtOrAfterDate(
                    datetime(2000, 1, 1, tzinfo=timezone.utc)
                ).conjunct_with(TrackHasClassifications({"truck", "car"})),
                True,
            ),
            (
                TrackStartsAtOrAfterDate(
                    datetime(2000, 1, 1, tzinfo=timezone.utc)
                ).conjunct_with(TrackHasClassifications({"truck", "bicycle"})),
                False,
            ),
        ],
    )
    def test_predicates(
        self, predicate: TrackPredicate, expected_result: bool, track: Track
    ) -> None:
        assert predicate.test(track) is expected_result


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
        builder.build()

        track_filter = builder.get_result()
        assert hasattr(track_filter, "_predicate")
        assert type(track_filter._predicate) is TrackStartsAtOrAfterDate
        assert track_filter._predicate._start_date == start_date

    def test_add_ends_before_or_at_predicate(self) -> None:
        end_date = datetime(2000, 1, 3)

        builder = TrackFilterBuilder()
        builder.add_ends_before_or_at_date_predicate(end_date)
        builder.build()

        track_filter = builder.get_result()
        assert hasattr(track_filter, "_predicate")
        assert type(track_filter._predicate) is TrackEndsBeforeOrAtDate
        assert track_filter._predicate._end_date == end_date

    def test_add_has_classifications_predicate(self) -> None:
        classifications = {"car", "truck"}
        builder = TrackFilterBuilder()
        builder.add_has_classifications_predicate(classifications)
        builder.build()

        track_filter = builder.get_result()
        assert hasattr(track_filter, "_predicate")
        assert type(track_filter._predicate) is TrackHasClassifications
        assert track_filter._predicate._classifications == classifications

    def test_add_multiple_predicates_fulfills(self, track: Track) -> None:
        start_date = datetime(2000, 1, 1, tzinfo=timezone.utc)
        classifications = {"car", "truck"}

        builder = TrackFilterBuilder()
        builder.add_has_classifications_predicate(classifications)
        builder.add_starts_at_or_after_date_predicate(start_date)
        builder.build()
        track_filter = builder.get_result()

        result = track_filter.apply([track])
        assert result == [track]

    def test_add_multiple_predicates_not_fulfilled(self, track: Track) -> None:
        start_date = datetime(2000, 1, 1, tzinfo=timezone.utc)
        classifications = {"bicycle", "truck"}

        builder = TrackFilterBuilder()
        builder.add_has_classifications_predicate(classifications)
        builder.add_starts_at_or_after_date_predicate(
            start_date,
        )
        builder.build()
        track_filter = builder.get_result()

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
        builder.build()
        track_filter = builder.get_result()

        assert type(track_filter) is NoOpTrackFilter

    def test_reset(self) -> None:
        builder = TrackFilterBuilder()
        builder.add_has_classifications_predicate({"car"})

        builder.build()
        assert builder._result is not None
        assert builder._complex_predicate is not None

        builder.get_result()
        assert builder._result is None
        assert builder._complex_predicate is None
