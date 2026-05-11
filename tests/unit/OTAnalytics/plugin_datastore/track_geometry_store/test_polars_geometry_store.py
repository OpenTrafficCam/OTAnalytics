from dataclasses import dataclass
from datetime import datetime
from unittest.mock import Mock

import polars
import pytest
from polars import DataFrame
from pytest import approx

from OTAnalytics.domain.geometry import Coordinate, RelativeOffsetCoordinate
from OTAnalytics.domain.section import LineSection, SectionId, SectionType
from OTAnalytics.domain.track import FRAME, TRACK_CLASSIFICATION, VIDEO_NAME, H, W
from OTAnalytics.domain.track_dataset.track_dataset import END_FRAME, END_VIDEO_NAME
from OTAnalytics.domain.types import EventType
from OTAnalytics.plugin_datastore.track_geometry_store.polars_geometry_store import (
    END_H,
    END_OCCURRENCE,
    END_W,
    END_X,
    END_Y,
    INTERSECTION_LINE_ID,
    INTERSECTION_X,
    INTERSECTION_Y,
    INTERSECTS,
    INTERSECTS_POLYGON,
    OCCURRENCE,
    ROW_ID,
    START_H,
    START_OCCURRENCE,
    START_W,
    START_X,
    START_Y,
    TRACK_ID,
    PolarsTrackGeometryDataset,
    Polygon,
    X,
    Y,
    check_polygon_intersections,
    create_track_segments,
    find_line_intersections,
)


def test_find_line_intersections_empty_df() -> None:
    """Test that an empty DataFrame returns an empty DataFrame."""
    df = DataFrame()
    result = find_line_intersections(
        df, "line1", 0.0, 0.0, 10.0, 10.0, RelativeOffsetCoordinate(0.0, 0.0)
    )
    assert result.is_empty()


def test_find_line_intersections_no_intersections() -> None:
    """Test with segments that don't intersect with the line."""
    # Create test data
    segments_data = {
        ROW_ID: [1, 2],
        TRACK_ID: ["track1", "track2"],
        TRACK_CLASSIFICATION: ["car", "car"],
        END_VIDEO_NAME: ["video1", "video1"],
        END_FRAME: [2, 3],
        START_X: [10.0, 100.0],
        START_Y: [15.0, 150.0],
        END_X: [20.0, 110.0],
        END_Y: [25.0, 160.0],
        START_W: [0.0, 0.0],
        START_H: [0.0, 0.0],
        END_W: [0.0, 0.0],
        END_H: [0.0, 0.0],
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
        segments_df,
        line_id,
        start_x,
        start_y,
        end_x,
        end_y,
        RelativeOffsetCoordinate(0.0, 0.0),
    )

    # Check that no segments intersect
    assert not result.get_column(INTERSECTS).any()
    assert (result.get_column(INTERSECTION_X).is_nan()).all()
    assert (result.get_column(INTERSECTION_Y).is_nan()).all()
    assert (result.get_column(INTERSECTION_LINE_ID).is_null()).all()


@pytest.mark.parametrize(
    "offset, expected_intersection",
    [
        (RelativeOffsetCoordinate(0.0, 0.0), 30.0),
        (RelativeOffsetCoordinate(0.5, 0.0), 33.0),
        (RelativeOffsetCoordinate(1.0, 0.0), 36.0),
        (RelativeOffsetCoordinate(0.0, 0.5), 33.0),
        (RelativeOffsetCoordinate(0.5, 0.5), 36.0),
        (RelativeOffsetCoordinate(1.0, 0.5), 39.0),
        (RelativeOffsetCoordinate(0.0, 1.0), 36.0),
        (RelativeOffsetCoordinate(0.5, 1.0), 39.0),
        (RelativeOffsetCoordinate(1.0, 1.0), 42.0),
    ],
)
def test_find_line_intersections_with_intersections(
    offset: RelativeOffsetCoordinate, expected_intersection: float
) -> None:
    """Test with segments that intersect with the line."""
    # Create test data
    segments_data = {
        ROW_ID: [1, 2],
        TRACK_ID: ["track1", "track2"],
        TRACK_CLASSIFICATION: ["car", "car"],
        END_VIDEO_NAME: ["video1", "video1"],
        END_FRAME: [2, 3],
        START_X: [60.0, 100.0],
        START_Y: [0.0, 150.0],
        END_X: [0.0, 110.0],
        END_Y: [60.0, 160.0],
        START_W: [12.0, 12.0],
        START_H: [12.0, 12.0],
        END_W: [12.0, 12.0],
        END_H: [12.0, 12.0],
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
    end_x = 120.0
    end_y = 120.0

    # Find intersections
    result = find_line_intersections(
        segments_df, line_id, start_x, start_y, end_x, end_y, offset
    )

    # Check that the first segment intersects
    assert result.row(0, named=True)[INTERSECTS]
    assert result.row(0, named=True)[INTERSECTION_X] == approx(expected_intersection)
    assert result.row(0, named=True)[INTERSECTION_Y] == approx(expected_intersection)
    assert result.row(0, named=True)[INTERSECTION_LINE_ID] == line_id

    # Check that the second segment doesn't intersect
    assert not result.row(1, named=True)[INTERSECTS]
    assert (result.slice(1, 1).get_column(INTERSECTION_X).is_nan()).all()
    assert (result.slice(1, 1).get_column(INTERSECTION_Y).is_nan()).all()
    assert (result.slice(1, 1).get_column(INTERSECTION_LINE_ID).is_null()).all()


def test_find_line_intersections_multiple_intersections() -> None:
    """Test with multiple segments intersecting with the line."""
    # Create test data
    segments_data = {
        ROW_ID: [1, 2, 3],
        TRACK_ID: ["track1", "track2", "track3"],
        TRACK_CLASSIFICATION: ["car", "car", "car"],
        END_VIDEO_NAME: ["video1", "video1", "video1"],
        END_FRAME: [2, 3, 4],
        START_X: [20.0, 100.0, 30.0],
        START_Y: [10.0, 10.0, 40.0],
        END_X: [10.0, 110.0, 40.0],
        END_Y: [20.0, 20.0, 30.0],
        START_W: [0.0, 0.0, 0.0],
        START_H: [0.0, 0.0, 0.0],
        END_W: [0.0, 0.0, 0.0],
        END_H: [0.0, 0.0, 0.0],
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
        segments_df,
        line_id,
        start_x,
        start_y,
        end_x,
        end_y,
        RelativeOffsetCoordinate(0.0, 0.0),
    )

    # Check that the first and third segments intersect
    assert result.row(0, named=True)[INTERSECTS]
    assert result.row(0, named=True)[INTERSECTION_X] == approx(15.0)
    assert result.row(0, named=True)[INTERSECTION_Y] == approx(15.0)
    assert result.row(0, named=True)[INTERSECTION_LINE_ID] == line_id

    assert not result.row(1, named=True)[INTERSECTS]

    assert result.row(2, named=True)[INTERSECTS]
    assert result.row(2, named=True)[INTERSECTION_X] == approx(35.0)
    assert result.row(2, named=True)[INTERSECTION_Y] == approx(35.0)
    assert result.row(2, named=True)[INTERSECTION_LINE_ID] == line_id

    # Check the count of intersecting segments
    assert result[INTERSECTS].sum() == 2


def test_create_track_segments_empty_df() -> None:
    """Test that an empty DataFrame returns an empty DataFrame."""
    df = DataFrame()
    result = create_track_segments(df)
    assert result.is_empty()


def test_create_track_segments_single_track() -> None:
    """Test creating segments from a single track with multiple points."""
    # Create test data
    data = {
        ROW_ID: [1, 2, 3],
        TRACK_ID: ["track1", "track1", "track1"],
        TRACK_CLASSIFICATION: ["car", "car", "car"],
        OCCURRENCE: [
            datetime(2023, 1, 1, 10, 0, 0),
            datetime(2023, 1, 1, 10, 0, 1),
            datetime(2023, 1, 1, 10, 0, 2),
        ],
        FRAME: [1, 2, 3],
        VIDEO_NAME: ["video1", "video1", "video1"],
        X: [10.0, 20.0, 30.0],
        Y: [15.0, 25.0, 35.0],
        W: [10.0, 20.0, 30.0],
        H: [8.0, 16.0, 24.0],
    }
    df = DataFrame(data)

    # Create segments
    result = create_track_segments(df)

    # Check result
    assert len(result) == 2  # Should have 2 segments for 3 points

    # Check first segment
    assert result.row(0, named=True)[TRACK_ID] == "track1"
    assert result.row(0, named=True)[START_OCCURRENCE] == datetime(2023, 1, 1, 10, 0, 0)
    assert result.row(0, named=True)[END_OCCURRENCE] == datetime(2023, 1, 1, 10, 0, 1)
    assert result.row(0, named=True)[START_X] == 10.0
    assert result.row(0, named=True)[START_Y] == 15.0
    assert result.row(0, named=True)[START_W] == 10.0
    assert result.row(0, named=True)[START_H] == 8.0
    assert result.row(0, named=True)[END_X] == 20.0
    assert result.row(0, named=True)[END_Y] == 25.0
    assert result.row(0, named=True)[END_W] == 20.0
    assert result.row(0, named=True)[END_H] == 16.0

    # Check second segment
    assert result.row(1, named=True)[TRACK_ID] == "track1"
    assert result.row(1, named=True)[START_OCCURRENCE] == datetime(2023, 1, 1, 10, 0, 1)
    assert result.row(1, named=True)[END_OCCURRENCE] == datetime(2023, 1, 1, 10, 0, 2)
    assert result.row(1, named=True)[START_X] == 20.0
    assert result.row(1, named=True)[START_Y] == 25.0
    assert result.row(1, named=True)[START_W] == 20.0
    assert result.row(1, named=True)[START_H] == 16.0
    assert result.row(1, named=True)[END_X] == 30.0
    assert result.row(1, named=True)[END_Y] == 35.0
    assert result.row(1, named=True)[END_W] == 30.0
    assert result.row(1, named=True)[END_H] == 24.0


def test_create_track_segments_multiple_tracks() -> None:
    """Test creating segments from multiple tracks."""
    # Create test data
    data = {
        ROW_ID: [1, 2, 3, 4],
        TRACK_ID: ["track1", "track1", "track2", "track2"],
        TRACK_CLASSIFICATION: ["car", "car", "car", "car"],
        OCCURRENCE: [
            datetime(2023, 1, 1, 10, 0, 0),
            datetime(2023, 1, 1, 10, 0, 1),
            datetime(2023, 1, 1, 10, 0, 0),
            datetime(2023, 1, 1, 10, 0, 1),
        ],
        FRAME: [1, 2, 1, 2],
        X: [10.0, 20.0, 100.0, 110.0],
        Y: [15.0, 25.0, 150.0, 160.0],
        W: [5.0, 10.0, 20.0, 40.0],
        H: [8.0, 16.0, 30.0, 60.0],
        VIDEO_NAME: ["video1", "video1", "video1", "video1"],
    }
    df = DataFrame(data)

    # Create segments
    result = create_track_segments(df)

    # Check result
    assert len(result) == 2  # Should have 2 segments (1 for each track)

    # Check track1 segment
    track1_segment = result.filter(polars.col(TRACK_ID) == "track1").row(0, named=True)
    assert track1_segment[START_OCCURRENCE] == datetime(2023, 1, 1, 10, 0, 0)
    assert track1_segment[END_OCCURRENCE] == datetime(2023, 1, 1, 10, 0, 1)
    assert track1_segment[START_X] == 10.0
    assert track1_segment[START_Y] == 15.0
    assert track1_segment[START_W] == 5.0
    assert track1_segment[START_H] == 8.0
    assert track1_segment[END_X] == 20.0
    assert track1_segment[END_Y] == 25.0
    assert track1_segment[END_W] == 10.0
    assert track1_segment[END_H] == 16.0

    # Check track2 segment
    track2_segment = result.filter(polars.col(TRACK_ID) == "track2").row(0, named=True)
    assert track2_segment[START_OCCURRENCE] == datetime(2023, 1, 1, 10, 0, 0)
    assert track2_segment[END_OCCURRENCE] == datetime(2023, 1, 1, 10, 0, 1)
    assert track2_segment[START_X] == 100.0
    assert track2_segment[START_Y] == 150.0
    assert track2_segment[START_W] == 20.0
    assert track2_segment[START_H] == 30.0
    assert track2_segment[END_X] == 110.0
    assert track2_segment[END_Y] == 160.0
    assert track2_segment[END_W] == 40.0
    assert track2_segment[END_H] == 60.0


def test_check_polygon_intersections_empty_df() -> None:
    """Test that an empty DataFrame returns an empty DataFrame."""
    df = DataFrame()
    polygon = Polygon(
        [
            Coordinate(0.0, 0.0),
            Coordinate(10.0, 0.0),
            Coordinate(10.0, 10.0),
            Coordinate(0.0, 10.0),
            Coordinate(0.0, 0.0),
        ]
    )
    result = check_polygon_intersections(
        df, polygon, RelativeOffsetCoordinate(0.0, 0.0)
    )
    assert result.is_empty()


def test_check_polygon_intersections_no_intersections() -> None:
    """Test with segments that don't intersect with the polygon."""
    # Create test data
    segments_data = {
        TRACK_ID: ["track1", "track2"],
        START_X: [20.0, 100.0],
        START_Y: [20.0, 150.0],
        END_X: [30.0, 110.0],
        END_Y: [30.0, 160.0],
        START_W: [0.0, 0.0],
        START_H: [0.0, 0.0],
        END_W: [0.0, 0.0],
        END_H: [0.0, 0.0],
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

    # Create a polygon that doesn't intersect with any segment
    polygon = Polygon(
        [
            Coordinate(0.0, 0.0),
            Coordinate(10.0, 0.0),
            Coordinate(10.0, 10.0),
            Coordinate(0.0, 10.0),
            Coordinate(0.0, 0.0),
        ]
    )

    # Check intersections
    result = check_polygon_intersections(
        segments_df, polygon, RelativeOffsetCoordinate(0.0, 0.0)
    )

    # Check that no segments intersect with the polygon
    assert not result[INTERSECTS_POLYGON].any()


def test_check_polygon_intersections_with_intersections() -> None:
    """Test with segments that intersect with the polygon."""
    # Create test data
    segments_data = {
        ROW_ID: [1, 2, 3],
        TRACK_ID: ["track1", "track2", "track3"],
        TRACK_CLASSIFICATION: ["car", "car", "car"],
        FRAME: [1, 2, 3],
        VIDEO_NAME: ["video1", "video1", "video1"],
        START_X: [5.0, 100.0, 0.0],
        START_Y: [5.0, 150.0, 5.0],
        END_X: [15.0, 110.0, 25.0],
        END_Y: [15.0, 160.0, 15.0],
        START_W: [0.0, 0.0, 0.0],
        START_H: [0.0, 0.0, 0.0],
        END_W: [0.0, 0.0, 0.0],
        END_H: [0.0, 0.0, 0.0],
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

    # Create a polygon that intersects with the first and third segments
    polygon = Polygon(
        [
            Coordinate(0.0, 0.0),
            Coordinate(10.0, 0.0),
            Coordinate(10.0, 10.0),
            Coordinate(0.0, 10.0),
            Coordinate(0.0, 0.0),
        ]
    )

    # Check intersections
    result = check_polygon_intersections(
        segments_df, polygon, RelativeOffsetCoordinate(0.0, 0.0)
    )

    # Check that the first and third segments intersect with the polygon
    assert result.row(0, named=True)[INTERSECTS_POLYGON]
    assert not result.row(1, named=True)[INTERSECTS_POLYGON]
    assert result.row(2, named=True)[INTERSECTS_POLYGON]

    # Check the count of intersecting segments
    assert result[INTERSECTS_POLYGON].sum() == 2


def _create_cutting_section(
    section_id: str, coordinates: list[tuple[float, float]]
) -> Mock:
    """Helper function to create a mock cutting section for testing."""
    section = Mock(spec=LineSection)
    section.get_coordinates.return_value = [
        Coordinate(coord[0], coord[1]) for coord in coordinates
    ]
    section.relative_offset_coordinates = {
        EventType.SECTION_ENTER: RelativeOffsetCoordinate(0.0, 0.0)
    }
    section.get_offset.return_value = RelativeOffsetCoordinate(0.0, 0.0)
    section.id = SectionId(section_id)
    section.get_type.return_value = SectionType.CUTTING
    return section


@dataclass
class TrackIdsAfterCutGiven:
    """Test data container for track_ids_after_cut tests."""

    dataset: PolarsTrackGeometryDataset
    section: Mock


def create_segments_dataframe(
    row_ids: list[int],
    track_ids: list[str],
    start_x: list[float],
    start_y: list[float],
    end_x: list[float],
    end_y: list[float],
    start_times: list[datetime],
    end_times: list[datetime],
) -> DataFrame:
    """Create a segments DataFrame with the given data."""
    num_segments = len(row_ids)
    return DataFrame(
        {
            ROW_ID: row_ids,
            TRACK_ID: track_ids,
            TRACK_CLASSIFICATION: ["car"] * num_segments,
            END_VIDEO_NAME: ["video1"] * num_segments,
            END_FRAME: list(range(2, num_segments + 2)),
            START_X: start_x,
            START_Y: start_y,
            END_X: end_x,
            END_Y: end_y,
            START_W: [0.0] * num_segments,
            START_H: [0.0] * num_segments,
            END_W: [0.0] * num_segments,
            END_H: [0.0] * num_segments,
            START_OCCURRENCE: start_times,
            END_OCCURRENCE: end_times,
        }
    )


def setup_track_ids_after_cut(
    segments_df: DataFrame | None,
    section_coordinates: list[tuple[float, float]],
    section_id: str = "cut1",
) -> TrackIdsAfterCutGiven:
    """Set up test data for track_ids_after_cut tests."""
    if segments_df is None:
        dataset = PolarsTrackGeometryDataset(RelativeOffsetCoordinate(0.0, 0.0))
    else:
        dataset = PolarsTrackGeometryDataset(
            RelativeOffsetCoordinate(0.0, 0.0), segments_df
        )
    section = _create_cutting_section(section_id, section_coordinates)
    return TrackIdsAfterCutGiven(dataset=dataset, section=section)


class TestTrackIdsAfterCut:
    """Tests for the track_ids_after_cut method of PolarsTrackGeometryDataset."""

    def test_single_detection_dataset(self) -> None:
        """
        Supporting test case for bug OP#9023
        """
        detections = DataFrame(
            {
                ROW_ID: [1],
                TRACK_CLASSIFICATION: ["car"],
                TRACK_ID: ["track1"],
                OCCURRENCE: [datetime(2023, 1, 1, 10, 0, 0)],
                X: [10.0],
                Y: [10.0],
                W: [10.0],
                H: [10.0],
                FRAME: [1],
                VIDEO_NAME: ["video_1.mp4"],
            }
        )
        segments_df = create_track_segments(detections)
        given = setup_track_ids_after_cut(
            segments_df=segments_df,
            section_coordinates=[(50.0, 0.0), (50.0, 100.0)],
        )

        # Empty dataset raises ColumnNotFoundError because the method tries to
        # select ROW_ID from an empty DataFrame without the required columns
        result = given.dataset.track_ids_after_cut(given.section)

        assert result.is_empty()

    def test_no_intersections(self) -> None:
        """Test with tracks that don't intersect with the cutting section."""
        segments_df = create_segments_dataframe(
            row_ids=[1, 2],
            track_ids=["track1", "track1"],
            start_x=[10.0, 20.0],
            start_y=[10.0, 10.0],
            end_x=[20.0, 30.0],
            end_y=[10.0, 10.0],
            start_times=[
                datetime(2023, 1, 1, 10, 0, 0),
                datetime(2023, 1, 1, 10, 0, 1),
            ],
            end_times=[
                datetime(2023, 1, 1, 10, 0, 1),
                datetime(2023, 1, 1, 10, 0, 2),
            ],
        )
        given = setup_track_ids_after_cut(
            segments_df=segments_df,
            section_coordinates=[(100.0, 0.0), (100.0, 100.0)],
        )

        result = given.dataset.track_ids_after_cut(given.section)

        # Method adds one extra row per track (for initial state with ROW_ID - 1)
        # So 2 segments + 1 initial row = 3 rows
        assert len(result) == 3
        # Track IDs should remain unchanged (no suffix added) since no intersection
        track_ids = result[TRACK_ID].unique().to_list()
        assert track_ids == ["track1"]

    def test_single_intersection(self) -> None:
        """Test with a single track that intersects the cutting section once."""
        segments_df = create_segments_dataframe(
            row_ids=[1, 2, 3],
            track_ids=["track1", "track1", "track1"],
            start_x=[10.0, 40.0, 60.0],
            start_y=[10.0, 10.0, 10.0],
            end_x=[40.0, 60.0, 80.0],
            end_y=[10.0, 10.0, 10.0],
            start_times=[
                datetime(2023, 1, 1, 10, 0, 0),
                datetime(2023, 1, 1, 10, 0, 1),
                datetime(2023, 1, 1, 10, 0, 2),
            ],
            end_times=[
                datetime(2023, 1, 1, 10, 0, 1),
                datetime(2023, 1, 1, 10, 0, 2),
                datetime(2023, 1, 1, 10, 0, 3),
            ],
        )
        given = setup_track_ids_after_cut(
            segments_df=segments_df,
            section_coordinates=[(50.0, 0.0), (50.0, 100.0)],
        )

        result = given.dataset.track_ids_after_cut(given.section)

        # Method adds one extra row per track (for initial state)
        # So 3 segments + 1 initial row = 4 rows
        assert len(result) == 4

        # Check that track IDs are modified after the cut
        # The result is sorted by TRACK_ID, ROW_ID, ORDER
        # For cut tracks, suffixes _0, _1 are added
        unique_track_ids = set(result[TRACK_ID].to_list())
        assert "track1_0" in unique_track_ids
        assert "track1_1" in unique_track_ids

    def test_multiple_tracks(self) -> None:
        """Test with multiple tracks where only some intersect the cutting section."""
        segments_df = create_segments_dataframe(
            row_ids=[1, 2, 3, 4],
            track_ids=["track1", "track1", "track2", "track2"],
            # track1 crosses the cutting line at x=50
            # track2 stays below x=50
            start_x=[10.0, 40.0, 10.0, 20.0],
            start_y=[10.0, 10.0, 50.0, 50.0],
            end_x=[40.0, 80.0, 20.0, 30.0],
            end_y=[10.0, 10.0, 50.0, 50.0],
            start_times=[
                datetime(2023, 1, 1, 10, 0, 0),
                datetime(2023, 1, 1, 10, 0, 1),
                datetime(2023, 1, 1, 10, 0, 0),
                datetime(2023, 1, 1, 10, 0, 1),
            ],
            end_times=[
                datetime(2023, 1, 1, 10, 0, 1),
                datetime(2023, 1, 1, 10, 0, 2),
                datetime(2023, 1, 1, 10, 0, 1),
                datetime(2023, 1, 1, 10, 0, 2),
            ],
        )
        given = setup_track_ids_after_cut(
            segments_df=segments_df,
            section_coordinates=[(50.0, 0.0), (50.0, 30.0)],
        )

        result = given.dataset.track_ids_after_cut(given.section)

        # Method adds one extra row per track (for initial state)
        # So 4 segments + 2 initial rows = 6 rows
        assert len(result) == 6

        # Check results
        unique_track_ids = set(result[TRACK_ID].to_list())
        # track1 should be cut (track1_0 and track1_1)
        assert "track1_0" in unique_track_ids
        assert "track1_1" in unique_track_ids
        # track2 should remain unchanged (no suffix)
        assert "track2" in unique_track_ids

    def test_multiple_intersections(self) -> None:
        """Test with a track that intersects the cutting section multiple times."""
        segments_df = create_segments_dataframe(
            row_ids=[1, 2, 3, 4],
            track_ids=["track1", "track1", "track1", "track1"],
            # Track goes: 10->60 (crosses at 50), 60->40 (crosses at 50), 40->30, 30->20
            start_x=[10.0, 60.0, 40.0, 30.0],
            start_y=[10.0, 10.0, 10.0, 10.0],
            end_x=[60.0, 40.0, 30.0, 20.0],
            end_y=[10.0, 10.0, 10.0, 10.0],
            start_times=[
                datetime(2023, 1, 1, 10, 0, 0),
                datetime(2023, 1, 1, 10, 0, 1),
                datetime(2023, 1, 1, 10, 0, 2),
                datetime(2023, 1, 1, 10, 0, 3),
            ],
            end_times=[
                datetime(2023, 1, 1, 10, 0, 1),
                datetime(2023, 1, 1, 10, 0, 2),
                datetime(2023, 1, 1, 10, 0, 3),
                datetime(2023, 1, 1, 10, 0, 4),
            ],
        )
        given = setup_track_ids_after_cut(
            segments_df=segments_df,
            section_coordinates=[(50.0, 0.0), (50.0, 100.0)],
        )

        result = given.dataset.track_ids_after_cut(given.section)

        # Method adds one extra row per track (for initial state)
        # So 4 segments + 1 initial row = 5 rows
        assert len(result) == 5

        # Check results - track should be split into 3 parts
        unique_track_ids = set(result[TRACK_ID].to_list())
        # First segment crosses -> track1_0 before, track1_1 after
        # Second segment crosses -> track1_2 after
        assert "track1_0" in unique_track_ids
        assert "track1_1" in unique_track_ids
        assert "track1_2" in unique_track_ids
