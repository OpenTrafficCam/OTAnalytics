from abc import ABC, abstractmethod
from typing import Callable, Iterable, Optional

from OTAnalytics.domain.event import Event, EventBuilder, EventType
from OTAnalytics.domain.geometry import (
    Coordinate,
    DirectionVector2D,
    Line,
    Polygon,
    RelativeOffsetCoordinate,
    calculate_direction_vector,
)
from OTAnalytics.domain.section import Area, LineSection, Section
from OTAnalytics.domain.track import Detection, Track


class IntersectImplementation(ABC):
    @abstractmethod
    def line_intersects_line(self, line_1: Line, line_2: Line) -> bool:
        """Checks if a line intersects with another line.

        Args:
            line_1 (Line): the line to be intersected.
            line_2 (Line): the other line to be intersected.

        Returns:
            bool: `True` if the lines intersect with other. Otherwise `False`.
        """
        pass

    @abstractmethod
    def line_intersects_polygon(self, line: Line, polygon: Polygon) -> bool:
        """Checks if a line intersects with a polygon.

        Args:
            line (Line): the line to be intersected.
            polygon (Polygon): the polygon to be intersected.

        Returns:
            bool: `True` if the line and polygon intersect with each other.
                `Otherwise `False`.
        """
        pass

    @abstractmethod
    def split_line_with_line(self, line: Line, splitter: Line) -> Optional[list[Line]]:
        """Splits a line with the help of another line and returns a list of lines.

        If `line` intersects `splitter` then line_1 will be splitted at the
        intersection points.
        I.e. Let line_1 = [p_1, p_2, ..., p_n], n a natural number and p_x
        the intersection point.

        Then `line` will be splitted as follows:
        [[p_1, p_2, ..., p_x], [p_x, p_(x+1), ..., p_n].

        Args:
            line (Line): the line to be splitted.
            splitter (Line): the line used for the splitting.

        Returns:
            Optional[list[Line]]: The splitted lines. Otherwise `None` if no
                intersection exists.
        """
        pass

    @abstractmethod
    def distance_between(
        self, coordinate_1: Coordinate, coordinate_2: Coordinate
    ) -> float:
        """Returns the distance between two coordinates.

        Args:
            coordinate_1 (Coordinate): the first coordinate
            coordinate_2 (Coordinate): the second coordinate

        Returns:
            float: the distance
        """
        pass

    @abstractmethod
    def are_coordinates_within_polygon(
        self, coordinates: list[Coordinate], polygon: Polygon
    ) -> list[bool]:
        """Checks if coordinates are within a polygon.

        A coordinate is within a polygon if it is enclosed by it. Meaning that a point
        sitting on the boundary of a polygon is treated as not being within it.

        Args:
            coordinates (list[Coordinate]): the coordinates to check if they are
                contained by the polygon
            polygon (Polygon): the polygon

        Returns:
            list[bool]: the boolean mask holding information whether a point is within
                a polygon or not
        """
        pass


class IntersectParallelizationStrategy(ABC):
    @abstractmethod
    def execute(
        self,
        intersect: Callable[
            [Track, Iterable[Section]],
            Iterable[Event],
        ],
        tracks: Iterable[Track],
        sections: Iterable[Section],
    ) -> list[Event]:
        """Executes the intersection of tracks with sections with the implemented
        parallelization strategy.

        Args:
            intersect (Callable[[Track, Iterable[Section]], Iterable[Event]]): the
                function to be executed on an iterable of tracks and sections.
            tracks (Iterable[Track]): the tracks to be processed.
            sections (Iterable[Section]): the sections to be processed.

        Returns:
            Iterable[Event]: the generated events.
        """
        pass


class Intersector(ABC):
    """
    Defines an interface to implement a family of algorithms to intersect tracks
    with sections.

    Args:
        implementation (IntersectImplementation): the intersection implementation
    """

    @abstractmethod
    def __init__(self, implementation: IntersectImplementation) -> None:
        self.implementation = implementation

    @abstractmethod
    def intersect(self, track: Track, event_builder: EventBuilder) -> list[Event]:
        """Intersect tracks with sections and generate events if they intersect.

        Args:
            track (Track): the track
            event_builder (EventBuilder): builder to generate events

        Returns:
            list[Event]: the events if the track intersects with the section.
                Otherwise return empty list.
        """
        pass

    @staticmethod
    def _select_coordinate_in_detection(
        detection: Detection, offset: RelativeOffsetCoordinate
    ) -> Coordinate:
        """Select a coordinate within the bounding box of a detection.

        A coordinate within the bounding box of a detection is selected by applying the
        offset.

        Args:
            detection (Detection): the detection containing the bounding box dimensions
            offset (RelativeOffsetCoordinate): the offset to include in the selection
                of the coordinate

        Returns:
            Coordinate: the coordinate
        """
        return Coordinate(
            x=detection.x + detection.w * offset.x,
            y=detection.y + detection.h * offset.y,
        )

    @staticmethod
    def _extract_offset_from_section(
        section: Section, offset_type: EventType
    ) -> RelativeOffsetCoordinate:
        """Extract the section offset.

        Args:
            section (Section): the section to extract the offset from
            offset_type (EventType): the type offset to extract

        Returns:
            RelativeOffsetCoordinate: the extracted offset
        """
        return section.relative_offset_coordinates[offset_type]

    @staticmethod
    def _calculate_direction_vector(
        first: Coordinate, second: Coordinate
    ) -> DirectionVector2D:
        """Calculate direction vector from two coordinates.

        Args:
            first (Coordinate): the first coordinate
            second (Coordinate): the second coordinate

        Returns:
            DirectionVector2D: the direction vector
        """
        result = calculate_direction_vector(first.x, first.y, second.x, second.y)
        return result


class LineSectionIntersector(Intersector):
    """Determines whether a line section intersects with a track.

    Args:
        implementation (IntersectorImplementation): the intersection implementation
        line (LineSection): the line to intersect with
    """

    @abstractmethod
    def __init__(
        self,
        implementation: IntersectImplementation,
        line_section: LineSection,
    ) -> None:
        super().__init__(implementation)
        self._line_section = line_section


class AreaIntersector(Intersector):
    """Determines whether an area intersects with a track.

    Args:
        implementation (IntersectorImplementation): the intersection implementation.
        area (Area): the area to intersect with.
        detection (Detection): the detection to intersect with.
    """

    def __init__(
        self,
        implementation: IntersectImplementation,
        area: Area,
    ) -> None:
        super().__init__(implementation)
        self._area = area
