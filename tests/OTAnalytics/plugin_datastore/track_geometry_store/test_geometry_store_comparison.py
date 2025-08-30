"""
Test comparison between pandas and polars geometry store implementations.

This module ensures that both pandas and polars implementations produce
identical results for all operations.
"""

from datetime import datetime
from typing import Any, Union

import polars as pl
import pytest
from pandas import DataFrame as PandasDataFrame
from pandas.testing import assert_frame_equal
from pytest import approx

from OTAnalytics.domain.geometry import Coordinate, RelativeOffsetCoordinate
from OTAnalytics.domain.track import H, W
from OTAnalytics.plugin_datastore.track_geometry_store.pandas_geometry_store import (
    END_H,
    END_OCCURRENCE,
    END_W,
    END_X,
    END_Y,
    INTERSECTION_X,
    INTERSECTS,
    OCCURRENCE,
    START_H,
    START_OCCURRENCE,
    START_W,
    START_X,
    START_Y,
    TRACK_ID,
    PandasTrackGeometryDataset,
)
from OTAnalytics.plugin_datastore.track_geometry_store.pandas_geometry_store import (
    Polygon as PandasPolygon,
)
from OTAnalytics.plugin_datastore.track_geometry_store.pandas_geometry_store import X, Y
from OTAnalytics.plugin_datastore.track_geometry_store.pandas_geometry_store import (
    check_polygon_intersections as pandas_check_polygon_intersections,
)
from OTAnalytics.plugin_datastore.track_geometry_store.pandas_geometry_store import (
    create_track_segments as pandas_create_track_segments,
)
from OTAnalytics.plugin_datastore.track_geometry_store.pandas_geometry_store import (
    find_line_intersections as pandas_find_line_intersections,
)
from OTAnalytics.plugin_datastore.track_geometry_store.polars_geometry_store import (
    INTERSECTION_Y,
    ROW_ID,
    PolarsTrackGeometryDataset,
)
from OTAnalytics.plugin_datastore.track_geometry_store.polars_geometry_store import (
    Polygon as PolarsPolygon,
)
from OTAnalytics.plugin_datastore.track_geometry_store.polars_geometry_store import (
    check_polygon_intersections as polars_check_polygon_intersections,
)
from OTAnalytics.plugin_datastore.track_geometry_store.polars_geometry_store import (
    create_track_segments as polars_create_track_segments,
)
from OTAnalytics.plugin_datastore.track_geometry_store.polars_geometry_store import (
    find_line_intersections as polars_find_line_intersections,
)


# Test data fixtures
@pytest.fixture
def sample_track_data() -> dict[str, list[Any]]:
    """Sample track data for testing."""
    return {
        TRACK_ID: ["track1", "track1", "track2", "track2"],
        OCCURRENCE: [
            datetime(2023, 1, 1, 10, 0, 0),
            datetime(2023, 1, 1, 10, 0, 1),
            datetime(2023, 1, 1, 10, 0, 0),
            datetime(2023, 1, 1, 10, 0, 1),
        ],
        X: [0.0, 10.0, 20.0, 30.0],
        Y: [0.0, 10.0, 20.0, 30.0],
        W: [5.0, 5.0, 5.0, 5.0],
        H: [5.0, 5.0, 5.0, 5.0],
    }


@pytest.fixture
def sample_segments_data() -> dict[str, list[Any]]:
    """Sample segments data for testing."""
    return {
        TRACK_ID: ["track1", "track2"],
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


def dataframes_equal(
    df1: Union[PandasDataFrame, pl.DataFrame], df2: Union[PandasDataFrame, pl.DataFrame]
) -> bool:
    """Compare two dataframes for equality, handling pandas and polars."""
    # Convert both to pandas for comparison
    if isinstance(df1, pl.DataFrame):
        df1 = df1.to_pandas()
    if isinstance(df2, pl.DataFrame):
        df2 = df2.drop(ROW_ID, strict=False).to_pandas()

    # Handle empty dataframes
    if df1.empty and df2.empty:
        return True
    if df1.empty or df2.empty:
        return False

    # Sort by common columns for consistent comparison
    sort_cols = []
    if TRACK_ID in df1.columns:
        sort_cols.append(TRACK_ID)
    if START_OCCURRENCE in df1.columns:
        sort_cols.append(START_OCCURRENCE)
    elif OCCURRENCE in df1.columns:
        sort_cols.append(OCCURRENCE)

    if sort_cols:
        df1 = df1.sort_values(sort_cols).reset_index(drop=True)
        df2 = df2.sort_values(sort_cols).reset_index(drop=True)

    # Compare using pandas equals with appropriate tolerance for floats
    try:
        assert_frame_equal(df1, df2)
        return True
    except Exception:
        try:
            assert_frame_equal(df1.round(10), df2.round(10))
            return True
        except Exception:
            # Fallback to manual comparison
            if set(df1.columns) != set(df2.columns):
                return False
            if len(df1) != len(df2):
                return False

            for col in df1.columns:
                if df1[col].dtype == "object" or df2[col].dtype == "object":
                    if not df1[col].equals(df2[col]):
                        return False
                else:
                    try:
                        if not (abs(df1[col] - df2[col]) < 1e-10).all():
                            return False
                    except Exception:
                        if not df1[col].equals(df2[col]):
                            return False
        return True


def prepare_polars_data_frame(
    data: dict[str, list[Any]],
) -> pl.DataFrame:
    df = pl.DataFrame(data).with_row_index(ROW_ID)
    if OCCURRENCE in df.columns:
        return df.with_columns(pl.col(OCCURRENCE).dt.cast_time_unit("ns"))
    else:
        return df.with_columns(
            pl.col(START_OCCURRENCE).dt.cast_time_unit("ns")
        ).with_columns(pl.col(END_OCCURRENCE).dt.cast_time_unit("ns"))


def prepare_polars_for_assert(
    df: pl.DataFrame,
) -> pl.DataFrame:
    return df.drop(ROW_ID, strict=False)


def prepare_pandas_for_assert(
    df: PandasDataFrame,
) -> PandasDataFrame:
    for column in [INTERSECTION_X, INTERSECTION_Y]:
        if column in df.columns:
            df[column] = df[column].astype(float)
    return df


class TestCreateTrackSegments:
    """Test create_track_segments function for both implementations."""

    def test_create_track_segments_empty_df(self) -> None:
        """Test that empty DataFrames return empty results."""
        pandas_df = PandasDataFrame()
        polars_df = pl.DataFrame()

        pandas_result = pandas_create_track_segments(pandas_df)
        polars_result = polars_create_track_segments(polars_df)

        assert pandas_result.empty
        assert polars_result.is_empty()

    def test_create_track_segments_single_track(
        self, sample_track_data: dict[str, list[Any]]
    ) -> None:
        """Test segment creation with single track."""
        # Filter for single track
        single_track_data = {k: [v[0], v[1]] for k, v in sample_track_data.items()}

        pandas_df = PandasDataFrame(single_track_data)
        polars_df = prepare_polars_data_frame(single_track_data)

        pandas_result = pandas_create_track_segments(pandas_df)
        polars_result = prepare_polars_for_assert(
            polars_create_track_segments(polars_df)
        )

        # Both should produce one segment
        assert len(pandas_result) == 1
        assert len(polars_result) == 1

        # Results should be equivalent
        assert dataframes_equal(pandas_result, polars_result)

    def test_create_track_segments_multiple_tracks(
        self, sample_track_data: dict[str, list[Any]]
    ) -> None:
        """Test segment creation with multiple tracks."""
        pandas_df = PandasDataFrame(sample_track_data)
        polars_df = prepare_polars_data_frame(sample_track_data)

        pandas_result = pandas_create_track_segments(pandas_df)
        polars_result = polars_create_track_segments(polars_df)

        # Both should produce two segments (one per track)
        assert len(pandas_result) == 2
        assert len(polars_result) == 2

        # Results should be equivalent
        assert dataframes_equal(pandas_result, polars_result)


class TestFindLineIntersections:
    """Test find_line_intersections function for both implementations."""

    def test_find_line_intersections_empty_df(self) -> None:
        """Test with empty DataFrames."""
        pandas_df = PandasDataFrame()
        polars_df = pl.DataFrame()
        offset = RelativeOffsetCoordinate(0.0, 0.0)

        pandas_result = pandas_find_line_intersections(
            pandas_df, "line1", 0.0, 0.0, 10.0, 10.0, offset
        )
        polars_result = polars_find_line_intersections(
            polars_df, "line1", 0.0, 0.0, 10.0, 10.0, offset
        )

        assert pandas_result.empty
        assert polars_result.is_empty()

    def test_find_line_intersections_no_intersections(
        self, sample_segments_data: dict[str, list[Any]]
    ) -> None:
        """Test with segments that don't intersect."""
        pandas_df = PandasDataFrame(sample_segments_data)
        polars_df = prepare_polars_data_frame(sample_segments_data)
        offset = RelativeOffsetCoordinate(0.0, 0.0)

        # Line that doesn't intersect
        line_id = "non_intersecting_line"
        start_x, start_y = 0.0, 100.0
        end_x, end_y = 5.0, 105.0

        pandas_result = pandas_find_line_intersections(
            pandas_df, line_id, start_x, start_y, end_x, end_y, offset
        )
        polars_result = polars_find_line_intersections(
            polars_df, line_id, start_x, start_y, end_x, end_y, offset
        )

        # Both should have no intersections
        assert not pandas_result[INTERSECTS].any()
        assert not polars_result[INTERSECTS].any()

        # Results should be equivalent
        assert dataframes_equal(
            prepare_pandas_for_assert(pandas_result),
            prepare_polars_for_assert(polars_result),
        )

    @pytest.mark.parametrize(
        "offset, expected_intersection",
        [
            (RelativeOffsetCoordinate(0.0, 0.0), 30.0),
            (RelativeOffsetCoordinate(0.5, 0.0), 33.0),
            (RelativeOffsetCoordinate(1.0, 0.0), 36.0),
        ],
    )
    def test_find_line_intersections_with_intersections(
        self,
        sample_segments_data: dict[str, list[Any]],
        offset: RelativeOffsetCoordinate,
        expected_intersection: float,
    ) -> None:
        """Test with segments that intersect with the line."""
        pandas_df = PandasDataFrame(sample_segments_data)
        polars_df = prepare_polars_data_frame(sample_segments_data)

        # Line that intersects with first segment
        line_id = "intersecting_line"
        start_x, start_y = 0.0, 0.0
        end_x, end_y = 120.0, 120.0

        pandas_result = pandas_find_line_intersections(
            pandas_df, line_id, start_x, start_y, end_x, end_y, offset
        )
        polars_result = polars_find_line_intersections(
            polars_df, line_id, start_x, start_y, end_x, end_y, offset
        )

        # Both should have same intersection pattern
        assert dataframes_equal(
            prepare_pandas_for_assert(pandas_result),
            prepare_polars_for_assert(polars_result),
        )

        # Check specific intersection values
        pandas_intersecting = pandas_result[pandas_result[INTERSECTS]]
        polars_intersecting = polars_result.to_pandas()[
            polars_result.to_pandas()[INTERSECTS]
        ]

        if len(pandas_intersecting) > 0:
            assert pandas_intersecting.iloc[0][INTERSECTION_X] == approx(
                expected_intersection
            )
            assert polars_intersecting.iloc[0][INTERSECTION_X] == approx(
                expected_intersection
            )


class TestCheckPolygonIntersections:
    """Test check_polygon_intersections function for both implementations."""

    def test_check_polygon_intersections_empty_df(self) -> None:
        """Test with empty DataFrames."""
        pandas_df = PandasDataFrame()
        polars_df = pl.DataFrame()
        polygon_coords = [Coordinate(0, 0), Coordinate(10, 0), Coordinate(10, 10)]
        pandas_polygon = PandasPolygon(polygon_coords)
        polars_polygon = PolarsPolygon(polygon_coords)
        offset = RelativeOffsetCoordinate(0.0, 0.0)

        pandas_result = pandas_check_polygon_intersections(
            pandas_df, pandas_polygon, offset
        )
        polars_result = polars_check_polygon_intersections(
            polars_df, polars_polygon, offset
        )

        assert pandas_result.empty
        assert polars_result.is_empty()

    def test_check_polygon_intersections_with_intersections(
        self, sample_segments_data: dict[str, list[Any]]
    ) -> None:
        """Test polygon intersections."""
        pandas_df = PandasDataFrame(sample_segments_data)
        polars_df = prepare_polars_data_frame(sample_segments_data)

        # Create a polygon that should intersect with some segments
        polygon_coords = [
            Coordinate(0, 0),
            Coordinate(70, 0),
            Coordinate(70, 70),
            Coordinate(0, 70),
        ]
        pandas_polygon = PandasPolygon(polygon_coords)
        polars_polygon = PolarsPolygon(polygon_coords)
        offset = RelativeOffsetCoordinate(0.0, 0.0)

        pandas_result = pandas_check_polygon_intersections(
            pandas_df, pandas_polygon, offset
        )
        polars_result = polars_check_polygon_intersections(
            polars_df, polars_polygon, offset
        )

        # Results should be equivalent
        assert dataframes_equal(
            prepare_pandas_for_assert(pandas_result),
            prepare_polars_for_assert(polars_result),
        )


class TestTrackGeometryDataset:
    """Test TrackGeometryDataset implementations."""

    def test_dataset_initialization(self) -> None:
        """Test dataset initialization."""
        offset = RelativeOffsetCoordinate(0.0, 0.0)

        pandas_dataset = PandasTrackGeometryDataset(offset)
        polars_dataset = PolarsTrackGeometryDataset(offset)

        assert pandas_dataset.empty
        assert polars_dataset.empty
        assert pandas_dataset.offset == polars_dataset.offset

    def test_dataset_track_ids(
        self, sample_segments_data: dict[str, list[Any]]
    ) -> None:
        """Test track_ids property."""
        offset = RelativeOffsetCoordinate(0.0, 0.0)
        pandas_df = PandasDataFrame(sample_segments_data)
        polars_df = pl.DataFrame(sample_segments_data)

        pandas_dataset = PandasTrackGeometryDataset(offset, pandas_df)
        polars_dataset = PolarsTrackGeometryDataset(offset, polars_df)

        assert pandas_dataset.track_ids == polars_dataset.track_ids

    def test_dataset_get_for(self, sample_segments_data: dict[str, list[Any]]) -> None:
        """Test get_for method."""
        offset = RelativeOffsetCoordinate(0.0, 0.0)
        pandas_df = PandasDataFrame(sample_segments_data)
        polars_df = pl.DataFrame(sample_segments_data)

        pandas_dataset = PandasTrackGeometryDataset(offset, pandas_df)
        polars_dataset = PolarsTrackGeometryDataset(offset, polars_df)

        track_ids = ["track1"]
        pandas_result = pandas_dataset.get_for(track_ids)
        polars_result = polars_dataset.get_for(track_ids)

        assert pandas_result.track_ids == polars_result.track_ids
        # Both should contain only track1
        assert pandas_result.track_ids == {"track1"}

    def test_dataset_remove(self, sample_segments_data: dict[str, list[Any]]) -> None:
        """Test remove method."""
        offset = RelativeOffsetCoordinate(0.0, 0.0)
        pandas_df = PandasDataFrame(sample_segments_data)
        polars_df = pl.DataFrame(sample_segments_data)

        pandas_dataset = PandasTrackGeometryDataset(offset, pandas_df)
        polars_dataset = PolarsTrackGeometryDataset(offset, polars_df)

        ids_to_remove = ["track1"]
        pandas_result = pandas_dataset.remove(ids_to_remove)
        polars_result = polars_dataset.remove(ids_to_remove)

        assert pandas_result.track_ids == polars_result.track_ids
        # Both should contain only track2
        assert pandas_result.track_ids == {"track2"}

    def test_dataset_equality_empty(self) -> None:
        """Test dataset equality with empty datasets."""
        offset = RelativeOffsetCoordinate(0.0, 0.0)

        pandas_dataset1 = PandasTrackGeometryDataset(offset)
        pandas_dataset2 = PandasTrackGeometryDataset(offset)
        polars_dataset1 = PolarsTrackGeometryDataset(offset)
        polars_dataset2 = PolarsTrackGeometryDataset(offset)

        assert pandas_dataset1 == pandas_dataset2
        assert polars_dataset1 == polars_dataset2

    def test_dataset_equality_with_data(
        self, sample_segments_data: dict[str, list[Any]]
    ) -> None:
        """Test dataset equality with data."""
        offset = RelativeOffsetCoordinate(0.0, 0.0)
        pandas_df = PandasDataFrame(sample_segments_data)
        polars_df = pl.DataFrame(sample_segments_data)

        pandas_dataset1 = PandasTrackGeometryDataset(offset, pandas_df.copy())
        pandas_dataset2 = PandasTrackGeometryDataset(offset, pandas_df.copy())
        polars_dataset1 = PolarsTrackGeometryDataset(offset, polars_df.clone())
        polars_dataset2 = PolarsTrackGeometryDataset(offset, polars_df.clone())

        assert pandas_dataset1 == pandas_dataset2
        assert polars_dataset1 == polars_dataset2


if __name__ == "__main__":
    pytest.main([__file__])
