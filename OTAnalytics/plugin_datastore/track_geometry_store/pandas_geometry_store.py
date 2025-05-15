from pandas import DataFrame

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
END_X = "end-x"
END_Y = "end-y"

# Column names for intersections
INTERSECTS = "intersects"
INTERSECTION_X = "intersection_x"
INTERSECTION_Y = "intersection_y"
INTERSECTION_LINE_ID = "intersection_line_id"


def create_track_segments(df: DataFrame) -> DataFrame:
    """
    Create track segments from a DataFrame containing track points.

    A track segment connects two consecutive points of a track.

    Args:
        df (DataFrame): DataFrame with columns TRACK_ID, OCCURRENCE, X, Y

    Returns:
        DataFrame: DataFrame with columns TRACK_ID, START_OCCURRENCE, END_OCCURRENCE,
                  START_X, START_Y, END_X, END_Y
    """
    if df.empty:
        return DataFrame()

    # Make a copy to avoid modifying the original DataFrame
    data = df.copy()

    # Ensure the DataFrame is sorted by track-id and occurrence
    data = data.sort_values(by=[TRACK_ID, OCCURRENCE])

    # Group by track-id to create segments
    grouped = data.groupby(TRACK_ID)

    # Create a new DataFrame with shifted values to get start and end points
    segments = DataFrame()
    segments[TRACK_ID] = data[TRACK_ID]
    segments[END_OCCURRENCE] = data[OCCURRENCE]
    segments[END_X] = data[X]
    segments[END_Y] = data[Y]
    segments[START_OCCURRENCE] = grouped[OCCURRENCE].shift(1)
    segments[START_X] = grouped[X].shift(1)
    segments[START_Y] = grouped[Y].shift(1)

    # Remove rows where start values are NaN (first point of each track)
    segments = segments.dropna()

    # Reset index for clean output
    segments = segments.reset_index(drop=True)

    return segments


def find_line_intersections(
    segments_df: DataFrame,
    line_id: str,
    start_x: float,
    start_y: float,
    end_x: float,
    end_y: float,
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

    # Create a copy to avoid modifying the original DataFrame
    result_df = segments_df.copy()

    # Initialize new columns
    result_df[INTERSECTS] = False
    result_df[INTERSECTION_X] = None
    result_df[INTERSECTION_Y] = None
    result_df[INTERSECTION_LINE_ID] = None

    # Define line segment coordinates
    line_x1, line_y1 = start_x, start_y
    line_x2, line_y2 = end_x, end_y

    # Calculate intersection using line segment intersection formula
    # First, calculate the denominator for all segments at once
    denominator = (line_y2 - line_y1) * (result_df[END_X] - result_df[START_X]) - (
        line_x2 - line_x1
    ) * (result_df[END_Y] - result_df[START_Y])

    # Filter out segments where lines are parallel (denominator == 0)
    non_parallel_mask = denominator != 0

    if non_parallel_mask.any():
        # Calculate the parameters for the intersection points
        ua = (
            (line_x2 - line_x1) * (result_df[START_Y] - line_y1)
            - (line_y2 - line_y1) * (result_df[START_X] - line_x1)
        ) / denominator

        ub = (
            (result_df[END_X] - result_df[START_X]) * (result_df[START_Y] - line_y1)
            - (result_df[END_Y] - result_df[START_Y]) * (result_df[START_X] - line_x1)
        ) / denominator

        # Create a mask for valid intersections (intersection point is on both line
        # segments)
        valid_intersection_mask = (
            (0 <= ua) & (ua <= 1) & (0 <= ub) & (ub <= 1) & non_parallel_mask
        )

        if valid_intersection_mask.any():
            # Calculate the intersection points for valid intersections
            intersection_x = result_df[START_X] + ua * (
                result_df[END_X] - result_df[START_X]
            )
            intersection_y = result_df[START_Y] + ua * (
                result_df[END_Y] - result_df[START_Y]
            )

            # Update the result DataFrame with intersection information
            result_df.loc[valid_intersection_mask, INTERSECTS] = True
            result_df.loc[valid_intersection_mask, INTERSECTION_X] = intersection_x[
                valid_intersection_mask
            ]
            result_df.loc[valid_intersection_mask, INTERSECTION_Y] = intersection_y[
                valid_intersection_mask
            ]
            result_df.loc[valid_intersection_mask, INTERSECTION_LINE_ID] = line_id

    return result_df
