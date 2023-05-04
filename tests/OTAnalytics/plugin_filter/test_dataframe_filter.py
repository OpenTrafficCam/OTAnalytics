from __future__ import annotations

from datetime import datetime
from typing import Iterable
from unittest.mock import Mock

import pytest
from pandas import DataFrame, Series

from OTAnalytics.domain.filter import FilterBuildError
from OTAnalytics.domain.track import (
    CLASSIFICATION,
    FRAME,
    OCCURRENCE,
    TRACK_ID,
    Detection,
    Track,
)
from OTAnalytics.plugin_filter.dataframe_filter import (
    DataFrameFilter,
    DataFrameFilterBuilder,
    DataFrameHasClassifications,
    DataFrameIsWithinDate,
    NoOpDataFrameFilter,
)
from tests.conftest import TrackBuilder


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
    converted = DataFrame(prepared)
    return converted.sort_values([TRACK_ID, FRAME])


@pytest.fixture
def track(track_builder: TrackBuilder) -> Track:
    track_builder.add_occurrence(2000, 1, 2, 0, 0, 0, 0)
    track_builder.append_detection()
    track_builder.append_detection()
    track_builder.append_detection()
    track_builder.append_detection()
    track_builder.append_detection()
    return track_builder.build_track()


@pytest.fixture
def track_dataframe(track: Track) -> DataFrame:
    return convert_tracks_to_dataframe([track])


class TestDataFrameIsWithinDate:
    def test_within_range(self, track_dataframe: DataFrame) -> None:
        start_date = datetime(2000, 1, 1)
        end_date = datetime(2000, 1, 3)

        predicate = DataFrameIsWithinDate(OCCURRENCE, start_date, end_date)
        result = predicate.test(track_dataframe)
        assert result.equals(Series([True, True, True, True, True]))

    def test_outside_range(self, track_dataframe: DataFrame) -> None:
        start_date = datetime(2000, 1, 10)
        end_date = datetime(2000, 1, 12)

        predicate = DataFrameIsWithinDate(OCCURRENCE, start_date, end_date)
        result = predicate.test(track_dataframe)
        assert result.equals(Series([False, False, False, False, False]))


class TestDataFrameHasClassification:
    def test_has_classifications(self, track_dataframe: DataFrame) -> None:
        predicate = DataFrameHasClassifications(CLASSIFICATION, ["car", "truck"])
        result = predicate.test(track_dataframe)

        assert result.equals(Series([True, True, True, True, True]))

    def test_has_not_classifications(self, track_dataframe: DataFrame) -> None:
        predicate = DataFrameHasClassifications(CLASSIFICATION, ["bicycle", "truck"])
        result = predicate.test(track_dataframe)

        assert result.equals(Series([False, False, False, False, False]))


class TestDataFramePredicateConjunction:
    def test_conjunct_predicate_fulfilled(self, track_dataframe: DataFrame) -> None:
        start_date = datetime(2000, 1, 1)
        end_date = datetime(2000, 1, 3)
        is_within_date = DataFrameIsWithinDate(OCCURRENCE, start_date, end_date)
        has_classifications = DataFrameHasClassifications(
            CLASSIFICATION, ["car", "truck"]
        )
        has_class_and_within_date = is_within_date.conjunct_with(has_classifications)
        result = has_class_and_within_date.test(track_dataframe)

        assert result.equals(Series([True, True, True, True, True]))

    def test_conjunct_predicate_not_fulfilled(self, track_dataframe: DataFrame) -> None:
        start_date = datetime(2000, 1, 10)
        end_date = datetime(2000, 1, 11)
        is_within_date = DataFrameIsWithinDate(OCCURRENCE, start_date, end_date)
        has_classifications = DataFrameHasClassifications(
            CLASSIFICATION, ["car", "truck"]
        )
        has_class_and_within_date = is_within_date.conjunct_with(has_classifications)
        result = has_class_and_within_date.test(track_dataframe)

        assert result.equals(Series([False, False, False, False, False]))


class TestDataFrameFilter:
    def test_filter_tracks_fulfill_all(self, track_dataframe: DataFrame) -> None:
        start_date = datetime(2000, 1, 1)
        end_date = datetime(2000, 1, 3)
        is_within_date = DataFrameIsWithinDate(OCCURRENCE, start_date, end_date)
        has_classifications = DataFrameHasClassifications(
            CLASSIFICATION, ["car", "truck"]
        )
        has_class_and_within_date = is_within_date.conjunct_with(has_classifications)
        dataframe_filter = DataFrameFilter(has_class_and_within_date)

        result = list(dataframe_filter.apply([track_dataframe]))

        assert result[0].equals(track_dataframe)


class TestNoOpDataFrameFilter:
    def test_apply(self) -> None:
        track_filter = NoOpDataFrameFilter()
        iterable = [Mock()]
        result = track_filter.apply(iterable)
        assert result == iterable


class TestDataFrameFilterBuilder:
    def test_add_is_within_predicate(self) -> None:
        start_date = datetime(2000, 1, 1)
        end_date = datetime(2000, 1, 3)

        builder = DataFrameFilterBuilder()
        builder.set_occurrence_column(OCCURRENCE)
        builder.add_is_within_date_predicate(start_date, end_date)

        dataframe_filter = builder.build()
        assert hasattr(dataframe_filter, "_predicate")
        assert type(dataframe_filter._predicate) == DataFrameIsWithinDate
        assert dataframe_filter._predicate._start_date == start_date
        assert dataframe_filter._predicate._end_date == end_date

    def test_add_has_classifications_predicate(self) -> None:
        classifications = ["car", "truck"]

        builder = DataFrameFilterBuilder()
        builder.set_classification_column(CLASSIFICATION)
        builder.add_has_classifications_predicate(classifications)

        dataframe_filter = builder.build()
        assert hasattr(dataframe_filter, "_predicate")
        assert type(dataframe_filter._predicate) == DataFrameHasClassifications
        assert dataframe_filter._predicate._classifications == classifications

    def test_add_has_classifcations_predicate_raise_error(self) -> None:
        classifications = ["car", "truck"]
        builder = DataFrameFilterBuilder()

        with pytest.raises(FilterBuildError):
            builder.add_has_classifications_predicate(classifications)

    def test_add_is_within_date_predicate_raise_error(self) -> None:
        start_date = datetime(2000, 1, 1)
        end_date = datetime(2000, 1, 3)
        builder = DataFrameFilterBuilder()

        with pytest.raises(FilterBuildError):
            builder.add_is_within_date_predicate(start_date, end_date)

    def test_add_multiple_predicates(self) -> None:
        start_date = datetime(2000, 1, 1)
        end_date = datetime(2000, 1, 3)
        classifications = ["car", "truck"]

        builder = DataFrameFilterBuilder()
        builder.set_occurrence_column(OCCURRENCE)
        builder.add_is_within_date_predicate(start_date, end_date)

        builder.set_classification_column(CLASSIFICATION)
        builder.add_has_classifications_predicate(classifications)

        dataframe_filter = builder.build()
        assert hasattr(dataframe_filter, "_predicate")
        assert (
            type(dataframe_filter._predicate._first_predicate) == DataFrameIsWithinDate
        )
        assert (
            type(dataframe_filter._predicate._second_predicate)
            == DataFrameHasClassifications
        )

        assert dataframe_filter._predicate._first_predicate._start_date == start_date
        assert dataframe_filter._predicate._first_predicate._end_date == end_date

    def test_create_noop_filter_if_no_predicate_added(self) -> None:
        builder = DataFrameFilterBuilder()
        track_filter = builder.build()

        assert type(track_filter) == NoOpDataFrameFilter
