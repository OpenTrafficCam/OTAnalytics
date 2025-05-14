from pandas import DataFrame


def create_track_segments(df: DataFrame) -> DataFrame:
    """
    Create track segments from a DataFrame containing track points.

    A track segment connects two consecutive points of a track.

    Args:
        df (DataFrame): DataFrame with columns 'track-id', 'occurrence', 'x', 'y'

    Returns:
        DataFrame: DataFrame with columns 'track-id', 'start-occurrence', 'end-occurrence',
                  'start-x', 'start-y', 'end-x', 'end-y'
    """
    if df.empty:
        return DataFrame()

    # Make a copy to avoid modifying the original DataFrame
    data = df.copy()

    # Ensure the DataFrame is sorted by track-id and occurrence
    data = data.sort_values(by=['track-id', 'occurrence'])

    # Group by track-id to create segments
    grouped = data.groupby('track-id')

    # Create a new DataFrame with shifted values to get start and end points
    segments = DataFrame()
    segments['track-id'] = data['track-id']
    segments['end-occurrence'] = data['occurrence']
    segments['end-x'] = data['x']
    segments['end-y'] = data['y']
    segments['start-occurrence'] = grouped['occurrence'].shift(1)
    segments['start-x'] = grouped['x'].shift(1)
    segments['start-y'] = grouped['y'].shift(1)

    # Remove rows where start values are NaN (first point of each track)
    segments = segments.dropna()

    # Reset index for clean output
    segments = segments.reset_index(drop=True)

    return segments


def find_line_intersections(segments_df: DataFrame, line_id: str, start_x: float, start_y: float, 
                           end_x: float, end_y: float) -> DataFrame:
    """
    Find intersection points between track segments and a line.

    Args:
        segments_df (DataFrame): DataFrame with track segments (output of create_track_segments)
        line_id (str): ID of the line
        start_x (float): X-coordinate of the line's start point
        start_y (float): Y-coordinate of the line's start point
        end_x (float): X-coordinate of the line's end point
        end_y (float): Y-coordinate of the line's end point

    Returns:
        DataFrame: The input DataFrame with additional columns for intersection information:
                  - 'intersects': Boolean indicating if the segment intersects with the line
                  - 'intersection_x': X-coordinate of the intersection point (if any)
                  - 'intersection_y': Y-coordinate of the intersection point (if any)
                  - 'intersection_line_id': ID of the intersecting line
    """
    if segments_df.empty:
        return segments_df

    # Create a copy to avoid modifying the original DataFrame
    result_df = segments_df.copy()

    # Initialize new columns
    result_df['intersects'] = False
    result_df['intersection_x'] = None
    result_df['intersection_y'] = None
    result_df['intersection_line_id'] = None

    # Define line segment coordinates
    line_x1, line_y1 = start_x, start_y
    line_x2, line_y2 = end_x, end_y

    # Calculate intersection using line segment intersection formula
    # First, calculate the denominator for all segments at once
    denominator = ((line_y2 - line_y1) * (result_df['end-x'] - result_df['start-x']) - 
                   (line_x2 - line_x1) * (result_df['end-y'] - result_df['start-y']))

    # Filter out segments where lines are parallel (denominator == 0)
    non_parallel_mask = denominator != 0

    if non_parallel_mask.any():
        # Calculate the parameters for the intersection points
        ua = ((line_x2 - line_x1) * (result_df['start-y'] - line_y1) - 
              (line_y2 - line_y1) * (result_df['start-x'] - line_x1)) / denominator

        ub = ((result_df['end-x'] - result_df['start-x']) * (result_df['start-y'] - line_y1) - 
              (result_df['end-y'] - result_df['start-y']) * (result_df['start-x'] - line_x1)) / denominator

        # Create a mask for valid intersections (intersection point is on both line segments)
        valid_intersection_mask = (0 <= ua) & (ua <= 1) & (0 <= ub) & (ub <= 1) & non_parallel_mask

        if valid_intersection_mask.any():
            # Calculate the intersection points for valid intersections
            intersection_x = result_df['start-x'] + ua * (result_df['end-x'] - result_df['start-x'])
            intersection_y = result_df['start-y'] + ua * (result_df['end-y'] - result_df['start-y'])

            # Update the result DataFrame with intersection information
            result_df.loc[valid_intersection_mask, 'intersects'] = True
            result_df.loc[valid_intersection_mask, 'intersection_x'] = intersection_x[valid_intersection_mask]
            result_df.loc[valid_intersection_mask, 'intersection_y'] = intersection_y[valid_intersection_mask]
            result_df.loc[valid_intersection_mask, 'intersection_line_id'] = line_id

    return result_df