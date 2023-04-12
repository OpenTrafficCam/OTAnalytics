from abc import ABC, abstractmethod
from typing import Optional

from OTAnalytics.domain.event import Event, EventBuilder, EventType
from OTAnalytics.domain.geometry import (
    Coordinate,
    DirectionVector2D,
    Line,
    Polygon,
    RelativeOffsetCoordinate,
    calculate_direction_vector,
)
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
    def _calculate_direction_vector(
        first: Detection, second: Detection
    ) -> DirectionVector2D:
        """Calculate direction vector from two detections.

        The direction vector will be calculated by taking the x and y values of the
        detection's bounding box.

        Args:
            first (Detection): the first detection
            second (Detection): the second detection

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


class IntersectBySplittingTrackLine(LineSectionIntersector):
    """
    Implements the intersection strategy by splitting a track with the section.

    Args:
        implementation (IntersectorImplementation): the intersection implementation
        line (LineSection): the line to intersect with
    """

    def __init__(
        self, implementation: IntersectImplementation, line_section: LineSection
    ) -> None:
        super().__init__(implementation, line_section)

    def intersect(self, track: Track, event_builder: EventBuilder) -> list[Event]:
        line_section_as_geometry = Line(
            [self._line_section.start, self._line_section.end]
        )
        if event_builder.event_type is None:
            raise ValueError("Event type not set in section builder")

        offset = self._line_section.relative_offset_coordinates[
            event_builder.event_type
        ]

        track_as_geometry = Line(
            [
                self._select_coordinate_in_detection(detection, offset)
                for detection in track.detections
            ]
        )

        splitted_lines = self.implementation.split_line_with_line(
            track_as_geometry, line_section_as_geometry
        )
        event_builder.add_road_user_type(track.classification)

        events: list[Event] = []

        if splitted_lines:
            current_idx = len(splitted_lines[0].coordinates)
            for n, splitted_line in enumerate(splitted_lines[1:], start=1):
                # Subtract by 2n to account for intersection points
                detection_index = current_idx - 2 * n + 1
                selected_detection = track.detections[detection_index]
                previous_detection = track.detections[detection_index - 1]

                event_builder.add_direction_vector(
                    self._calculate_direction_vector(
                        previous_detection, selected_detection
                    )
                )
                events.append(event_builder.create_event(selected_detection))
                current_idx += len(splitted_line.coordinates)
        return events


class IntersectBySmallTrackComponents(LineSectionIntersector):
    """
    Implements the intersection strategy by splitting up the track in its smallest
    components and intersecting each of them with the section.

    The smallest component of a track is to generate a Line with the coordinates of
    two neighboring detections in the track.

    Args:
        implementation (IntersectorImplementation): the intersection implementation
        line (LineSection): the line to intersect with
    """

    def __init__(
        self, implementation: IntersectImplementation, line_section: LineSection
    ) -> None:
        super().__init__(implementation, line_section)

    def intersect(self, track: Track, event_builder: EventBuilder) -> list[Event]:
        events: list[Event] = []

        line_section_as_geometry = Line(
            [self._line_section.start, self._line_section.end]
        )
        if not self._track_line_intersects_section(track, line_section_as_geometry):
            return events

        event_builder.add_road_user_type(track.classification)
        if event_builder.event_type is None:
            raise ValueError("Event type not set in section builder")

        offset = self._line_section.relative_offset_coordinates[
            event_builder.event_type
        ]

        for current_detection, next_detection in zip(
            track.detections[0:-1], track.detections[1:]
        ):
            detection_as_geometry = Line(
                [
                    self._select_coordinate_in_detection(current_detection, offset),
                    self._select_coordinate_in_detection(next_detection, offset),
                ]
            )
            intersects = self.implementation.line_intersects_line(
                line_section_as_geometry, detection_as_geometry
            )
            if intersects:
                event_builder.add_direction_vector(
                    self._calculate_direction_vector(current_detection, next_detection)
                )
                events.append(event_builder.create_event(next_detection))
        return events

    def _track_line_intersects_section(self, track: Track, line_section: Line) -> bool:
        """Whether a track line defined by all its detections intersects the section"""
        track_as_geometry = Line(
            [Coordinate(detection.x, detection.y) for detection in track.detections]
        )

        return self.implementation.line_intersects_line(line_section, track_as_geometry)


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


class IntersectAreaByTrackPoints(AreaIntersector):
    def __init__(self, implementation: IntersectImplementation, area: Area) -> None:
        super().__init__(implementation, area)

    def intersect(self, track: Track, event_builder: EventBuilder) -> list[Event]:
        """Intersect area with a detection.

        Returns:
            bool: `True` if area intersects detection. Otherwise `False`.
        """
        area_as_polygon = Polygon(self._area.coordinates)
        offset = self._area.relative_offset_coordinates[EventType.SECTION_ENTER]

        track_coordinates: list[Coordinate] = [
            self._select_coordinate_in_detection(detection, offset)
            for detection in track.detections
        ]
        mask = self.implementation.are_coordinates_within_polygon(
            track_coordinates, area_as_polygon
        )
        events: list[Event] = []

        event_builder.add_road_user_type(track.classification)
        track_starts_inside_area = mask[0]

        if track_starts_inside_area:
            first_detection = track.detections[0]
            second_detection = track.detections[1]

            event_builder.add_event_type(EventType.SECTION_ENTER)
            event_builder.add_road_user_type(first_detection.classification)
            event_builder.add_direction_vector(
                self._calculate_direction_vector(first_detection, second_detection)
            )
            event = event_builder.create_event(first_detection)
            events.append(event)

        section_currently_entered = track_starts_inside_area
        for index, (current_detection, entered) in enumerate(
            zip(track.detections[1:], mask[1:]), start=1
        ):
            if section_currently_entered == entered:
                continue
            prev_detection = track.detections[index - 1]

            event_builder.add_direction_vector(
                self._calculate_direction_vector(prev_detection, current_detection)
            )

            if entered:
                event_builder.add_event_type(EventType.SECTION_ENTER)
            else:
                event_builder.add_event_type(EventType.SECTION_LEAVE)

            event = event_builder.create_event(current_detection)
            events.append(event)
            section_currently_entered = entered

        return events
