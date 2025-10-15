from pathlib import Path
from typing import Iterable
from unittest.mock import Mock

import polars as pl
from polars.testing import assert_frame_equal

from OTAnalytics.application.export_formats import event_list
from OTAnalytics.application.export_formats.event_list import DATE_TIME_FORMAT
from OTAnalytics.domain.track import Detection, Track
from OTAnalytics.domain.track_dataset.track_dataset import TrackDataset
from OTAnalytics.plugin_prototypes.eventlist_exporter import eventlist_exporter


def assert_equal_detection_properties(actual: Detection, expected: Detection) -> None:
    assert expected.classification == actual.classification
    assert expected.confidence == actual.confidence
    assert expected.x == actual.x
    assert expected.y == actual.y
    assert expected.w == actual.w
    assert expected.h == actual.h
    assert expected.frame == actual.frame
    assert expected.occurrence == actual.occurrence
    assert expected.video_name == actual.video_name
    assert expected.interpolated_detection == actual.interpolated_detection
    assert actual.track_id == expected.track_id
    assert actual.input_file == expected.input_file


def assert_equal_track_properties(actual: Track, expected: Track) -> None:
    assert actual.id == expected.id
    assert actual.original_id == expected.original_id
    assert actual.classification == expected.classification
    assert len(actual.detections) == len(expected.detections)
    for first_detection, second_detection in zip(
        expected.detections, actual.detections
    ):
        assert_equal_detection_properties(second_detection, first_detection)


def assert_track_datasets_equal(actual: TrackDataset, expected: TrackDataset) -> None:
    assert len(actual.track_ids) == len(expected.track_ids)
    assert set(actual.track_ids) == set(expected.track_ids)

    for actual_track in actual.as_list():
        if expected_track := expected.get_for(actual_track.id):
            assert_equal_track_properties(actual_track, expected_track)
        else:
            raise AssertionError(
                f"Track with id {actual_track.id} not found in expected dataset"
            )


def assert_track_geometry_dataset_add_all_called_correctly(
    called_method: Mock, expected_arg: Iterable[Track]
) -> None:
    for actual_track, expected_track in zip(
        called_method.call_args_list[0][0][0], expected_arg
    ):
        assert_equal_track_properties(actual_track, expected_track)


def assert_track_dataset_has_tracks(dataset: TrackDataset, tracks: list[Track]) -> None:
    assert len(dataset) == len(tracks)
    for expected in tracks:
        actual = dataset.get_for(expected.id)
        assert actual
        assert_equal_track_properties(actual, expected)


def assert_equal_event_files(
    actual_counts_file: Path, expected_counts_file: Path
) -> None:
    actual = _read_event_csv(actual_counts_file)
    expected = _read_event_csv(expected_counts_file)
    assert_frame_equal(actual, expected)


def assert_equal_count_files(
    actual_counts_file: Path, expected_counts_file: Path
) -> None:
    actual = _read_counts_csv(actual_counts_file)
    expected = _read_counts_csv(expected_counts_file)
    assert_frame_equal(actual, expected)


def _read_counts_csv(file: Path) -> pl.DataFrame:
    return pl.read_csv(file)


def _read_event_csv(file: Path) -> pl.DataFrame:
    data = pl.read_csv(file)
    return (
        data.with_columns(
            pl.col(event_list.INTERPOLATED_OCCURRENCE)
            .str.to_datetime(DATE_TIME_FORMAT)
            .dt.round("1ms")
        )
        .with_columns(pl.col(event_list.INTERPOLATED_EVENT_COORDINATE_X).round(3))
        .with_columns(pl.col(event_list.INTERPOLATED_EVENT_COORDINATE_Y).round(3))
        .sort(by=eventlist_exporter.EXPORT_COLUMNS)
    )
