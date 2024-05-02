from datetime import datetime, timezone
from typing import Iterable
from unittest.mock import Mock

import pytest
from pandas import DataFrame

from OTAnalytics.application.plotting import GetCurrentFrame
from OTAnalytics.domain import track
from OTAnalytics.domain.track import CLASSIFICATION, FRAME, OCCURRENCE, Detection, Track
from OTAnalytics.plugin_filter.dataframe_filter import (
    DataFrameEndsBeforeOrAtDate,
    DataFrameEndsBeforeOrAtFrame,
    DataFrameFilter,
    DataFrameFilterBuilder,
    DataFrameHasClassifications,
    DataFramePredicate,
    DataFrameStartsAtOrAfterDate,
    DataFrameStartsAtOrAfterFrame,
    NoOpDataFrameFilter,
)
from tests.utils.builders.track_builder import TrackBuilder


def convert_tracks_to_dataframe(tracks: Iterable[Track]) -> DataFrame:
    """
    Convert tracks into a dataframe.

    Args:
        tracks (Iterable[Track]): tracks to convert

    Returns:
        DataFrame: tracks as dataframe
    """
    detections: list[Detection] = []
    for current_track in tracks:
        detections.extend(current_track.detections)
    prepared = [detection.to_dict() for detection in detections]
    converted = DataFrame(prepared).set_index([track.TRACK_ID, track.OCCURRENCE])
    return converted.sort_values([track.TRACK_ID, track.FRAME])


@pytest.fixture
def simple_track(track_builder: TrackBuilder) -> Track:
    track_builder.add_occurrence(2000, 1, 2, 0, 0, 0, 0)
    track_builder.append_detection()
    track_builder.append_detection()
    track_builder.append_detection()
    track_builder.append_detection()
    track_builder.append_detection()
    return track_builder.build_track()


@pytest.fixture
def track_dataframe(simple_track: Track) -> DataFrame:
    return convert_tracks_to_dataframe([simple_track])


class TestDataFrameStartsAtOrAfterDate:
    def test_dataframe_with_wrong_index(self) -> None:
        df = DataFrame()
        df_filter = DataFrameStartsAtOrAfterDate(
            OCCURRENCE, datetime(2000, 1, 1, tzinfo=timezone.utc)
        )
        with pytest.raises(ValueError):
            df_filter.test(df)


class TestDataFrameEndsBeforeOrAtDate:
    def test_dataframe_with_wrong_index(self) -> None:
        df = DataFrame()
        df_filter = DataFrameEndsBeforeOrAtDate(
            OCCURRENCE, datetime(2000, 1, 1, tzinfo=timezone.utc)
        )
        with pytest.raises(ValueError):
            df_filter.test(df)


class TestDataFramePredicates:
    @pytest.mark.parametrize(
        "predicate, expected_mask",
        [
            (
                DataFrameStartsAtOrAfterDate(
                    OCCURRENCE, datetime(2000, 1, 1, tzinfo=timezone.utc)
                ),
                [True, True, True, True, True],
            ),
            (
                DataFrameStartsAtOrAfterDate(
                    OCCURRENCE, datetime(2000, 1, 10, tzinfo=timezone.utc)
                ),
                [False, False, False, False, False],
            ),
            (
                DataFrameStartsAtOrAfterFrame(FRAME, 0),
                [True, True, True, True, True],
            ),
            (
                DataFrameStartsAtOrAfterFrame(FRAME, 10),
                [False, False, False, False, False],
            ),
            (
                DataFrameHasClassifications(CLASSIFICATION, {"car", "truck"}),
                [True, True, True, True, True],
            ),
            (
                DataFrameHasClassifications(CLASSIFICATION, {"bicycle", "truck"}),
                [False, False, False, False, False],
            ),
            (
                DataFrameStartsAtOrAfterDate(
                    OCCURRENCE, datetime(2000, 1, 1, tzinfo=timezone.utc)
                ).conjunct_with(
                    DataFrameHasClassifications(CLASSIFICATION, {"car", "truck"}),
                ),
                [True, True, True, True, True],
            ),
            (
                DataFrameStartsAtOrAfterDate(
                    OCCURRENCE, datetime(2000, 1, 11, tzinfo=timezone.utc)
                ).conjunct_with(
                    DataFrameHasClassifications(CLASSIFICATION, {"car", "truck"}),
                ),
                [False, False, False, False, False],
            ),
        ],
    )
    def test_predicate(
        self,
        predicate: DataFramePredicate,
        expected_mask: list[bool],
        track_dataframe: DataFrame,
    ) -> None:
        result = predicate.test(track_dataframe)
        expected_result = track_dataframe[expected_mask]

        assert result.equals(expected_result)


class TestDataFrameFilter:
    def test_filter_tracks_fulfill_all(self, track_dataframe: DataFrame) -> None:
        start_date = datetime(2000, 1, 1, tzinfo=timezone.utc)
        starts_at_or_after_date = DataFrameStartsAtOrAfterDate(OCCURRENCE, start_date)
        has_classifications = DataFrameHasClassifications(
            CLASSIFICATION, {"car", "truck"}
        )
        has_class_and_within_date = starts_at_or_after_date.conjunct_with(
            has_classifications
        )
        dataframe_filter = DataFrameFilter(has_class_and_within_date)

        result = list(dataframe_filter.apply([track_dataframe]))

        assert result[0].equals(track_dataframe)


class TestNoOpDataFrameFilter:
    def test_apply(self) -> None:
        track_filter = NoOpDataFrameFilter()
        iterable = [Mock()]
        result = track_filter.apply(iterable)
        assert result == iterable


DEFAULT_FRAME = 1


class TestDataFrameFilterBuilder:
    @pytest.fixture
    def current_frame(self) -> Mock:
        current_frame = Mock(spec=GetCurrentFrame)
        frame = DEFAULT_FRAME
        current_frame.get_frame_number_for.return_value = frame
        return current_frame

    def test_add_starts_at_or_after_date_predicate(self, current_frame: Mock) -> None:
        start_date = datetime(2000, 1, 1)

        builder = DataFrameFilterBuilder(current_frame)
        builder.set_occurrence_column(OCCURRENCE)
        builder.add_starts_at_or_after_date_predicate(start_date)
        builder.build()
        dataframe_filter = builder.get_result()
        assert hasattr(dataframe_filter, "_predicate")
        assert type(dataframe_filter._predicate) is DataFrameStartsAtOrAfterFrame
        assert dataframe_filter._predicate._frame == DEFAULT_FRAME
        current_frame.get_frame_number_for.assert_called_once_with(start_date)

    def test_add_ends_before_or_at_date_predicate(self, current_frame: Mock) -> None:
        end_date = datetime(2000, 1, 3)

        builder = DataFrameFilterBuilder(current_frame)
        builder.set_occurrence_column(OCCURRENCE)
        builder.add_ends_before_or_at_date_predicate(end_date)
        builder.build()

        dataframe_filter = builder.get_result()
        assert hasattr(dataframe_filter, "_predicate")
        assert type(dataframe_filter._predicate) is DataFrameEndsBeforeOrAtFrame
        assert dataframe_filter._predicate._frame == DEFAULT_FRAME
        current_frame.get_frame_number_for.assert_called_once_with(end_date)

    def test_add_has_classifications_predicate(self, current_frame: Mock) -> None:
        classifications = {"car", "truck"}

        builder = DataFrameFilterBuilder(current_frame)
        builder.set_classification_column(CLASSIFICATION)
        builder.add_has_classifications_predicate(classifications)

        builder.build()

        dataframe_filter = builder.get_result()
        assert hasattr(dataframe_filter, "_predicate")
        assert type(dataframe_filter._predicate) is DataFrameHasClassifications
        assert dataframe_filter._predicate._classifications == classifications

    def test_add_has_classifications_predicate_column_not_set(
        self, current_frame: Mock
    ) -> None:
        classifications = {"car", "truck"}
        builder = DataFrameFilterBuilder(current_frame)
        builder.add_has_classifications_predicate(classifications)
        builder.build()
        dataframe_filter = builder.get_result()
        assert isinstance(dataframe_filter, NoOpDataFrameFilter)

    def test_add_starts_at_or_after_date_predicate_raise_error(
        self, current_frame: Mock
    ) -> None:
        start_date = datetime(2000, 1, 1)
        builder = DataFrameFilterBuilder(current_frame)
        builder.add_starts_at_or_after_date_predicate(start_date)
        builder.build()
        dataframe_filter = builder.get_result()
        assert isinstance(dataframe_filter, NoOpDataFrameFilter)

    def test_add_ends_before_or_date_predicate_raise_error(
        self, current_frame: Mock
    ) -> None:
        end_date = datetime(2000, 1, 1)
        builder = DataFrameFilterBuilder(current_frame)
        builder.add_ends_before_or_at_date_predicate(end_date)
        builder.build()
        dataframe_filter = builder.get_result()
        assert isinstance(dataframe_filter, NoOpDataFrameFilter)

    def test_add_multiple_predicates(self, current_frame: Mock) -> None:
        end_date = datetime(2000, 1, 3)
        classifications = {"car", "truck"}

        builder = DataFrameFilterBuilder(current_frame)
        builder.set_occurrence_column(OCCURRENCE)
        builder.add_ends_before_or_at_date_predicate(end_date)

        builder.set_classification_column(CLASSIFICATION)
        builder.add_has_classifications_predicate(classifications)

        builder.build()

        dataframe_filter = builder.get_result()
        assert hasattr(dataframe_filter, "_predicate")
        assert (
            type(dataframe_filter._predicate._first_predicate)
            is DataFrameEndsBeforeOrAtFrame
        )
        assert (
            type(dataframe_filter._predicate._second_predicate)
            is DataFrameHasClassifications
        )

        assert dataframe_filter._predicate._first_predicate._frame == DEFAULT_FRAME

    def test_create_noop_filter_if_no_predicate_added(
        self, current_frame: Mock
    ) -> None:
        builder = DataFrameFilterBuilder(current_frame)
        builder.build()
        track_filter = builder.get_result()

        assert type(track_filter) is NoOpDataFrameFilter

    def test_reset(self, current_frame: Mock) -> None:
        classifications = {"car", "truck"}

        builder = DataFrameFilterBuilder(current_frame)
        builder.set_classification_column(CLASSIFICATION)
        builder.set_occurrence_column(OCCURRENCE)
        builder.add_has_classifications_predicate(classifications)

        builder.build()
        assert builder._result is not None
        assert builder._complex_predicate is not None
        assert builder._classification_column == CLASSIFICATION
        assert builder._occurrence_column == OCCURRENCE

        builder.get_result()
        assert builder._result is None
        assert builder._complex_predicate is None
        assert builder._classification_column is None
        assert builder._occurrence_column is None
