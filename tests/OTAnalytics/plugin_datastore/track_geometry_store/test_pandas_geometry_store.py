from datetime import datetime

import pandas as pd
from pandas import DataFrame
from pytest import approx

from OTAnalytics.plugin_datastore.track_geometry_store.pandas_geometry_store import (
    END_OCCURRENCE,
    END_X,
    END_Y,
    INTERSECTION_LINE_ID,
    INTERSECTION_X,
    INTERSECTION_Y,
    INTERSECTS,
    OCCURRENCE,
    START_OCCURRENCE,
    START_X,
    START_Y,
    TRACK_ID,
    X,
    Y,
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
        TRACK_ID: ["track1", "track2"],
        START_X: [10.0, 100.0],
        START_Y: [15.0, 150.0],
        END_X: [20.0, 110.0],
        END_Y: [25.0, 160.0],
        START_OCCURRENCE: [
            datetime(2023, 1, 1, 10, 0, 0),
            datetime(2023, 1, 1, 10, 0, 0),
        ],
        END_OCCURRENCE: [
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
    assert not result[INTERSECTS].any()
    assert (result[INTERSECTION_X].isna()).all()
    assert (result[INTERSECTION_Y].isna()).all()
    assert (result[INTERSECTION_LINE_ID].isna()).all()


def test_find_line_intersections_with_intersections() -> None:
    """Test with segments that intersect with the line."""
    # Create test data
    segments_data = {
        TRACK_ID: ["track1", "track2"],
        START_X: [10.0, 100.0],
        START_Y: [10.0, 150.0],
        END_X: [20.0, 110.0],
        END_Y: [20.0, 160.0],
        START_OCCURRENCE: [
            datetime(2023, 1, 1, 10, 0, 0),
            datetime(2023, 1, 1, 10, 0, 0),
        ],
        END_OCCURRENCE: [
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
    assert result.iloc[0][INTERSECTS]
    assert result.iloc[0][INTERSECTION_X] == approx(15.0)
    assert result.iloc[0][INTERSECTION_Y] == approx(15.0)
    assert result.iloc[0][INTERSECTION_LINE_ID] == line_id

    # Check that the second segment doesn't intersect
    assert not result.iloc[1][INTERSECTS]
    assert pd.isna(result.iloc[1][INTERSECTION_X])
    assert pd.isna(result.iloc[1][INTERSECTION_Y])
    assert pd.isna(result.iloc[1][INTERSECTION_LINE_ID])


def test_find_line_intersections_multiple_intersections() -> None:
    """Test with multiple segments intersecting with the line."""
    # Create test data
    segments_data = {
        TRACK_ID: ["track1", "track2", "track3"],
        START_X: [10.0, 100.0, 30.0],
        START_Y: [10.0, 10.0, 30.0],
        END_X: [20.0, 110.0, 40.0],
        END_Y: [20.0, 20.0, 40.0],
        START_OCCURRENCE: [
            datetime(2023, 1, 1, 10, 0, 0),
            datetime(2023, 1, 1, 10, 0, 0),
            datetime(2023, 1, 1, 10, 0, 0),
        ],
        END_OCCURRENCE: [
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
    assert result.iloc[0][INTERSECTS]
    assert result.iloc[0][INTERSECTION_X] == approx(15.0)
    assert result.iloc[0][INTERSECTION_Y] == approx(15.0)
    assert result.iloc[0][INTERSECTION_LINE_ID] == line_id

    assert not result.iloc[1][INTERSECTS]

    assert result.iloc[2][INTERSECTS]
    assert result.iloc[2][INTERSECTION_X] == approx(35.0)
    assert result.iloc[2][INTERSECTION_Y] == approx(35.0)
    assert result.iloc[2][INTERSECTION_LINE_ID] == line_id

    # Check the count of intersecting segments
    assert result[INTERSECTS].sum() == 2


def test_create_track_segments_empty_df() -> None:
    """Test that an empty DataFrame returns an empty DataFrame."""
    df = DataFrame()
    result = create_track_segments(df)
    assert result.empty


def test_create_track_segments_single_track() -> None:
    """Test creating segments from a single track with multiple points."""
    # Create test data
    data = {
        TRACK_ID: ["track1", "track1", "track1"],
        OCCURRENCE: [
            datetime(2023, 1, 1, 10, 0, 0),
            datetime(2023, 1, 1, 10, 0, 1),
            datetime(2023, 1, 1, 10, 0, 2),
        ],
        X: [10.0, 20.0, 30.0],
        Y: [15.0, 25.0, 35.0],
    }
    df = DataFrame(data)

    # Create segments
    result = create_track_segments(df)

    # Check result
    assert len(result) == 2  # Should have 2 segments for 3 points

    # Check first segment
    assert result.iloc[0][TRACK_ID] == "track1"
    assert result.iloc[0][START_OCCURRENCE] == datetime(2023, 1, 1, 10, 0, 0)
    assert result.iloc[0][END_OCCURRENCE] == datetime(2023, 1, 1, 10, 0, 1)
    assert result.iloc[0][START_X] == 10.0
    assert result.iloc[0][START_Y] == 15.0
    assert result.iloc[0][END_X] == 20.0
    assert result.iloc[0][END_Y] == 25.0

    # Check second segment
    assert result.iloc[1][TRACK_ID] == "track1"
    assert result.iloc[1][START_OCCURRENCE] == datetime(2023, 1, 1, 10, 0, 1)
    assert result.iloc[1][END_OCCURRENCE] == datetime(2023, 1, 1, 10, 0, 2)
    assert result.iloc[1][START_X] == 20.0
    assert result.iloc[1][START_Y] == 25.0
    assert result.iloc[1][END_X] == 30.0
    assert result.iloc[1][END_Y] == 35.0


def test_create_track_segments_multiple_tracks() -> None:
    """Test creating segments from multiple tracks."""
    # Create test data
    data = {
        TRACK_ID: ["track1", "track1", "track2", "track2"],
        OCCURRENCE: [
            datetime(2023, 1, 1, 10, 0, 0),
            datetime(2023, 1, 1, 10, 0, 1),
            datetime(2023, 1, 1, 10, 0, 0),
            datetime(2023, 1, 1, 10, 0, 1),
        ],
        X: [10.0, 20.0, 100.0, 110.0],
        Y: [15.0, 25.0, 150.0, 160.0],
    }
    df = DataFrame(data)

    # Create segments
    result = create_track_segments(df)

    # Check result
    assert len(result) == 2  # Should have 2 segments (1 for each track)

    # Check track1 segment
    track1_segment = result[result[TRACK_ID] == "track1"].iloc[0]
    assert track1_segment[START_OCCURRENCE] == datetime(2023, 1, 1, 10, 0, 0)
    assert track1_segment[END_OCCURRENCE] == datetime(2023, 1, 1, 10, 0, 1)
    assert track1_segment[START_X] == 10.0
    assert track1_segment[START_Y] == 15.0
    assert track1_segment[END_X] == 20.0
    assert track1_segment[END_Y] == 25.0

    # Check track2 segment
    track2_segment = result[result[TRACK_ID] == "track2"].iloc[0]
    assert track2_segment[START_OCCURRENCE] == datetime(2023, 1, 1, 10, 0, 0)
    assert track2_segment[END_OCCURRENCE] == datetime(2023, 1, 1, 10, 0, 1)
    assert track2_segment[START_X] == 100.0
    assert track2_segment[START_Y] == 150.0
    assert track2_segment[END_X] == 110.0
    assert track2_segment[END_Y] == 160.0
