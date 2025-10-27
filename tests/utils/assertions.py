from pathlib import Path
from typing import Iterable
from unittest.mock import Mock

import polars as pl
from polars.testing import assert_frame_equal

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


def assert_two_files_equal_sorted(
    actual_counts_file: Path, expected_counts_file: Path
) -> None:

    with open(actual_counts_file, mode="r") as actual:
        act_lines = sorted([line for line in actual.readlines()])

        with open(expected_counts_file, mode="r") as expected:
            exp_lines = sorted([line for line in expected.readlines()])

            assert set(act_lines) == set(exp_lines), (
                f"Sets are not equal [act len: {len(act_lines)}, "
                f"exp len {len(exp_lines)}]:\n"
                f"actual invents (fst.): "
                f"{([a for a in act_lines if a not in exp_lines] + [None])[0]}\n"
                f"actual missing (fst.): "
                f"{([e for e in exp_lines if e not in act_lines] + [None])[0]}\n"
                f"actual invents (scnd): "
                f"{([a for a in act_lines if a not in exp_lines] + [None] * 2)[1]}\n"
                f"actual missing (scnd): "
                f"{([e for e in exp_lines if e not in act_lines] + [None] * 2)[1]}\n"
                f"actual invents (num): "
                f"{len([a for a in act_lines if a not in exp_lines])}\n"
                f"actual missing (num): "
                f"{len([e for e in exp_lines if e not in act_lines])}\n"
            )

            assert act_lines == exp_lines, (
                f"First difference of {actual_counts_file.name} ({len(act_lines)}) "
                f"to expected {expected_counts_file.name} ({len(exp_lines)}):\n"
                f"exp: "
                f"{([e for e, a in zip(exp_lines, act_lines) if e != a] + [None])[0]}\n"
                f"act: "
                f"{([a for e, a in zip(exp_lines, act_lines) if e != a] + [None])[0]}\n"
                f"\n"
            )


def assert_equal_event_files(
    actual_counts_file: Path, expected_counts_file: Path
) -> None:
    actual = _read_event_csv(actual_counts_file)
    expected = _read_event_csv(expected_counts_file)
    assert_frame_equal(actual, expected)


def debugging_function_compare(actual: pl.DataFrame, expected: pl.DataFrame) -> None:
    actual_small = actual.select(
        [eventlist_exporter.ROAD_USER_ID, eventlist_exporter.FRAME_NUMBER]
    )
    expected_small = (
        expected.with_columns(
            pl.col(eventlist_exporter.ROAD_USER_ID).alias(
                f"expected_{eventlist_exporter.ROAD_USER_ID}"
            )
        )
        .with_columns(
            pl.col(eventlist_exporter.FRAME_NUMBER).alias(
                f"expected_{eventlist_exporter.FRAME_NUMBER}"
            )
        )
        .drop([eventlist_exporter.ROAD_USER_ID, eventlist_exporter.FRAME_NUMBER])
    )
    temp = pl.concat([actual_small, expected_small], how="horizontal")
    filtered = temp.filter(
        pl.col(f"expected_{eventlist_exporter.FRAME_NUMBER}")
        != pl.col(eventlist_exporter.FRAME_NUMBER)
    )
    print(filtered)


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
    return data.with_columns(
        pl.col(eventlist_exporter.INTERPOLATED_OCCURRENCE)
        .str.to_datetime(DATE_TIME_FORMAT)
        .dt.round("1ms")
        .alias(eventlist_exporter.INTERPOLATED_OCCURRENCE)
    ).sort(by=eventlist_exporter.EXPORT_COLUMNS)
