from datetime import datetime

import pandas as pd
from pandas import DataFrame
from pytest import approx

from OTAnalytics.plugin_datastore.track_geometry_store.pandas_geometry_store import (
    create_track_segments,
    find_line_intersections,
)


def test_find_line_intersections_empty_df() -> None:
    """Test that an empty DataFrame returns an empty DataFrame."""
    df = DataFrame()
    result = find_line_intersections(df, "line1", 0.0, 0.0, 10.0, 10.0)
    assert result.empty


def test_find_line_intersections_no_intersections() -> None:
    """Test with segments that don't intersect with the line."""
    # Create test data
    segments_data = {
        "track-id": ["track1", "track2"],
        "start-x": [10.0, 100.0],
        "start-y": [15.0, 150.0],
        "end-x": [20.0, 110.0],
        "end-y": [25.0, 160.0],
        "start-occurrence": [
            datetime(2023, 1, 1, 10, 0, 0),
            datetime(2023, 1, 1, 10, 0, 0),
        ],
        "end-occurrence": [
            datetime(2023, 1, 1, 10, 0, 1),
            datetime(2023, 1, 1, 10, 0, 1),
        ],
    }
    segments_df = DataFrame(segments_data)

    # Define a line that doesn't intersect with any segment
    line_id = "non_intersecting_line"
    start_x = 0.0
    start_y = 100.0
    end_x = 5.0
    end_y = 105.0

    # Find intersections
    result = find_line_intersections(
        segments_df, line_id, start_x, start_y, end_x, end_y
    )

    # Check that no segments intersect
    assert not result["intersects"].any()
    assert (result["intersection_x"].isna()).all()
    assert (result["intersection_y"].isna()).all()
    assert (result["intersection_line_id"].isna()).all()


def test_find_line_intersections_with_intersections() -> None:
    """Test with segments that intersect with the line."""
    # Create test data
    segments_data = {
        "track-id": ["track1", "track2"],
        "start-x": [10.0, 100.0],
        "start-y": [10.0, 150.0],
        "end-x": [20.0, 110.0],
        "end-y": [20.0, 160.0],
        "start-occurrence": [
            datetime(2023, 1, 1, 10, 0, 0),
            datetime(2023, 1, 1, 10, 0, 0),
        ],
        "end-occurrence": [
            datetime(2023, 1, 1, 10, 0, 1),
            datetime(2023, 1, 1, 10, 0, 1),
        ],
    }
    segments_df = DataFrame(segments_data)

    # Define a line that intersects with the first segment
    line_id = "intersecting_line"
    start_x = 0.0
    start_y = 0.0
    end_x = 30.0
    end_y = 30.0

    # Find intersections
    result = find_line_intersections(
        segments_df, line_id, start_x, start_y, end_x, end_y
    )

    # Check that the first segment intersects
    assert result.iloc[0]["intersects"]
    assert result.iloc[0]["intersection_x"] == approx(15.0)
    assert result.iloc[0]["intersection_y"] == approx(15.0)
    assert result.iloc[0]["intersection_line_id"] == line_id

    # Check that the second segment doesn't intersect
    assert not result.iloc[1]["intersects"]
    assert pd.isna(result.iloc[1]["intersection_x"])
    assert pd.isna(result.iloc[1]["intersection_y"])
    assert pd.isna(result.iloc[1]["intersection_line_id"])


def test_find_line_intersections_multiple_intersections() -> None:
    """Test with multiple segments intersecting with the line."""
    # Create test data
    segments_data = {
        "track-id": ["track1", "track2", "track3"],
        "start-x": [10.0, 100.0, 30.0],
        "start-y": [10.0, 10.0, 30.0],
        "end-x": [20.0, 110.0, 40.0],
        "end-y": [20.0, 20.0, 40.0],
        "start-occurrence": [
            datetime(2023, 1, 1, 10, 0, 0),
            datetime(2023, 1, 1, 10, 0, 0),
            datetime(2023, 1, 1, 10, 0, 0),
        ],
        "end-occurrence": [
            datetime(2023, 1, 1, 10, 0, 1),
            datetime(2023, 1, 1, 10, 0, 1),
            datetime(2023, 1, 1, 10, 0, 1),
        ],
    }
    segments_df = DataFrame(segments_data)

    # Define a line that intersects with the first and third segments
    line_id = "multiple_intersecting_line"
    start_x = 0.0
    start_y = 0.0
    end_x = 50.0
    end_y = 50.0

    # Find intersections
    result = find_line_intersections(
        segments_df, line_id, start_x, start_y, end_x, end_y
    )

    # Check that the first and third segments intersect
    assert result.iloc[0]["intersects"]
    assert result.iloc[0]["intersection_x"] == approx(15.0)
    assert result.iloc[0]["intersection_y"] == approx(15.0)
    assert result.iloc[0]["intersection_line_id"] == line_id

    assert not result.iloc[1]["intersects"]

    assert result.iloc[2]["intersects"]
    assert result.iloc[2]["intersection_x"] == approx(35.0)
    assert result.iloc[2]["intersection_y"] == approx(35.0)
    assert result.iloc[2]["intersection_line_id"] == line_id

    # Check the count of intersecting segments
    assert result["intersects"].sum() == 2


def test_create_track_segments_empty_df() -> None:
    """Test that an empty DataFrame returns an empty DataFrame."""
    df = DataFrame()
    result = create_track_segments(df)
    assert result.empty


def test_create_track_segments_single_track() -> None:
    """Test creating segments from a single track with multiple points."""
    # Create test data
    data = {
        "track-id": ["track1", "track1", "track1"],
        "occurrence": [
            datetime(2023, 1, 1, 10, 0, 0),
            datetime(2023, 1, 1, 10, 0, 1),
            datetime(2023, 1, 1, 10, 0, 2),
        ],
        "x": [10.0, 20.0, 30.0],
        "y": [15.0, 25.0, 35.0],
    }
    df = DataFrame(data)

    # Create segments
    result = create_track_segments(df)

    # Check result
    assert len(result) == 2  # Should have 2 segments for 3 points

    # Check first segment
    assert result.iloc[0]["track-id"] == "track1"
    assert result.iloc[0]["start-occurrence"] == datetime(2023, 1, 1, 10, 0, 0)
    assert result.iloc[0]["end-occurrence"] == datetime(2023, 1, 1, 10, 0, 1)
    assert result.iloc[0]["start-x"] == 10.0
    assert result.iloc[0]["start-y"] == 15.0
    assert result.iloc[0]["end-x"] == 20.0
    assert result.iloc[0]["end-y"] == 25.0

    # Check second segment
    assert result.iloc[1]["track-id"] == "track1"
    assert result.iloc[1]["start-occurrence"] == datetime(2023, 1, 1, 10, 0, 1)
    assert result.iloc[1]["end-occurrence"] == datetime(2023, 1, 1, 10, 0, 2)
    assert result.iloc[1]["start-x"] == 20.0
    assert result.iloc[1]["start-y"] == 25.0
    assert result.iloc[1]["end-x"] == 30.0
    assert result.iloc[1]["end-y"] == 35.0


def test_create_track_segments_multiple_tracks() -> None:
    """Test creating segments from multiple tracks."""
    # Create test data
    data = {
        "track-id": ["track1", "track1", "track2", "track2"],
        "occurrence": [
            datetime(2023, 1, 1, 10, 0, 0),
            datetime(2023, 1, 1, 10, 0, 1),
            datetime(2023, 1, 1, 10, 0, 0),
            datetime(2023, 1, 1, 10, 0, 1),
        ],
        "x": [10.0, 20.0, 100.0, 110.0],
        "y": [15.0, 25.0, 150.0, 160.0],
    }
    df = DataFrame(data)

    # Create segments
    result = create_track_segments(df)

    # Check result
    assert len(result) == 2  # Should have 2 segments (1 for each track)

    # Check track1 segment
    track1_segment = result[result["track-id"] == "track1"].iloc[0]
    assert track1_segment["start-occurrence"] == datetime(2023, 1, 1, 10, 0, 0)
    assert track1_segment["end-occurrence"] == datetime(2023, 1, 1, 10, 0, 1)
    assert track1_segment["start-x"] == 10.0
    assert track1_segment["start-y"] == 15.0
    assert track1_segment["end-x"] == 20.0
    assert track1_segment["end-y"] == 25.0

    # Check track2 segment
    track2_segment = result[result["track-id"] == "track2"].iloc[0]
    assert track2_segment["start-occurrence"] == datetime(2023, 1, 1, 10, 0, 0)
    assert track2_segment["end-occurrence"] == datetime(2023, 1, 1, 10, 0, 1)
    assert track2_segment["start-x"] == 100.0
    assert track2_segment["start-y"] == 150.0
    assert track2_segment["end-x"] == 110.0
    assert track2_segment["end-y"] == 160.0
