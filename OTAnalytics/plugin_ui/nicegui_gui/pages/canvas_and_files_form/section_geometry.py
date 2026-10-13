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
