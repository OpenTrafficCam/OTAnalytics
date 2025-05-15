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

# Column names for intersection parameters
DENOMINATOR = "denominator"
NON_PARALLEL = "non_parallel"
UA = "ua"
UB = "ub"


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


def calculate_intersection_parameters(
    segments_df: DataFrame,
    line_x1: float,
    line_y1: float,
    line_x2: float,
    line_y2: float,
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

    # Calculate denominator for all segments at once
    result_df[DENOMINATOR] = (line_y2 - line_y1) * (
        segments_df[END_X] - segments_df[START_X]
    ) - (line_x2 - line_x1) * (segments_df[END_Y] - segments_df[START_Y])

    # Filter out segments where lines are parallel (denominator == 0)
    result_df[NON_PARALLEL] = result_df[DENOMINATOR] != 0

    # Initialize ua and ub columns
    result_df[UA] = None
    result_df[UB] = None

    if result_df[NON_PARALLEL].any():
        # Calculate the parameters for the intersection points
        ua_values = (
            (line_x2 - line_x1) * (segments_df[START_Y] - line_y1)
            - (line_y2 - line_y1) * (segments_df[START_X] - line_x1)
        ) / result_df[DENOMINATOR]

        ub_values = (
            (segments_df[END_X] - segments_df[START_X])
            * (segments_df[START_Y] - line_y1)
            - (segments_df[END_Y] - segments_df[START_Y])
            * (segments_df[START_X] - line_x1)
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
) -> DataFrame:
    """
    Check if track segments intersect with a line.

    Args:
        segments_df (DataFrame): DataFrame with track segments
        line_x1 (float): X-coordinate of the line's start point
        line_y1 (float): Y-coordinate of the line's start point
        line_x2 (float): X-coordinate of the line's end point
        line_y2 (float): Y-coordinate of the line's end point

    Returns:
        DataFrame: Boolean mask indicating which segments intersect with the line
    """
    if segments_df.empty:
        return segments_df

    # Calculate intersection parameters
    params_df = calculate_intersection_parameters(
        segments_df, line_x1, line_y1, line_x2, line_y2
    )

    # If all segments are parallel or ua/ub couldn't be calculated
    if (
        not params_df[NON_PARALLEL].any()
        or params_df[UA].isna().all()
        or params_df[UB].isna().all()
    ):
        return DataFrame(index=segments_df.index, data=False, columns=[INTERSECTS])

    # Create a mask for valid intersections (intersection point is on both line
    # segments)
    valid_intersection_mask = (
        (0 <= params_df[UA])
        & (params_df[UA] <= 1)
        & (0 <= params_df[UB])
        & (params_df[UB] <= 1)
        & params_df[NON_PARALLEL]
    )

    # Create a DataFrame with the intersection results
    intersects_df = DataFrame(index=segments_df.index, data=False, columns=[INTERSECTS])
    intersects_df.loc[valid_intersection_mask, INTERSECTS] = True

    return intersects_df


def calculate_intersection_points(
    segments_df: DataFrame,
    line_x1: float,
    line_y1: float,
    line_x2: float,
    line_y2: float,
) -> DataFrame:
    """
    Calculate intersection points between track segments and a line.

    Args:
        segments_df (DataFrame): DataFrame with track segments
        line_x1 (float): X-coordinate of the line's start point
        line_y1 (float): Y-coordinate of the line's start point
        line_x2 (float): X-coordinate of the line's end point
        line_y2 (float): Y-coordinate of the line's end point

    Returns:
        DataFrame: DataFrame with columns INTERSECTION_X and INTERSECTION_Y containing
                  the coordinates of intersection points
    """
    if segments_df.empty:
        return DataFrame(
            index=segments_df.index, columns=[INTERSECTION_X, INTERSECTION_Y]
        )

    # Calculate intersection parameters
    params_df = calculate_intersection_parameters(
        segments_df, line_x1, line_y1, line_x2, line_y2
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
        # Calculate the intersection points for valid intersections
        intersection_x = segments_df[START_X] + params_df[UA] * (
            segments_df[END_X] - segments_df[START_X]
        )
        intersection_y = segments_df[START_Y] + params_df[UA] * (
            segments_df[END_Y] - segments_df[START_Y]
        )

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

    # Check which segments intersect with the line
    intersects_df = check_line_intersections(result_df, start_x, start_y, end_x, end_y)

    # If there are any intersections
    if intersects_df[INTERSECTS].any():
        # Calculate intersection points
        intersection_df = calculate_intersection_points(
            result_df, start_x, start_y, end_x, end_y
        )

        # Update the result DataFrame with intersection information
        valid_intersection_mask = intersects_df[INTERSECTS]
        result_df.loc[valid_intersection_mask, INTERSECTS] = True
        result_df.loc[valid_intersection_mask, INTERSECTION_X] = intersection_df.loc[
            valid_intersection_mask, INTERSECTION_X
        ]
        result_df.loc[valid_intersection_mask, INTERSECTION_Y] = intersection_df.loc[
            valid_intersection_mask, INTERSECTION_Y
        ]
        result_df.loc[valid_intersection_mask, INTERSECTION_LINE_ID] = line_id

    return result_df
