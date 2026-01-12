import math
from dataclasses import dataclass
from typing import Any, Iterable, Iterator, Optional, Sequence

import polars as pl

from OTAnalytics.domain import event, track
from OTAnalytics.domain.common import DataclassValidation
from OTAnalytics.domain.event import (
    SECTION_ID,
    Event,
    EventBuilder,
    EventDataset,
    SectionEventBuilder,
)
from OTAnalytics.domain.geometry import (
    Coordinate,
    DirectionVector2D,
    ImageCoordinate,
    RelativeOffsetCoordinate,
)
from OTAnalytics.domain.section import Section, SectionId, SectionType
from OTAnalytics.domain.track import (
    FRAME,
    OCCURRENCE,
    TRACK_CLASSIFICATION,
    TRACK_ID,
    VIDEO_NAME,
    H,
    Track,
    TrackId,
    W,
    X,
    Y,
)
from OTAnalytics.domain.track_dataset.track_dataset import (
    CURRENT_X,
    CURRENT_Y,
    END_FRAME,
    END_H,
    END_OCCURRENCE,
    END_VIDEO_NAME,
    END_W,
    END_X,
    END_Y,
    PREVIOUS_X,
    PREVIOUS_Y,
    START_H,
    START_OCCURRENCE,
    START_W,
    START_X,
    START_Y,
    IntersectionPoint,
    IntersectionPointsDataset,
    TrackDataset,
    TrackGeometryDataset,
    TrackIdSet,
)
from OTAnalytics.domain.types import EventType
from OTAnalytics.plugin_datastore.polars_track_id_set import PolarsTrackIdSet

MAGNITUDE = "magnitude"
CUM_SUM = "cum_sum"
ORDER = "order"
TRACK_ID_SUFFIX = f"{TRACK_ID}_suffix"

SEGMENT_LENGTH_X = "segment_length_x"
SEGMENT_LENGTH_Y = "segment_length_y"
SEGMENT_LENGTH = "segment_length"
INTERSECTION_LENGTH_X = "intersection_length_x"
INTERSECTION_LENGTH_Y = "intersection_length_y"
INTERSECTION_LENGTH = "intersection_length"
RELATIVE_POSITION = "relative_position"

# Column names for track segments
ROW_ID = "row_id"

# Column names for intersections
INTERSECTS = "intersects"
INTERSECTION_X = "intersection_x"
INTERSECTION_Y = "intersection_y"
INTERSECTION_LINE_ID = "intersection_line_id"
INTERSECTS_POLYGON = "intersects-polygon"

# Column names for intersection parameters
DENOMINATOR = "denominator"
NON_PARALLEL = "non_parallel"
UA = "ua"
UB = "ub"

# Column names for events
DIRECTION_VECTOR_X = f"{event.DIRECTION_VECTOR}_X"
DIRECTION_VECTOR_Y = f"{event.DIRECTION_VECTOR}_Y"
EVENT_COORDINATE_X = f"{event.EVENT_COORDINATE}_X"
EVENT_COORDINATE_Y = f"{event.EVENT_COORDINATE}_Y"
INTERPOLATED_EVENT_COORDINATE_X = f"{event.INTERPOLATED_EVENT_COORDINATE}_X"
INTERPOLATED_EVENT_COORDINATE_Y = f"{event.INTERPOLATED_EVENT_COORDINATE}_Y"


@dataclass(frozen=True)
class Polygon(DataclassValidation):
    """A polygon consists of an ordered sequence of coordinates.

    Note:
        The coordinates are not required to form a closed chain in this representation.

    Args:
        coordinates (list[Coordinate]): The coordinates defining the polygon. Must
            contain at least two coordinates.

    Raises:
        ValueError: If fewer than two coordinates are provided.
    """

    coordinates: list[Coordinate]

    def _validate(self) -> None:
        if len(self.coordinates) < 2:
            raise ValueError(
                (
                    "Number of coordinates to define a valid polygon must be "
                    f"greater equal two, but is {len(self.coordinates)}"
                )
            )


def create_track_segments(df: pl.DataFrame) -> pl.DataFrame:
    """
    Create track segments from a DataFrame of track points.

    A track segment connects two consecutive points of a track.

    Args:
        df (pl.DataFrame): DataFrame with columns TRACK_ID, OCCURRENCE, X, Y, W, H.

    Returns:
        pl.DataFrame: DataFrame with columns TRACK_ID, START_OCCURRENCE, END_OCCURRENCE,
            START_X, START_Y, START_W, START_H, END_X, END_Y, END_W, END_H.
    """
    if df.is_empty():
        return pl.DataFrame()

    # Sort by track_id and occurrence for efficient window operations
    df_sorted = df.sort([TRACK_ID, OCCURRENCE])

    # Use window functions to create segments - this is much more efficient in polars
    segments = df_sorted.with_columns(
        [
            # End values (current row)
            pl.col(OCCURRENCE).alias(END_OCCURRENCE),
            pl.col(X).alias(END_X),
            pl.col(Y).alias(END_Y),
            pl.col(W).alias(END_W),
            pl.col(H).alias(END_H),
            pl.col(FRAME).alias(END_FRAME),
            pl.col(VIDEO_NAME).alias(END_VIDEO_NAME),
            # Start values (previous row within the same track)
            pl.col(OCCURRENCE).shift(1).over(TRACK_ID).alias(START_OCCURRENCE),
            pl.col(X).shift(1).over(TRACK_ID).alias(START_X),
            pl.col(Y).shift(1).over(TRACK_ID).alias(START_Y),
            pl.col(W).shift(1).over(TRACK_ID).alias(START_W),
            pl.col(H).shift(1).over(TRACK_ID).alias(START_H),
        ]
    ).drop_nulls()  # Remove rows where shift resulted in null (first rows per track)

    # Select only the required columns in the exact order that pandas produces
    segments = segments.select(
        [
            ROW_ID,
            TRACK_ID,
            TRACK_CLASSIFICATION,
            END_VIDEO_NAME,
            END_FRAME,
            END_OCCURRENCE,
            END_X,
            END_Y,
            END_W,
            END_H,
            START_OCCURRENCE,
            START_X,
            START_Y,
            START_W,
            START_H,
        ]
    )

    return segments


def calculate_intersection_parameters(
    segments_df: pl.DataFrame,
    line_x1: float,
    line_y1: float,
    line_x2: float,
    line_y2: float,
    offset: RelativeOffsetCoordinate,
) -> pl.DataFrame:
    """
    Calculate intersection parameters between track segments and a line.

    This function implements the line-line intersection algorithm to determine
    intersection parameters for segments and a reference line.

    Args:
        segments_df (pl.DataFrame): DataFrame with track segments.
        line_x1, line_y1, line_x2, line_y2 (float): Coordinates of the reference line.
        offset (RelativeOffsetCoordinate): Offset applied to segment endpoints.

    Returns:
        pl.DataFrame: DataFrame with intersection parameters.
    """
    if segments_df.is_empty():
        return segments_df

    # Apply offset to segment endpoints
    result_df = segments_df.with_columns(
        [
            (pl.col(START_X) + pl.col(START_W) * offset.x).alias("seg_x1"),
            (pl.col(START_Y) + pl.col(START_H) * offset.y).alias("seg_y1"),
            (pl.col(END_X) + pl.col(END_W) * offset.x).alias("seg_x2"),
            (pl.col(END_Y) + pl.col(END_H) * offset.y).alias("seg_y2"),
        ]
    )

    # Calculate intersection parameters using vectorized operations
    result_df = (
        result_df.with_columns(
            [
                # Line direction vectors
                pl.lit(line_x2 - line_x1).alias("line_dx"),
                pl.lit(line_y2 - line_y1).alias("line_dy"),
                (pl.col("seg_x2") - pl.col("seg_x1")).alias("seg_dx"),
                (pl.col("seg_y2") - pl.col("seg_y1")).alias("seg_dy"),
            ]
        )
        .with_columns(
            [
                # Calculate denominator for intersection formula
                (
                    -pl.col("line_dx") * pl.col("seg_dy")
                    + pl.col("line_dy") * pl.col("seg_dx")
                ).alias(DENOMINATOR),
            ]
        )
        .with_columns(
            [
                # Check if lines are non-parallel
                (pl.col(DENOMINATOR).abs() > 1e-10).alias(NON_PARALLEL),
            ]
        )
    )

    # Calculate intersection parameters only for non-parallel segments
    result_df = result_df.with_columns(
        [
            pl.when(pl.col(NON_PARALLEL))
            .then(
                (
                    -(pl.col("seg_x1") - line_x1) * pl.col("seg_dy")
                    + (pl.col("seg_y1") - line_y1) * pl.col("seg_dx")
                )
                / pl.col(DENOMINATOR)
            )
            .otherwise(None)
            .alias(UA),
            pl.when(pl.col(NON_PARALLEL))
            .then(
                (
                    pl.col("line_dx") * (pl.col("seg_y1") - line_y1)
                    - pl.col("line_dy") * (pl.col("seg_x1") - line_x1)
                )
                / pl.col(DENOMINATOR)
            )
            .otherwise(None)
            .alias(UB),
        ]
    )

    return result_df


def check_line_intersections(
    segments_df: pl.DataFrame,
    line_x1: float,
    line_y1: float,
    line_x2: float,
    line_y2: float,
    offset: RelativeOffsetCoordinate,
) -> pl.DataFrame:
    """
    Check if track segments intersect with a line segment.

    Args:
        segments_df (pl.DataFrame): DataFrame with track segments.
        line_x1, line_y1, line_x2, line_y2 (float): Coordinates of the line segment.
        offset (RelativeOffsetCoordinate): Offset applied to segment endpoints.

    Returns:
        pl.DataFrame: DataFrame with intersection information.
    """
    if segments_df.is_empty():
        return segments_df

    # Calculate intersection parameters
    result_df = calculate_intersection_parameters(
        segments_df, line_x1, line_y1, line_x2, line_y2, offset
    )

    # Check if intersection is within both line segments (0 <= ua <= 1 and 0 <= ub <= 1)
    result_df = result_df.with_columns(
        [
            (
                pl.col(NON_PARALLEL)
                & (pl.col(UA).is_not_null())
                & (pl.col(UB).is_not_null())
                & (pl.col(UA) >= 0)
                & (pl.col(UA) <= 1)
                & (pl.col(UB) >= 0)
                & (pl.col(UB) <= 1)
            ).alias(INTERSECTS)
        ]
    )

    return result_df


def calculate_intersection_points(
    segments_df: pl.DataFrame,
    line_x1: float,
    line_y1: float,
    line_x2: float,
    line_y2: float,
    offset: RelativeOffsetCoordinate,
) -> pl.DataFrame:
    """
    Calculate intersection points between track segments and a line.

    Args:
        segments_df (pl.DataFrame): DataFrame with track segments.
        line_x1, line_y1, line_x2, line_y2 (float): Coordinates of the line.
        offset (RelativeOffsetCoordinate): Offset applied to segment endpoints.

    Returns:
        pl.DataFrame: DataFrame with intersection points.
    """
    if segments_df.is_empty():
        return segments_df

    # First check for intersections
    result_df = check_line_intersections(
        segments_df, line_x1, line_y1, line_x2, line_y2, offset
    )

    # Calculate intersection coordinates for intersecting segments
    result_df = result_df.with_columns(
        [
            pl.when(pl.col(INTERSECTS))
            .then(line_x1 + pl.col(UA) * (line_x2 - line_x1))
            .otherwise(None)
            .alias(INTERSECTION_X),
            pl.when(pl.col(INTERSECTS))
            .then(line_y1 + pl.col(UA) * (line_y2 - line_y1))
            .otherwise(None)
            .alias(INTERSECTION_Y),
        ]
    )

    return result_df


def find_line_intersections(
    segments_df: pl.DataFrame,
    line_id: str,
    start_x: float,
    start_y: float,
    end_x: float,
    end_y: float,
    offset: RelativeOffsetCoordinate | None = None,
) -> pl.DataFrame:
    """
    Find intersections between track segments and a line segment.

    Args:
        segments_df (pl.DataFrame): DataFrame with track segments.
        line_id (str): Identifier for the line.
        start_x, start_y, end_x, end_y (float): Line segment coordinates.
        offset (RelativeOffsetCoordinate, optional): Offset for segment endpoints.

    Returns:
        pl.DataFrame: DataFrame with intersection information and points.
    """
    if segments_df.is_empty():
        return segments_df

    if offset is None:
        offset = RelativeOffsetCoordinate(x=0.0, y=0.0)

    # Calculate intersection points
    result_df = calculate_intersection_points(
        segments_df, start_x, start_y, end_x, end_y, offset
    )

    # Add line ID for intersecting segments
    result_df = result_df.with_columns(
        [
            pl.when(pl.col(INTERSECTS))
            .then(pl.lit(line_id))
            .otherwise(None)
            .alias(INTERSECTION_LINE_ID)
        ]
    ).select(
        [
            ROW_ID,
            TRACK_ID,
            TRACK_CLASSIFICATION,
            END_VIDEO_NAME,
            END_FRAME,
            START_X,
            START_Y,
            END_X,
            END_Y,
            START_W,
            START_H,
            END_W,
            END_H,
            START_OCCURRENCE,
            END_OCCURRENCE,
            INTERSECTS,
            INTERSECTION_X,
            INTERSECTION_Y,
            INTERSECTION_LINE_ID,
        ]
    )

    return result_df


def check_polygon_intersections(
    segments_df: pl.DataFrame,
    polygon: Polygon,
    offset: RelativeOffsetCoordinate,
) -> pl.DataFrame:
    """
    Check if track segments intersect with a polygon.

    A polygon consists of a set of lines. This function checks if each track segment
    intersects with any of the lines in the polygon.

    Args:
        segments_df (pl.DataFrame): DataFrame with track segments.
        polygon (Polygon): The polygon to check intersections with.
        offset (RelativeOffsetCoordinate): Relative offset applied to segment endpoints.

    Returns:
        pl.DataFrame: DataFrame with an additional column INTERSECTS_POLYGON.
    """
    if segments_df.is_empty():
        return segments_df

    # Initialize intersection column
    result_df = segments_df.with_columns([pl.lit(False).alias(INTERSECTS_POLYGON)])

    # Get polygon coordinates
    polygon_coordinates = polygon.coordinates

    # Calculate polygon bounding box
    poly_min_x = min(c.x for c in polygon_coordinates)
    poly_max_x = max(c.x for c in polygon_coordinates)
    poly_min_y = min(c.y for c in polygon_coordinates)
    poly_max_y = max(c.y for c in polygon_coordinates)

    # Calculate segment endpoints with offset
    result_df = result_df.with_columns(
        [
            (pl.col(START_X) + pl.col(START_W) * offset.x).alias("sxa"),
            (pl.col(START_Y) + pl.col(START_H) * offset.y).alias("sya"),
            (pl.col(END_X) + pl.col(END_W) * offset.x).alias("exa"),
            (pl.col(END_Y) + pl.col(END_H) * offset.y).alias("eya"),
        ]
    )

    # Calculate segment bounding boxes
    result_df = result_df.with_columns(
        [
            pl.min_horizontal([pl.col("sxa"), pl.col("exa")]).alias("seg_min_x"),
            pl.max_horizontal([pl.col("sxa"), pl.col("exa")]).alias("seg_max_x"),
            pl.min_horizontal([pl.col("sya"), pl.col("eya")]).alias("seg_min_y"),
            pl.max_horizontal([pl.col("sya"), pl.col("eya")]).alias("seg_max_y"),
        ]
    )

    # Pre-filter segments whose bounding box intersects polygon bounding box
    candidate_mask = (
        (pl.col("seg_max_x") >= poly_min_x)
        & (pl.col("seg_min_x") <= poly_max_x)
        & (pl.col("seg_max_y") >= poly_min_y)
        & (pl.col("seg_min_y") <= poly_max_y)
    )

    candidates_df = result_df.filter(candidate_mask)

    if candidates_df.is_empty():
        return result_df

    # Check intersections with each line segment of the polygon
    intersecting_indices = set()

    for i in range(len(polygon_coordinates) - 1):
        # Get the start and end points of the current line segment
        start_x = polygon_coordinates[i].x
        start_y = polygon_coordinates[i].y
        end_x = polygon_coordinates[i + 1].x
        end_y = polygon_coordinates[i + 1].y

        # Further prefilter by line bounding box
        line_min_x = min(start_x, end_x)
        line_max_x = max(start_x, end_x)
        line_min_y = min(start_y, end_y)
        line_max_y = max(start_y, end_y)

        line_candidates = candidates_df.filter(
            (pl.col("seg_max_x") >= line_min_x)
            & (pl.col("seg_min_x") <= line_max_x)
            & (pl.col("seg_max_y") >= line_min_y)
            & (pl.col("seg_min_y") <= line_max_y)
        )

        if line_candidates.is_empty():
            continue

        # Check which segments intersect with the current line segment
        intersects_df = check_line_intersections(
            line_candidates, start_x, start_y, end_x, end_y, offset
        )

        # Collect indices of intersecting segments
        intersecting_rows = intersects_df.filter(pl.col(INTERSECTS))
        if not intersecting_rows.is_empty():
            # Get original indices from the filtered dataframe
            for row in intersecting_rows.iter_rows(named=True):
                # Find matching rows in original dataframe to get correct indices
                matching_indices = (
                    result_df.with_row_index()
                    .filter(
                        (pl.col(TRACK_ID) == row[TRACK_ID])
                        & (pl.col(START_OCCURRENCE) == row[START_OCCURRENCE])
                        & (pl.col(END_OCCURRENCE) == row[END_OCCURRENCE])
                    )
                    .select("index")
                    .to_series()
                    .to_list()
                )
                intersecting_indices.update(matching_indices)

    # Update intersection column for identified segments
    if intersecting_indices:
        # Create a boolean mask for intersecting rows
        mask_values = [i in intersecting_indices for i in range(len(result_df))]
        result_df = result_df.with_columns(
            [
                pl.when(pl.Series(mask_values))
                .then(True)
                .otherwise(pl.col(INTERSECTS_POLYGON))
                .alias(INTERSECTS_POLYGON)
            ]
        )

    return result_df.drop(
        ["sxa", "sya", "exa", "eya", "seg_min_x", "seg_max_x", "seg_min_y", "seg_max_y"]
    )


def get_section_offset(section: Section) -> RelativeOffsetCoordinate:
    if offset := section.relative_offset_coordinates.get(EventType.SECTION_ENTER):
        return offset
    raise ValueError(f"Section {section.id} has no offset")


class PolarsEventDataset(EventDataset):

    def __init__(self, events: Optional[pl.DataFrame] = None) -> None:
        if events is None:
            self._events = pl.DataFrame()
        else:
            self._events = events

    def __iter__(self) -> Iterator[Event]:
        for row in self._events.iter_rows(named=True):
            yield Event(
                road_user_id=row[event.ROAD_USER_ID],
                road_user_type=row[event.ROAD_USER_TYPE],
                hostname=row[event.HOSTNAME],
                occurrence=row[event.OCCURRENCE],
                frame_number=row[event.FRAME_NUMBER],
                section_id=(
                    SectionId(row[event.SECTION_ID]) if row[event.SECTION_ID] else None
                ),
                event_coordinate=ImageCoordinate(
                    row[EVENT_COORDINATE_X], row[EVENT_COORDINATE_Y]
                ),
                event_type=EventType.parse(row[event.EVENT_TYPE]),
                direction_vector=DirectionVector2D(
                    row[DIRECTION_VECTOR_X], row[DIRECTION_VECTOR_Y]
                ),
                video_name=row[event.VIDEO_NAME],
                interpolated_occurrence=row[event.INTERPOLATED_OCCURRENCE],
                interpolated_event_coordinate=ImageCoordinate(
                    row[INTERPOLATED_EVENT_COORDINATE_X],
                    row[INTERPOLATED_EVENT_COORDINATE_Y],
                ),
            )

    def __len__(self) -> int:
        return len(self._events)

    def __add__(self, other: "EventDataset") -> "EventDataset":
        # TODO: Check to remove
        raise NotImplementedError

    def __eq__(self, other: object) -> bool:
        # TODO: Check to remove
        raise NotImplementedError

    def extend(self, other: "EventDataset") -> None:
        # TODO: Check to remove
        raise NotImplementedError

    def append(self, event: Event) -> None:
        # TODO: Check to remove
        raise NotImplementedError

    def is_empty(self) -> bool:
        return self._events.is_empty()


class PolarsIntersectionPointsDataset(IntersectionPointsDataset):

    def __init__(self, points: Optional[pl.DataFrame] = None) -> None:
        if points is None:
            self._points = pl.DataFrame()
        else:
            self._points = points

    def items(
        self,
    ) -> Iterator[tuple[TrackId, list[tuple[SectionId, IntersectionPoint]]]]:
        raise NotImplementedError

    def keys(self) -> Iterator[TrackId]:
        raise NotImplementedError

    def get(self, track_id: TrackId) -> list[tuple[SectionId, IntersectionPoint]]:
        raise NotImplementedError

    @property
    def empty(self) -> bool:
        return self._points.is_empty()

    def __len__(self) -> int:
        return len(self._points)

    def __contains__(self, track_id: TrackId) -> bool:
        raise NotImplementedError

    def create_events(
        self,
        offset: RelativeOffsetCoordinate,
        event_builder: EventBuilder = SectionEventBuilder(),
    ) -> EventDataset:
        if self.empty:
            return PolarsEventDataset()
        events = (
            self._points.with_columns(
                [
                    pl.col(TRACK_ID).alias(event.ROAD_USER_ID),
                    pl.col(TRACK_CLASSIFICATION).alias(event.ROAD_USER_TYPE),
                    pl.col(END_VIDEO_NAME)
                    .str.extract(event.FILE_NAME_PATTERN)
                    .alias(event.HOSTNAME),
                    pl.col(END_OCCURRENCE).alias(event.OCCURRENCE),
                    pl.col(END_FRAME).alias(event.FRAME_NUMBER),
                    pl.col(SECTION_ID).alias(event.SECTION_ID),
                    pl.col(CURRENT_X).alias(EVENT_COORDINATE_X),
                    pl.col(CURRENT_Y).alias(EVENT_COORDINATE_Y),
                    pl.lit(EventType.SECTION_ENTER.value).alias(event.EVENT_TYPE),
                    (pl.col(CURRENT_X) - pl.col(PREVIOUS_X)).alias(DIRECTION_VECTOR_X),
                    (pl.col(CURRENT_Y) - pl.col(PREVIOUS_Y)).alias(DIRECTION_VECTOR_Y),
                    pl.col(END_VIDEO_NAME).alias(event.VIDEO_NAME),
                    (
                        pl.col(START_OCCURRENCE)
                        + pl.col(RELATIVE_POSITION)
                        * (pl.col(END_OCCURRENCE) - pl.col(START_OCCURRENCE))
                    ).alias(event.INTERPOLATED_OCCURRENCE),
                    (
                        pl.col(PREVIOUS_X)
                        + pl.col(RELATIVE_POSITION)
                        * (pl.col(CURRENT_X) - pl.col(PREVIOUS_X))
                    ).alias(INTERPOLATED_EVENT_COORDINATE_X),
                    (
                        pl.col(PREVIOUS_Y)
                        + pl.col(RELATIVE_POSITION)
                        * (pl.col(CURRENT_Y) - pl.col(PREVIOUS_Y))
                    ).alias(INTERPOLATED_EVENT_COORDINATE_Y),
                ]
            )
            .with_columns(
                [
                    (
                        (
                            pl.col(DIRECTION_VECTOR_X) ** 2
                            + pl.col(DIRECTION_VECTOR_Y) ** 2
                        ).sqrt()
                    ).alias(MAGNITUDE),
                ]
            )
            .with_columns(
                [
                    pl.when(pl.col(MAGNITUDE) == 0)
                    .then(pl.lit(0))
                    .otherwise(pl.col(DIRECTION_VECTOR_X) / pl.col(MAGNITUDE))
                    .alias(DIRECTION_VECTOR_X),
                    pl.when(pl.col(MAGNITUDE) == 0)
                    .then(pl.lit(0))
                    .otherwise(pl.col(DIRECTION_VECTOR_Y) / pl.col(MAGNITUDE))
                    .alias(DIRECTION_VECTOR_Y),
                ]
            )
            .select(
                [
                    event.ROAD_USER_ID,
                    event.ROAD_USER_TYPE,
                    event.HOSTNAME,
                    event.OCCURRENCE,
                    event.FRAME_NUMBER,
                    event.SECTION_ID,
                    EVENT_COORDINATE_X,
                    EVENT_COORDINATE_Y,
                    event.EVENT_TYPE,
                    DIRECTION_VECTOR_X,
                    DIRECTION_VECTOR_Y,
                    event.VIDEO_NAME,
                    event.INTERPOLATED_OCCURRENCE,
                    INTERPOLATED_EVENT_COORDINATE_X,
                    INTERPOLATED_EVENT_COORDINATE_Y,
                ]
            )
        )
        return PolarsEventDataset(events)


class PolarsTrackGeometryDataset(TrackGeometryDataset):
    _segments_df: pl.DataFrame

    def __init__(
        self,
        offset: RelativeOffsetCoordinate,
        segments_df: Optional[pl.DataFrame] = None,
    ):
        """Initialize a PolarsTrackGeometryDataset.

        Args:
            offset (RelativeOffsetCoordinate): Relative offset to apply to track points.
            segments_df (Optional[pl.DataFrame], optional): DataFrame with track
                segments. If None, an empty DataFrame will be created. Defaults to None.
        """
        self._offset = offset
        if segments_df is None:
            self._segments_df = pl.DataFrame()
        else:
            self._segments_df = segments_df

        # Ensure the DataFrame has the required columns
        required_columns = [
            TRACK_ID,
            START_X,
            START_Y,
            START_W,
            START_H,
            END_X,
            END_Y,
            END_W,
            END_H,
            START_OCCURRENCE,
            END_OCCURRENCE,
        ]

        if not self._segments_df.is_empty():
            missing_columns = [
                col for col in required_columns if col not in self._segments_df.columns
            ]
            if missing_columns:
                raise ValueError(
                    "Segments DataFrame must have the required columns. "
                    f"Following columns are missing: {missing_columns}"
                )

    @property
    def track_ids(self) -> set[str]:
        """Get track ids of tracks stored in dataset.

        Returns:
            set[str]: the track ids stored.
        """
        if self._segments_df.is_empty():
            return set()
        return set(self._segments_df[TRACK_ID].unique().to_list())

    @property
    def offset(self) -> RelativeOffsetCoordinate:
        return self._offset

    @property
    def empty(self) -> bool:
        """Check if the dataset is empty.

        Returns:
            bool: True if the dataset is empty, False otherwise.
        """
        return self._segments_df.is_empty()

    @staticmethod
    def from_track_dataset(
        dataset: TrackDataset, offset: RelativeOffsetCoordinate
    ) -> "PolarsTrackGeometryDataset":
        """Create a PolarsTrackGeometryDataset from a TrackDataset.

        Args:
            dataset (TrackDataset): The source track dataset.
            offset (RelativeOffsetCoordinate): Relative offset to apply to track points
                before segment creation.

        Returns:
            TrackGeometryDataset: A dataset containing the generated track segments.

        Raises:
            ValueError: If the dataset cannot be converted to polars format.
        """
        # Try to get data from pandas dataset and convert to polars
        try:
            if hasattr(dataset, "get_data"):
                data = dataset.get_data()
                # Convert pandas DataFrame to polars DataFrame
                if isinstance(data, pl.DataFrame):
                    polars_data = data
                elif hasattr(data, "to_dict"):
                    # It's a pandas DataFrame
                    polars_data = pl.DataFrame(data.to_dict(orient="list"))
                else:
                    # Try direct conversion
                    polars_data = pl.DataFrame(data)
            else:
                raise ValueError("Cannot extract data from the provided dataset")

            segments = create_track_segments(polars_data)
            return PolarsTrackGeometryDataset(offset, segments)
        except Exception as e:
            raise ValueError(
                f"PolarsTrackGeometryDataset could not be created from dataset: {e}"
            )

    def add_all(self, tracks: Iterable[Track]) -> "PolarsTrackGeometryDataset":
        """Add tracks to existing dataset.

        Pre-existing tracks will be overwritten.

        Args:
            tracks (Iterable[Track]): the tracks to add.

        Returns:
            PolarsTrackGeometryDataset: the dataset with tracks added.
        """
        # Convert tracks to DataFrame format
        track_data = self._convert_tracks_to_dataframe(tracks)
        if track_data.is_empty():
            return self

        # Create segments from track data
        new_segments = create_track_segments(track_data)
        if new_segments.is_empty():
            return self

        if self.empty:
            # If current dataset is empty, return new dataset with the new segments
            return PolarsTrackGeometryDataset(self._offset, new_segments)

        # Merge with existing segments, overwriting duplicates
        # Remove existing segments for tracks that are being added
        new_track_ids = new_segments[TRACK_ID].unique().to_list()
        existing_without_new = self._segments_df.filter(
            ~pl.col(TRACK_ID).is_in(new_track_ids)
        )

        # Combine existing (without overlaps) and new segments
        if not existing_without_new.is_empty() and not new_segments.is_empty():
            combined_segments = pl.concat([existing_without_new, new_segments])
        elif not existing_without_new.is_empty():
            combined_segments = existing_without_new
        elif not new_segments.is_empty():
            combined_segments = new_segments
        else:
            combined_segments = pl.DataFrame()

        return PolarsTrackGeometryDataset(self._offset, combined_segments)

    def _convert_tracks_to_dataframe(self, tracks: Iterable[Track]) -> pl.DataFrame:
        """Convert tracks to DataFrame format.

        Args:
            tracks (Iterable[Track]): tracks to convert.

        Returns:
            pl.DataFrame: tracks as dataframe with TRACK_ID, OCCURRENCE, X, Y, W, H.
        """
        if not tracks:
            return pl.DataFrame()

        data = []
        for current in tracks:
            track_id = current.id.id
            for detection in current.detections:
                data.append(
                    {
                        TRACK_ID: track_id,
                        OCCURRENCE: detection.occurrence,
                        X: detection.x,
                        Y: detection.y,
                        W: detection.w,
                        H: detection.h,
                    }
                )

        if not data:
            return pl.DataFrame()

        return pl.DataFrame(data)

    def remove(self, ids: Sequence[str]) -> "PolarsTrackGeometryDataset":
        """Remove track geometries with given ids from dataset.

        Args:
            ids (Sequence[str]): the track geometries to remove.

        Returns:
            PolarsTrackGeometryDataset: the dataset with tracks removed.
        """
        if self.empty or not ids:
            return self

        # Filter out segments with track IDs in the removal list
        remaining_segments = self._segments_df.filter(~pl.col(TRACK_ID).is_in(ids))

        return PolarsTrackGeometryDataset(self._offset, remaining_segments)

    def get_for(self, track_ids: list[str]) -> "PolarsTrackGeometryDataset":
        """Get geometries for given track ids if they exist.

        Ids that do not exist will not be included in the dataset.

        Args:
            track_ids (list[str]): the track ids.

        Returns:
            PolarsTrackGeometryDataset: the dataset with tracks.
        """
        if self.empty or not track_ids:
            return PolarsTrackGeometryDataset(self._offset)

        # Filter segments to include only those with track IDs in the provided list
        filtered_segments = self._segments_df.filter(pl.col(TRACK_ID).is_in(track_ids))

        return PolarsTrackGeometryDataset(self._offset, filtered_segments)

    def intersecting_tracks(self, sections: list[Section]) -> TrackIdSet:
        """Return a set of tracks intersecting a set of sections.

        Args:
            sections (list[Section]): the list of sections to intersect.

        Returns:
            set[TrackId]: the track ids intersecting the given sections.
        """
        if self.empty or not sections:
            return PolarsTrackIdSet()

        # Create a set to store the track IDs that intersect with any section
        intersecting_track_ids: set[TrackId] = set()

        # Check intersections for each section
        for section in sections:
            # Get the coordinates of the section
            coordinates = section.get_coordinates()
            offset = get_section_offset(section)

            if (
                section.get_type() == SectionType.LINE
                or section.get_type() == SectionType.CUTTING
            ):
                # For line sections, check if any track segment intersects with any leg
                # of the line. A leg is formed by each consecutive pair of coordinates.
                for i in range(len(coordinates) - 1):
                    start_x, start_y = coordinates[i].x, coordinates[i].y
                    end_x, end_y = coordinates[i + 1].x, coordinates[i + 1].y

                    # Find intersections with this leg of the line
                    intersections = find_line_intersections(
                        self._segments_df,
                        section.id.serialize(),
                        start_x,
                        start_y,
                        end_x,
                        end_y,
                        offset,
                    )

                    # Add track IDs that intersect with the line to the result set
                    intersecting_segments = intersections.filter(pl.col(INTERSECTS))
                    if not intersecting_segments.is_empty():
                        intersecting_track_ids.update(
                            TrackId(track_id)
                            for track_id in intersecting_segments[TRACK_ID]
                            .unique()
                            .to_list()
                        )
            elif section.get_type() == SectionType.AREA:
                # For area sections, check if any track segment intersects with the
                # polygon
                polygon = Polygon(coordinates)

                # Check polygon intersections
                intersections = check_polygon_intersections(
                    self._segments_df, polygon, offset
                )

                # Add track IDs that intersect with the polygon to the result set
                intersecting_segments = intersections.filter(pl.col(INTERSECTS_POLYGON))
                if not intersecting_segments.is_empty():
                    intersecting_track_ids.update(
                        TrackId(track_id)
                        for track_id in intersecting_segments[TRACK_ID]
                        .unique()
                        .to_list()
                    )

        return PolarsTrackIdSet(intersecting_track_ids)

    def intersection_points(
        self, sections: list[Section]
    ) -> dict[TrackId, list[tuple[SectionId, IntersectionPoint]]]:
        """Return the intersection points from tracks and the given sections.

        Args:
            sections (list[Section]): the sections to intersect with.

        Returns:
            dict[TrackId, list[tuple[SectionId, IntersectionPoint]]]:
                the intersection points.
        """
        if self.empty or not sections:
            return {}

        # Create a dictionary to store the intersection points for each track
        result: dict[TrackId, list[tuple[SectionId, IntersectionPoint]]] = {}

        # Process only line sections
        # (area sections don't have specific intersection points)
        line_sections = [
            section
            for section in sections
            if section.get_type() == SectionType.LINE
            or section.get_type() == SectionType.CUTTING
        ]

        if not line_sections:
            return {}

        # For each line section, find intersections with track segments
        for section in line_sections:
            # Get the coordinates of the section
            coordinates = section.get_coordinates()
            offset = get_section_offset(section)

            # Process each leg of the section (consecutive pair of coordinates)
            for i in range(len(coordinates) - 1):
                start_x, start_y = coordinates[i].x, coordinates[i].y
                end_x, end_y = coordinates[i + 1].x, coordinates[i + 1].y

                # Find intersections with this leg of the line
                intersections = find_line_intersections(
                    self._segments_df,
                    section.id.serialize(),
                    start_x,
                    start_y,
                    end_x,
                    end_y,
                    offset,
                )

                # Filter to only include segments that intersect with the line
                intersecting_segments = intersections.filter(pl.col(INTERSECTS))

                # Process each intersecting segment using polars iteration
                for row in intersecting_segments.iter_rows(named=True):
                    track_id = row[TRACK_ID]

                    # Calculate the relative position of the intersection point
                    # along the segment
                    segment_length_x = (row[END_X] + row[END_W] * offset.x) - (
                        row[START_X] + row[START_W] * offset.x
                    )
                    segment_length_y = (row[END_Y] + row[END_H] * offset.y) - (
                        row[START_Y] + row[START_H] * offset.y
                    )
                    segment_length = math.sqrt(
                        segment_length_x**2 + segment_length_y**2
                    )
                    # Avoid division by zero
                    if segment_length_x == 0 and segment_length_y == 0:
                        continue

                    # Calculate the relative position (0 to 1) along the segment
                    intersection_length_x = row[INTERSECTION_X] - (
                        row[START_X] + row[START_W] * offset.x
                    )
                    intersection_length_y = row[INTERSECTION_Y] - (
                        row[START_Y] + row[START_H] * offset.y
                    )
                    intersection_length = math.sqrt(
                        intersection_length_x**2 + intersection_length_y**2
                    )
                    relative_position = intersection_length / segment_length

                    # Create an IntersectionPoint
                    # The upper_index is 1 because we're dealing with segments
                    intersection_point = IntersectionPoint(
                        upper_index=1, relative_position=relative_position
                    )

                    # Add to the result dictionary
                    if track_id not in result:
                        result[track_id] = []
                    result[track_id].append((section.id, intersection_point))
        return result

    def wrap_intersection_points(
        self, sections: list[Section]
    ) -> IntersectionPointsDataset:
        """Return the intersection points from tracks and the given sections.

        Args:
            sections (list[Section]): the sections to intersect with.

        Returns:
            IntersectionPointsDataset: the intersection points.
        """
        if self.empty or not sections:
            return PolarsIntersectionPointsDataset()

        # Process only line sections
        # (area sections don't have specific intersection points)
        line_sections = [
            section
            for section in sections
            if section.get_type() == SectionType.LINE
            or section.get_type() == SectionType.CUTTING
        ]

        if not line_sections:
            return PolarsIntersectionPointsDataset()

        result_df: list[pl.DataFrame] = []
        # For each line section, find intersections with track segments
        for section in line_sections:
            # Get the coordinates of the section
            coordinates = section.get_coordinates()
            offset = get_section_offset(section)

            # Process each leg of the section (consecutive pair of coordinates)
            for i in range(len(coordinates) - 1):
                start_x, start_y = coordinates[i].x, coordinates[i].y
                end_x, end_y = coordinates[i + 1].x, coordinates[i + 1].y

                # Find intersections with this leg of the line
                intersections = find_line_intersections(
                    self._segments_df,
                    section.id.serialize(),
                    start_x,
                    start_y,
                    end_x,
                    end_y,
                    offset,
                )

                # Filter to only include segments that intersect with the line
                intersecting_segments = intersections.filter(pl.col(INTERSECTS))

                intersection_points = (
                    intersecting_segments.with_columns(
                        [
                            (pl.col(END_X) + pl.col(END_W) * offset.x).alias(CURRENT_X),
                            (pl.col(END_Y) + pl.col(END_H) * offset.y).alias(CURRENT_Y),
                            (pl.col(START_X) + pl.col(START_W) * offset.x).alias(
                                PREVIOUS_X
                            ),
                            (pl.col(START_Y) + pl.col(START_H) * offset.y).alias(
                                PREVIOUS_Y
                            ),
                        ]
                    )
                    .with_columns(
                        [
                            (pl.col(CURRENT_X) - pl.col(PREVIOUS_X)).alias(
                                SEGMENT_LENGTH_X
                            ),
                            (pl.col(CURRENT_Y) - pl.col(PREVIOUS_Y)).alias(
                                SEGMENT_LENGTH_Y
                            ),
                        ]
                    )
                    .with_columns(
                        [
                            (
                                pl.col(SEGMENT_LENGTH_X) ** 2
                                + pl.col(SEGMENT_LENGTH_Y) ** 2
                            )
                            .sqrt()
                            .alias(SEGMENT_LENGTH)
                        ]
                    )
                    .with_columns(
                        [
                            (
                                pl.col(INTERSECTION_X)
                                - (pl.col(START_X) + pl.col(START_W) * offset.x)
                            ).alias(INTERSECTION_LENGTH_X),
                            (
                                pl.col(INTERSECTION_Y)
                                - (pl.col(START_Y) + pl.col(START_H) * offset.y)
                            ).alias(INTERSECTION_LENGTH_Y),
                        ]
                    )
                    .with_columns(
                        [
                            (
                                pl.col(INTERSECTION_LENGTH_X) ** 2
                                + pl.col(INTERSECTION_LENGTH_Y) ** 2
                            )
                            .sqrt()
                            .alias(INTERSECTION_LENGTH)
                        ]
                    )
                    .with_columns(
                        [
                            pl.when(
                                (pl.col(SEGMENT_LENGTH_X) == 0)
                                & (pl.col(SEGMENT_LENGTH_Y) == 0)
                            )
                            .then(None)
                            .otherwise(
                                pl.col(INTERSECTION_LENGTH) / pl.col(SEGMENT_LENGTH)
                            )
                            .alias(RELATIVE_POSITION)
                        ]
                    )
                    .filter(pl.col(RELATIVE_POSITION).is_not_null())
                    .drop(
                        [
                            SEGMENT_LENGTH_X,
                            SEGMENT_LENGTH_Y,
                            SEGMENT_LENGTH,
                            INTERSECTION_LENGTH_X,
                            INTERSECTION_LENGTH_Y,
                            INTERSECTION_LENGTH,
                        ]
                    )
                    .with_columns(pl.lit(section.id.id).alias(SECTION_ID))
                )

                if len(intersecting_segments) > 0:
                    result_df.append(intersection_points)

        if result_df:
            return PolarsIntersectionPointsDataset(pl.concat(result_df))
        return PolarsIntersectionPointsDataset()

    def contained_by_sections(
        self, sections: list[Section]
    ) -> dict[TrackId, list[tuple[SectionId, list[bool]]]]:
        raise NotImplementedError

    def __eq__(self, other: Any) -> bool:
        """Check if this dataset is equal to another dataset.

        Args:
            other (Any): the other dataset to compare with.

        Returns:
            bool: True if the datasets are equal, False otherwise.
        """
        if not isinstance(other, PolarsTrackGeometryDataset):
            return False

        # If both are empty, they are equal
        if self.empty and other.empty:
            return True

        # If only one is empty, they are not equal
        if self.empty != other.empty:
            return False

        # Compare the DataFrames
        # First, ensure both DataFrames have the same columns
        if set(self._segments_df.columns) != set(other._segments_df.columns):
            return False

        # Sort both DataFrames to ensure consistent comparison
        self_df = self._segments_df.sort([TRACK_ID, START_OCCURRENCE])
        other_df = other._segments_df.sort([TRACK_ID, START_OCCURRENCE])

        # Compare the DataFrames using polars frame_equal
        try:
            return self_df.equals(other_df)
        except Exception:
            # Fallback to row-by-row comparison if frame_equal fails
            if len(self_df) != len(other_df):
                return False

            # Convert to list of dicts for comparison
            self_rows = self_df.to_dicts()
            other_rows = other_df.to_dicts()

            return self_rows == other_rows

    def track_ids_after_cut(self, section: Section) -> pl.DataFrame:
        if not section:
            return pl.DataFrame()

        # Create a set to store the track IDs that intersect with any section
        result = self._segments_df.select([ROW_ID, track.TRACK_ID]).with_columns(
            pl.lit(False).alias(INTERSECTS)
        )

        # Get the coordinates of the section
        coordinates = section.get_coordinates()
        offset = get_section_offset(section)

        if section.get_type() in [SectionType.CUTTING, SectionType.LINE]:
            # For line sections, check if any track segment intersects with any leg
            # of the line. A leg is formed by each consecutive pair of coordinates.
            for i in range(len(coordinates) - 1):
                start_x, start_y = coordinates[i].x, coordinates[i].y
                end_x, end_y = coordinates[i + 1].x, coordinates[i + 1].y

                # Find intersections with this leg of the line
                intersections = find_line_intersections(
                    self._segments_df,
                    section.id.serialize(),
                    start_x,
                    start_y,
                    end_x,
                    end_y,
                    offset,
                )

                # Add track IDs that intersect with the line to the result set
                if not intersections.is_empty():
                    result = (
                        result.join(
                            intersections.select([ROW_ID, TRACK_ID, INTERSECTS]),
                            on=ROW_ID,
                        )
                        .with_columns(
                            pl.col(INTERSECTS).or_(
                                pl.col(f"{INTERSECTS}_right")
                                .fill_null(False)
                                .alias(INTERSECTS)
                            )
                        )
                        .select([ROW_ID, TRACK_ID, INTERSECTS])
                    )

        COLUMN_ORDER = [ROW_ID, TRACK_ID, INTERSECTS, CUM_SUM, ORDER]
        results = (
            result.with_columns(
                pl.col(INTERSECTS).cum_sum().over(TRACK_ID).alias(CUM_SUM)
            )
            .with_columns(pl.lit(1).alias(ORDER))
            .select(COLUMN_ORDER)
        )
        temp = (
            results.group_by(TRACK_ID)
            .first()
            .with_columns(pl.lit(0).alias(ORDER))
            .with_columns(pl.lit(0, pl.UInt32).alias(CUM_SUM))
            .with_columns(pl.col(ROW_ID) - 1)
            .select(COLUMN_ORDER)
        )
        temp_r = pl.concat([results, temp])
        results = temp_r.sort(by=[TRACK_ID, ROW_ID, ORDER])
        cut_track_ids = (
            results.filter(pl.col(CUM_SUM) > 0).unique().select(TRACK_ID).to_series()
        )
        return (
            results.with_columns(
                pl.when(pl.col(TRACK_ID).is_in(cut_track_ids))
                .then("_" + pl.col(CUM_SUM).cast(pl.Utf8))
                .otherwise(pl.lit("").cast(pl.Utf8))
                .alias(TRACK_ID_SUFFIX)
            )
            .with_columns((pl.col(TRACK_ID) + pl.col(TRACK_ID_SUFFIX)).alias(TRACK_ID))
            .select([ROW_ID, TRACK_ID])
        )
