from dataclasses import dataclass
from typing import Any, Iterable, Optional, Sequence

from pandas import DataFrame

from OTAnalytics.domain.common import DataclassValidation
from OTAnalytics.domain.geometry import Coordinate, RelativeOffsetCoordinate
from OTAnalytics.domain.section import Section, SectionId, SectionType
from OTAnalytics.domain.track import H, Track, TrackId, W
from OTAnalytics.domain.track_dataset.track_dataset import (
    IntersectionPoint,
    TrackDataset,
    TrackGeometryDataset,
)
from OTAnalytics.domain.types import EventType
from OTAnalytics.plugin_datastore.track_store import PandasTrackDataset

# Column names for track points
TRACK_ID = "track-id"
OCCURRENCE = "occurrence"
X = "x"
Y = "y"

# Column names for track segments
START_OCCURRENCE = "start-occurrence"
END_OCCURRENCE = "end-occurrence"
START_X = "start-x"
START_Y = "start-y"
START_W = "start-w"
START_H = "start-h"
END_X = "end-x"
END_Y = "end-y"
END_W = "end-w"
END_H = "end-h"

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


def create_track_segments(df: DataFrame) -> DataFrame:
    """
    Create track segments from a DataFrame of track points.

    A track segment connects two consecutive points of a track.

    Args:
        df (DataFrame): DataFrame with columns TRACK_ID, OCCURRENCE, X, Y, W, H.

    Returns:
        DataFrame: DataFrame with columns TRACK_ID, START_OCCURRENCE, END_OCCURRENCE,
            START_X, START_Y, START_W, START_H, END_X, END_Y, END_W, END_H.
    """
    if df.empty:
        return DataFrame()

    # Create MultiIndex and sort once
    df_indexed = df.set_index([TRACK_ID, OCCURRENCE]).sort_index()

    # Group by level 0 (TRACK_ID) - this is very fast on sorted MultiIndex
    grouped = df_indexed.groupby(level=0)

    # Create segments DataFrame
    segments = DataFrame()
    segments[TRACK_ID] = df_indexed.index.get_level_values(0)
    segments[END_OCCURRENCE] = df_indexed.index.get_level_values(1)
    segments[END_X] = df_indexed[X]
    segments[END_Y] = df_indexed[Y]
    segments[END_W] = df_indexed[W]
    segments[END_H] = df_indexed[H]

    # Shift operations are faster on sorted groups
    segments[START_OCCURRENCE] = grouped[OCCURRENCE].shift(1)
    segments[START_X] = grouped[X].shift(1)
    segments[START_Y] = grouped[Y].shift(1)
    segments[START_W] = grouped[W].shift(1)
    segments[START_H] = grouped[H].shift(1)

    # Remove NaN rows and reset index
    segments = segments.dropna().reset_index(drop=True)

    return segments


def apply_offset(segments_df: DataFrame, offset: RelativeOffsetCoordinate) -> DataFrame:
    """Apply an offset to the coordinates of a DataFrame containing track segments."""
    if segments_df.empty:
        return segments_df

    segments_df = segments_df.copy()
    segments_df[START_X] += segments_df[START_W] * offset.x
    segments_df[START_Y] += segments_df[START_H] * offset.y
    segments_df[END_X] += segments_df[END_W] * offset.x
    segments_df[END_Y] += segments_df[END_H] * offset.y
    return segments_df


def calculate_intersection_parameters(
    segments_df: DataFrame,
    line_x1: float,
    line_y1: float,
    line_x2: float,
    line_y2: float,
    offset: RelativeOffsetCoordinate,
) -> DataFrame:
    """
    Calculate parameters needed for line intersection calculations.

    Args:
        segments_df (DataFrame): DataFrame with track segments
        line_x1 (float): X-coordinate of the line's start point
        line_y1 (float): Y-coordinate of the line's start point
        line_x2 (float): X-coordinate of the line's end point
        line_y2 (float): Y-coordinate of the line's end point

    Returns:
        DataFrame: A DataFrame containing the following columns:
            - DENOMINATOR: Denominator values for intersection calculations
            - NON_PARALLEL: Boolean mask for non-parallel segments
            - UA: Parameter ua for intersection point calculation
            - UB: Parameter ub for intersection point calculation
    """
    # Initialize result DataFrame
    result_df = DataFrame(index=segments_df.index)

    # Apply offset on-the-fly (no mutation/copy)
    sxa = segments_df[START_X] + segments_df[START_W] * offset.x
    sya = segments_df[START_Y] + segments_df[START_H] * offset.y
    exa = segments_df[END_X] + segments_df[END_W] * offset.x
    eya = segments_df[END_Y] + segments_df[END_H] * offset.y

    # Calculate denominator for all segments at once
    result_df[DENOMINATOR] = (line_y2 - line_y1) * (exa - sxa) - (line_x2 - line_x1) * (
        eya - sya
    )

    # Filter out segments where lines are parallel (denominator == 0)
    result_df[NON_PARALLEL] = result_df[DENOMINATOR] != 0

    # Initialize ua and ub columns
    result_df[UA] = None
    result_df[UB] = None

    if result_df[NON_PARALLEL].any():
        # Calculate the parameters for the intersection points
        ua_values = (
            (line_x2 - line_x1) * (sya - line_y1)
            - (line_y2 - line_y1) * (sxa - line_x1)
        ) / result_df[DENOMINATOR]

        ub_values = (
            (exa - sxa) * (sya - line_y1) - (eya - sya) * (sxa - line_x1)
        ) / result_df[DENOMINATOR]

        # Update ua and ub columns for non-parallel segments
        result_df.loc[result_df[NON_PARALLEL], UA] = ua_values[result_df[NON_PARALLEL]]
        result_df.loc[result_df[NON_PARALLEL], UB] = ub_values[result_df[NON_PARALLEL]]

    return result_df


def check_line_intersections(
    segments_df: DataFrame,
    line_x1: float,
    line_y1: float,
    line_x2: float,
    line_y2: float,
    offset: RelativeOffsetCoordinate,
) -> DataFrame:
    """
    Check if track segments intersect with a line.

    Args:
        segments_df (DataFrame): DataFrame with track segments.
        line_x1 (float): X-coordinate of the line's start point.
        line_y1 (float): Y-coordinate of the line's start point.
        line_x2 (float): X-coordinate of the line's end point.
        line_y2 (float): Y-coordinate of the line's end point.
        offset (RelativeOffsetCoordinate): Relative offset applied to segment endpoints
            before intersection checks.

    Returns:
        DataFrame: DataFrame with a single column INTERSECTS indicating whether each
            segment intersects the line.
    """
    if segments_df.empty:
        return DataFrame(index=segments_df.index, data=False, columns=[INTERSECTS])

    # Bounding box of the line
    line_min_x = min(line_x1, line_x2)
    line_max_x = max(line_x1, line_x2)
    line_min_y = min(line_y1, line_y2)
    line_max_y = max(line_y1, line_y2)

    # Segment endpoints adjusted by offset (no copy/mutation)
    sxa = segments_df[START_X] + segments_df[START_W] * offset.x
    sya = segments_df[START_Y] + segments_df[START_H] * offset.y
    exa = segments_df[END_X] + segments_df[END_W] * offset.x
    eya = segments_df[END_Y] + segments_df[END_H] * offset.y

    # Segment bounding boxes
    seg_min_x = sxa.where(sxa <= exa, exa)
    seg_max_x = sxa.where(sxa >= exa, exa)
    seg_min_y = sya.where(sya <= eya, eya)
    seg_max_y = sya.where(sya >= eya, eya)

    # Candidate segments whose bbox intersects the line bbox
    candidate_mask = (
        (seg_max_x >= line_min_x)
        & (seg_min_x <= line_max_x)
        & (seg_max_y >= line_min_y)
        & (seg_min_y <= line_max_y)
    )

    # Prepare result DataFrame (all False by default)
    intersects_df = DataFrame(index=segments_df.index, data=False, columns=[INTERSECTS])

    if not candidate_mask.any():
        return intersects_df

    # Calculate intersection parameters for candidates only
    candidate_df = segments_df.loc[candidate_mask]
    params_df = calculate_intersection_parameters(
        candidate_df, line_x1, line_y1, line_x2, line_y2, offset
    )

    # If all candidate segments are parallel or ua/ub couldn't be calculated
    if (
        not params_df[NON_PARALLEL].any()
        or params_df[UA].isna().all()
        or params_df[UB].isna().all()
    ):
        return intersects_df

    # Create a mask for valid intersections
    # (intersection point is on both line segments)
    valid_intersection_mask = (
        (0 <= params_df[UA])
        & (params_df[UA] <= 1)
        & (0 <= params_df[UB])
        & (params_df[UB] <= 1)
        & params_df[NON_PARALLEL]
    )

    # Update the result DataFrame with True where intersections occur
    if valid_intersection_mask.any():
        valid_idx = params_df.index[valid_intersection_mask]
        intersects_df.loc[valid_idx, INTERSECTS] = True

    return intersects_df


def calculate_intersection_points(
    segments_df: DataFrame,
    line_x1: float,
    line_y1: float,
    line_x2: float,
    line_y2: float,
    offset: RelativeOffsetCoordinate,
) -> DataFrame:
    """
    Calculate intersection points between track segments and a line.

    Args:
        segments_df (DataFrame): DataFrame with track segments.
        line_x1 (float): X-coordinate of the line's start point.
        line_y1 (float): Y-coordinate of the line's start point.
        line_x2 (float): X-coordinate of the line's end point.
        line_y2 (float): Y-coordinate of the line's end point.
        offset (RelativeOffsetCoordinate): Relative offset applied to segment endpoints
            before intersection calculation.

    Returns:
        DataFrame: DataFrame with columns INTERSECTION_X and INTERSECTION_Y containing
            the coordinates of intersection points.
    """
    if segments_df.empty:
        return DataFrame(
            index=segments_df.index, columns=[INTERSECTION_X, INTERSECTION_Y]
        )

    # Calculate intersection parameters (offset applied on-the-fly)
    params_df = calculate_intersection_parameters(
        segments_df, line_x1, line_y1, line_x2, line_y2, offset
    )

    # Initialize DataFrame for intersection coordinates
    intersection_df = DataFrame(
        index=segments_df.index, columns=[INTERSECTION_X, INTERSECTION_Y]
    )

    # If all segments are parallel or ua/ub couldn't be calculated
    if (
        not params_df[NON_PARALLEL].any()
        or params_df[UA].isna().all()
        or params_df[UB].isna().all()
    ):
        return intersection_df

    # Create a mask for valid intersections
    valid_intersection_mask = (
        (0 <= params_df[UA])
        & (params_df[UA] <= 1)
        & (0 <= params_df[UB])
        & (params_df[UB] <= 1)
        & params_df[NON_PARALLEL]
    )

    if valid_intersection_mask.any():
        # Adjusted segment endpoints with offset
        sxa = segments_df[START_X] + segments_df[START_W] * offset.x
        sya = segments_df[START_Y] + segments_df[START_H] * offset.y
        exa = segments_df[END_X] + segments_df[END_W] * offset.x
        eya = segments_df[END_Y] + segments_df[END_H] * offset.y

        # Calculate the intersection points for valid intersections
        intersection_x = sxa + params_df[UA] * (exa - sxa)
        intersection_y = sya + params_df[UA] * (eya - sya)

        # Update the result DataFrame with intersection coordinates
        intersection_df.loc[valid_intersection_mask, INTERSECTION_X] = intersection_x[
            valid_intersection_mask
        ]
        intersection_df.loc[valid_intersection_mask, INTERSECTION_Y] = intersection_y[
            valid_intersection_mask
        ]

    return intersection_df


def find_line_intersections(
    segments_df: DataFrame,
    line_id: str,
    start_x: float,
    start_y: float,
    end_x: float,
    end_y: float,
    offset: RelativeOffsetCoordinate | None = None,
) -> DataFrame:
    """
    Find intersection points between track segments and a line.

    Args:
        segments_df (DataFrame): DataFrame with track segments (output of
            create_track_segments)
        line_id (str): ID of the line
        start_x (float): X-coordinate of the line's start point
        start_y (float): Y-coordinate of the line's start point
        end_x (float): X-coordinate of the line's end point
        end_y (float): Y-coordinate of the line's end point
        offset (RelativeOffsetCoordinate): Relative offset applied to segment endpoints
            before intersection checks.

    Returns:
        DataFrame: The input DataFrame with additional columns for intersection
            information:
                  - INTERSECTS: Boolean indicating if the segment intersects with the
                        line
                  - INTERSECTION_X: X-coordinate of the intersection point (if any)
                  - INTERSECTION_Y: Y-coordinate of the intersection point (if any)
                  - INTERSECTION_LINE_ID: ID of the intersecting line
    """
    if segments_df.empty:
        return segments_df

    # Default offset if not provided
    if offset is None:
        offset = RelativeOffsetCoordinate(0.0, 0.0)

    # Use a shallow copy to avoid duplicating data blocks
    result_df = segments_df.copy(deep=False)

    # Initialize new columns
    result_df[INTERSECTS] = False
    result_df[INTERSECTION_X] = None
    result_df[INTERSECTION_Y] = None
    result_df[INTERSECTION_LINE_ID] = None

    # Check which segments intersect with the line
    intersects_df = check_line_intersections(
        segments_df, start_x, start_y, end_x, end_y, offset
    )

    # If there are any intersections
    if intersects_df[INTERSECTS].any():
        valid_intersection_mask = intersects_df[INTERSECTS]

        # Calculate intersection points only for intersecting segments
        intersection_df = calculate_intersection_points(
            segments_df.loc[valid_intersection_mask],
            start_x,
            start_y,
            end_x,
            end_y,
            offset,
        )

        # Update the result DataFrame with intersection information
        result_df.loc[valid_intersection_mask, INTERSECTS] = True
        result_df.loc[valid_intersection_mask, INTERSECTION_X] = intersection_df[
            INTERSECTION_X
        ]
        result_df.loc[valid_intersection_mask, INTERSECTION_Y] = intersection_df[
            INTERSECTION_Y
        ]
        result_df.loc[valid_intersection_mask, INTERSECTION_LINE_ID] = line_id

    return result_df


def check_polygon_intersections(
    segments_df: DataFrame,
    polygon: Polygon,
    offset: RelativeOffsetCoordinate,
) -> DataFrame:
    """
    Check if track segments intersect with a polygon.

    A polygon consists of a set of lines. This function checks if each track segment
    intersects with any of the lines in the polygon.

    Args:
        segments_df (DataFrame): DataFrame with track segments (output of
            create_track_segments).
        polygon (Polygon): The polygon to check intersections with.
        offset (RelativeOffsetCoordinate): Relative offset applied to segment endpoints
            before intersection checks.

    Returns:
        DataFrame: The input DataFrame with an additional column INTERSECTS_POLYGON
            indicating if the segment intersects with the polygon.
    """
    if segments_df.empty:
        return segments_df

    # Shallow copy to add result column without duplicating data
    result_df = segments_df.copy(deep=False)

    # Initialize the intersects-polygon column to False
    result_df[INTERSECTS_POLYGON] = False

    # Get the coordinates of the polygon
    polygon_coordinates = polygon.coordinates

    # Polygon bounding box
    poly_min_x = min(c.x for c in polygon_coordinates)
    poly_max_x = max(c.x for c in polygon_coordinates)
    poly_min_y = min(c.y for c in polygon_coordinates)
    poly_max_y = max(c.y for c in polygon_coordinates)

    # Segment endpoints adjusted by offset (no copy/mutation)
    sxa = segments_df[START_X] + segments_df[START_W] * offset.x
    sya = segments_df[START_Y] + segments_df[START_H] * offset.y
    exa = segments_df[END_X] + segments_df[END_W] * offset.x
    eya = segments_df[END_Y] + segments_df[END_H] * offset.y

    # Segment bounding boxes
    seg_min_x = sxa.where(sxa <= exa, exa)
    seg_max_x = sxa.where(sxa >= exa, exa)
    seg_min_y = sya.where(sya <= eya, eya)
    seg_max_y = sya.where(sya >= eya, eya)

    # Pre-filter segments whose bbox intersects polygon bbox
    candidate_mask = (
        (seg_max_x >= poly_min_x)
        & (seg_min_x <= poly_max_x)
        & (seg_max_y >= poly_min_y)
        & (seg_min_y <= poly_max_y)
    )

    if not candidate_mask.any():
        return result_df

    # Check intersections with each line segment of the polygon
    for i in range(len(polygon_coordinates) - 1):
        # Get the start and end points of the current line segment
        start_x = polygon_coordinates[i].x
        start_y = polygon_coordinates[i].y
        end_x = polygon_coordinates[i + 1].x
        end_y = polygon_coordinates[i + 1].y

        # Further prefilter by line bbox
        line_min_x = min(start_x, end_x)
        line_max_x = max(start_x, end_x)
        line_min_y = min(start_y, end_y)
        line_max_y = max(start_y, end_y)
        cand2_mask = (
            (seg_max_x >= line_min_x)
            & (seg_min_x <= line_max_x)
            & (seg_max_y >= line_min_y)
            & (seg_min_y <= line_max_y)
            & candidate_mask
        )
        if not cand2_mask.any():
            continue

        # Check which segments intersect with the current line segment
        intersects_df = check_line_intersections(
            segments_df.loc[cand2_mask], start_x, start_y, end_x, end_y, offset
        )

        # Update the result DataFrame using indices of True values
        if intersects_df[INTERSECTS].any():
            true_idx = intersects_df.index[intersects_df[INTERSECTS]]
            result_df.loc[true_idx, INTERSECTS_POLYGON] = True

    return result_df


def get_section_offset(section: Section) -> RelativeOffsetCoordinate:
    if offset := section.relative_offset_coordinates.get(EventType.SECTION_ENTER):
        return offset
    raise ValueError(f"Section {section.id} has no offset")


class PandasTrackGeometryDataset(TrackGeometryDataset):
    _segments_df: DataFrame

    def __init__(self, segments_df: Optional[DataFrame] = None):
        """Initialize a PandasTrackGeometryDataset.

        Args:
            segments_df (Optional[DataFrame], optional): DataFrame with track segments.
                If None, an empty DataFrame will be created. Defaults to None.
        """
        if segments_df is None:
            self._segments_df = DataFrame()
        else:
            self._segments_df = segments_df.copy()

        # Ensure the DataFrame has the required columns
        if not self._segments_df.empty and not all(
            col in self._segments_df.columns
            for col in [
                TRACK_ID,
                START_X,
                START_Y,
                END_X,
                END_Y,
                START_OCCURRENCE,
                END_OCCURRENCE,
            ]
        ):
            raise ValueError("Segments DataFrame must have the required columns")

    @property
    def track_ids(self) -> set[str]:
        """Get track ids of tracks stored in dataset.

        Returns:
            set[str]: the track ids stored.
        """
        if self._segments_df.empty:
            return set()
        return set(self._segments_df[TRACK_ID].unique())

    @property
    def offset(self) -> RelativeOffsetCoordinate:
        # TODO Do not implement
        raise NotImplementedError

    @property
    def empty(self) -> bool:
        """Check if the dataset is empty.

        Returns:
            bool: True if the dataset is empty, False otherwise.
        """
        return self._segments_df.empty

    @staticmethod
    def from_track_dataset(
        dataset: TrackDataset, offset: RelativeOffsetCoordinate
    ) -> "TrackGeometryDataset":
        """Create a PandasTrackGeometryDataset from a TrackDataset.

        Args:
            dataset (TrackDataset): The source track dataset. Must be a
                PandasTrackDataset.
            offset (RelativeOffsetCoordinate): Relative offset to apply to track points
                before segment creation. Currently not applied in this implementation.

        Returns:
            TrackGeometryDataset: A dataset containing the generated track segments.

        Raises:
            ValueError: If the dataset is not a PandasTrackDataset.
        """
        if isinstance(dataset, PandasTrackDataset):
            data = dataset.get_data()
            segments = create_track_segments(data)
            return PandasTrackGeometryDataset(segments)
        else:
            raise ValueError(
                "PandasTrackGeometryDataset can only be created from a "
                "PandasTrackDataset"
            )

    def add_all(self, tracks: Iterable[Track]) -> "TrackGeometryDataset":
        # TODO Do not implement
        raise NotImplementedError

    def remove(self, ids: Sequence[str]) -> "TrackGeometryDataset":
        # TODO Do not implement
        raise NotImplementedError

    def get_for(self, track_ids: list[str]) -> "TrackGeometryDataset":
        # TODO Do not implement
        raise NotImplementedError

    def intersecting_tracks(self, sections: list[Section]) -> set[TrackId]:
        """Return a set of tracks intersecting a set of sections.

        Args:
            sections (list[Section]): the list of sections to intersect.

        Returns:
            set[TrackId]: the track ids intersecting the given sections.
        """
        if self.empty or not sections:
            return set()

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
                    intersecting_segments = intersections[intersections[INTERSECTS]]
                    intersecting_track_ids.update(
                        intersecting_segments[TRACK_ID].unique()
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
                intersecting_segments = intersections[intersections[INTERSECTS_POLYGON]]
                intersecting_track_ids.update(intersecting_segments[TRACK_ID].unique())

        return intersecting_track_ids

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
                intersecting_segments = intersections[intersections[INTERSECTS]]

                # Process each intersecting segment
                for _, segment in intersecting_segments.iterrows():
                    track_id = segment[TRACK_ID]

                    # Calculate the relative position of the intersection point
                    # along the segment
                    segment_length_x = segment[END_X] - segment[START_X]
                    segment_length_y = segment[END_Y] - segment[START_Y]

                    # Avoid division by zero
                    if segment_length_x == 0 and segment_length_y == 0:
                        continue

                    # Calculate the relative position (0 to 1) along the segment
                    if segment_length_x != 0:
                        relative_position = (
                            segment[INTERSECTION_X] - segment[START_X]
                        ) / segment_length_x
                    else:
                        relative_position = (
                            segment[INTERSECTION_Y] - segment[START_Y]
                        ) / segment_length_y

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

    def contained_by_sections(
        self, sections: list[Section]
    ) -> dict[TrackId, list[tuple[SectionId, list[bool]]]]:
        # TODO Do not implement
        raise NotImplementedError

    def __eq__(self, other: Any) -> bool:
        """Check if this dataset is equal to another dataset.

        Args:
            other (Any): the other dataset to compare with.

        Returns:
            bool: True if the datasets are equal, False otherwise.
        """
        if not isinstance(other, PandasTrackGeometryDataset):
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
        self_df = self._segments_df.sort_values(
            by=[TRACK_ID, START_OCCURRENCE]
        ).reset_index(drop=True)
        other_df = other._segments_df.sort_values(
            by=[TRACK_ID, START_OCCURRENCE]
        ).reset_index(drop=True)

        # Compare the DataFrames
        return self_df.equals(other_df)
