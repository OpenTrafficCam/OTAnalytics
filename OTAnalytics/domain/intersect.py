from abc import ABC, abstractmethod
from typing import Optional

from OTAnalytics.domain.event import Event, EventBuilder
from OTAnalytics.domain.geometry import Coordinate, Line, Polygon
from OTAnalytics.domain.section import Area, LineSection
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
    def distance_coord_coord(self, p1: Coordinate, p2: Coordinate) -> float:
        pass


class Intersector(ABC):
    @abstractmethod
    def __init__(self, implementation: IntersectImplementation) -> None:
        self.implementation = implementation

    @abstractmethod
    def intersect(
        self, track: Track, event_builder: EventBuilder
    ) -> Optional[list[Event]]:
        """Defines interface to intersect a section with a detection.

        Returns:
            bool: `True` if section intersects with coordinate. Otherwise `False`.
        """
        pass


class LineSectionIntersector(Intersector):
    """Determines whether a line section intersects with a detection.

    Args:
        implementation (IntersectorImplementation): the intersection implementation.
        line (LineSection): the line to intersect with.
        detection (Detection): the detection to intersect with.
    """

    @abstractmethod
    def __init__(
        self,
        implementation: IntersectImplementation,
        line_section: LineSection,
    ) -> None:
        super().__init__(implementation)
        self._line_section = line_section


class IntersectBySingleTrackLine(LineSectionIntersector):
    def __init__(
        self, implementation: IntersectImplementation, line_section: LineSection
    ) -> None:
        super().__init__(implementation, line_section)

    def intersect(
        self, track: Track, event_builder: EventBuilder
    ) -> Optional[list[Event]]:
        line_section_as_geometry = Line(
            [self._line_section.start, self._line_section.end]
        )
        track_as_geometry = Line(
            [Coordinate(detection.x, detection.y) for detection in track.detections]
        )

        splitted_lines = self.implementation.split_line_with_line(
            track_as_geometry, line_section_as_geometry
        )

        if splitted_lines:
            events: list[Event] = []
            current_idx = len(splitted_lines[0].coordinates)
            for n, splitted_line in enumerate(splitted_lines[1:], start=1):
                # Subtract by 2n to account for intersection points
                detection_index = current_idx - 2 * n + 1
                selected_detection = track.detections[detection_index]
                events.append(event_builder.create_event(selected_detection))
                current_idx += len(splitted_line.coordinates)
            return events

        return None


class IntersectBySmallTrackComponents(LineSectionIntersector):
    """Determines whether a line section intersects with a detection.

    Args:
        implementation (IntersectorImplementation): the intersection implementation.
        line (LineSection): the line to intersect with.
        detection (Detection): the detection to intersect with.
    """

    def __init__(
        self, implementation: IntersectImplementation, line_section: LineSection
    ) -> None:
        super().__init__(implementation, line_section)

    def intersect(
        self, track: Track, event_builder: EventBuilder
    ) -> Optional[list[Event]]:
        line_section_as_geometry = Line(
            [self._line_section.start, self._line_section.end]
        )

        if not self._track_line_intersects_section(track, line_section_as_geometry):
            return None

        events: list[Event] = []

        for first_detection, second_detection in zip(
            track.detections[0:-1], track.detections[1:]
        ):
            detection_as_geometry = Line(
                [
                    Coordinate(first_detection.x, first_detection.y),
                    Coordinate(second_detection.x, second_detection.y),
                ]
            )
            intersects = self.implementation.line_intersects_line(
                line_section_as_geometry, detection_as_geometry
            )
            if intersects:
                events.append(event_builder.create_event(first_detection))

        if events:
            return events

        return None

    def _track_line_intersects_section(self, track: Track, line_section: Line) -> bool:
        """Whether a track line defined by all its detections intersects the section"""
        track_as_geometry = Line(
            [Coordinate(detection.x, detection.y) for detection in track.detections]
        )

        intersects = self.implementation.line_intersects_line(
            line_section, track_as_geometry
        )
        return intersects


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

    def intersect(
        self, track: Track, event_builder: EventBuilder
    ) -> Optional[list[Event]]:
        """Intersect area with a detection.

        Returns:
            bool: `True` if area intersects detection. Otherwise `False`.
        """
        area_as_geometry = Polygon(self._area.coordinates)
        intersected_detections: list[Detection] = []
        for first_detection, second_detection in zip(
            track.detections[0:-1], track.detections[1:]
        ):
            detection_as_geometry = Line(
                [
                    Coordinate(first_detection.x, first_detection.y),
                    Coordinate(second_detection.x, second_detection.y),
                ]
            )
            intersects = self.implementation.line_intersects_polygon(
                detection_as_geometry, area_as_geometry
            )
            if intersects:
                intersected_detections.append(first_detection)

        if intersected_detections:
            selected_detection = intersected_detections[0]
            return [event_builder.create_event(selected_detection)]

        return None
