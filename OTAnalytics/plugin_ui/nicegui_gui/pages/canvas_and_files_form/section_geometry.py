"""UI independent geometry helpers for the section editor on the WebUI canvas."""

Point = tuple[int, int]

MINIMUM_LINE_SECTION_KNOBS = 2
MINIMUM_AREA_SECTION_KNOBS = 3


def minimum_knob_count(is_area_section: bool) -> int:
    """Minimal number of knobs a section must have.

    A line section needs a start and an end. An area needs at least three distinct
    knobs to enclose a surface.
    """
    if is_area_section:
        return MINIMUM_AREA_SECTION_KNOBS
    return MINIMUM_LINE_SECTION_KNOBS


def has_enough_knobs(coordinates: list[Point], is_area_section: bool) -> bool:
    return len(coordinates) >= minimum_knob_count(is_area_section)


def close_area(coordinates: list[Point], is_area_section: bool) -> list[Point]:
    """Append the first coordinate to an area so that it forms a closed polygon."""
    if not is_area_section or not coordinates:
        return list(coordinates)
    if len(coordinates) > 1 and coordinates[0] == coordinates[-1]:
        return list(coordinates)
    return list(coordinates) + [coordinates[0]]


def open_area(coordinates: list[Point], is_area_section: bool) -> list[Point]:
    """Remove the closing coordinate of an area so that every knob is unique.

    The first and the last coordinate of a stored area are equal. To edit the area,
    the closing coordinate has to be removed.
    """
    if is_area_section and len(coordinates) > 1 and coordinates[0] == coordinates[-1]:
        return list(coordinates[:-1])
    return list(coordinates)


def _squared_distance(first: Point, second: Point) -> float:
    return (first[0] - second[0]) ** 2 + (first[1] - second[1]) ** 2


def closest_knob_index(
    coordinates: list[Point], point: Point, radius: float
) -> int | None:
    """Index of the knob closest to the given point within the given radius."""
    closest: int | None = None
    closest_distance = radius**2
    for index, knob in enumerate(coordinates):
        distance = _squared_distance(knob, point)
        if distance <= closest_distance:
            closest = index
            closest_distance = distance
    return closest


def _projection(start: Point, end: Point, point: Point) -> float:
    """Relative position of the point projected onto the segment from start to end.

    0 means the projection is at start, 1 at end. Values outside [0, 1] lie
    outside the segment.
    """
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    squared_length = dx**2 + dy**2
    if squared_length == 0:
        return 0.0
    algebraic_dot = (point[0] - start[0]) * dx + (point[1] - start[1]) * dy
    return algebraic_dot / squared_length


def _squared_distance_to_segment(start: Point, end: Point, point: Point) -> float:
    position = min(max(_projection(start, end, point), 0.0), 1.0)
    closest = (
        start[0] + position * (end[0] - start[0]),
        start[1] + position * (end[1] - start[1]),
    )
    return (closest[0] - point[0]) ** 2 + (closest[1] - point[1]) ** 2


def _segments(coordinates: list[Point], is_area_section: bool) -> list[int]:
    """Indices of the start knobs of all segments of a section."""
    number_of_segments = len(coordinates) - 1
    if is_area_section and len(coordinates) > 2:
        number_of_segments = len(coordinates)
    return list(range(max(number_of_segments, 0)))


def insert_index(coordinates: list[Point], point: Point, is_area_section: bool) -> int:
    """Index at which a new knob at the given point should be inserted.

    The knob is inserted into the segment closest to the point. For line sections,
    points beyond the first or the last knob extend the line at that end.
    """
    segments = _segments(coordinates, is_area_section)
    if not segments:
        return len(coordinates)
    closest_segment = min(
        segments,
        key=lambda index: _squared_distance_to_segment(
            coordinates[index], coordinates[(index + 1) % len(coordinates)], point
        ),
    )
    if not is_area_section:
        start = coordinates[closest_segment]
        end = coordinates[closest_segment + 1]
        projection = _projection(start, end, point)
        if closest_segment == 0 and projection < 0:
            return 0
        if closest_segment == segments[-1] and projection > 1:
            return len(coordinates)
    return closest_segment + 1


def insert_knob(
    coordinates: list[Point], point: Point, is_area_section: bool
) -> tuple[list[Point], int]:
    """Insert a knob at the given point between the closest knobs."""
    index = insert_index(coordinates, point, is_area_section)
    new_coordinates = list(coordinates)
    new_coordinates.insert(index, point)
    return new_coordinates, index


def _swap(coordinates: list[Point], index: int, other: int) -> list[Point]:
    new_coordinates = list(coordinates)
    new_coordinates[index], new_coordinates[other] = (
        new_coordinates[other],
        new_coordinates[index],
    )
    return new_coordinates


def shift_knob_forward(
    coordinates: list[Point], index: int, is_area_section: bool
) -> tuple[list[Point], int]:
    """Move the knob at index one position forward in the order of knobs.

    The last knob of an area wraps around to the start. The last knob of a line
    section cannot be moved forward.
    """
    if not 0 <= index < len(coordinates):
        return list(coordinates), index
    if index == len(coordinates) - 1:
        if not is_area_section:
            return list(coordinates), index
        return _swap(coordinates, index, 0), 0
    return _swap(coordinates, index, index + 1), index + 1


def shift_knob_backward(
    coordinates: list[Point], index: int, is_area_section: bool
) -> tuple[list[Point], int]:
    """Move the knob at index one position backward in the order of knobs.

    The first knob of an area wraps around to the end. The first knob of a line
    section cannot be moved backward.
    """
    if not 0 <= index < len(coordinates):
        return list(coordinates), index
    if index == 0:
        if not is_area_section:
            return list(coordinates), index
        last = len(coordinates) - 1
        return _swap(coordinates, index, last), last
    return _swap(coordinates, index, index - 1), index - 1


def delete_knob(
    coordinates: list[Point], index: int, is_area_section: bool
) -> list[Point]:
    """Delete the knob at index unless the section would have too few knobs."""
    if not 0 <= index < len(coordinates):
        return list(coordinates)
    if len(coordinates) <= minimum_knob_count(is_area_section):
        return list(coordinates)
    new_coordinates = list(coordinates)
    del new_coordinates[index]
    return new_coordinates
