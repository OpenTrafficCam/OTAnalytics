from pathlib import Path
from typing import Iterable
from unittest.mock import Mock

from OTAnalytics.domain.track import Detection, Track
from OTAnalytics.domain.track_dataset import TrackDataset


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


def assert_equal_track_properties(actual: Track, expected: Track) -> None:
    assert actual.id == expected.id
    assert actual.classification == expected.classification
    assert len(actual.detections) == len(expected.detections)
    for first_detection, second_detection in zip(
        expected.detections, actual.detections
    ):
        assert_equal_detection_properties(second_detection, first_detection)


def assert_track_datasets_equal(actual: TrackDataset, expected: TrackDataset) -> None:
    assert actual.track_ids == expected.track_ids

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


def assert_two_files_equal_sorted(
    actual_counts_file: Path, expected_counts_file: Path
) -> None:
    with open(actual_counts_file, mode="r") as actual:
        actual_lines = sorted(actual.readlines())
        with open(expected_counts_file, mode="r") as expected:
            expected_lines = sorted(expected.readlines())
            assert actual_lines == expected_lines
