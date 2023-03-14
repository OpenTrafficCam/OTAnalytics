from abc import ABC, abstractmethod
from typing import Optional

from OTAnalytics.domain.event import Event, EventBuilder
from OTAnalytics.domain.geometry import Coordinate, Line, Polygon
from OTAnalytics.domain.section import Area, LineSection
from OTAnalytics.domain.track import Detection, Track


class IntersectImplementation(ABC):
    @abstractmethod
    def line_intersects_line(self, line_1: Line, line_2: Line) -> bool:
        pass

    @abstractmethod
    def line_intersects_polygon(self, line: Line, polygon: Polygon) -> bool:
        pass


class Intersector(ABC):
    @abstractmethod
    def __init__(self, implementation: IntersectImplementation) -> None:
        self.implementation = implementation

    @abstractmethod
    def intersect(self, track: Track, event_builder: EventBuilder) -> Optional[Event]:
        """Defines interface to intersect a section with a detection.

        Returns:
            bool: `True` if section intersects with coordinate. Otherwise `False`.
        """
        pass


class LineSectionTrackIntersector(Intersector):
    """Determines whether a line section intersects with a detection.

    Args:
        implementation (IntersectorImplementation): the intersection implementation.
        line (LineSection): the line to intersect with.
        detection (Detection): the detection to intersect with.
    """

    def __init__(
        self,
        implementation: IntersectImplementation,
        line_section: LineSection,
    ) -> None:
        super().__init__(implementation)
        self._line_section = line_section

    def intersect(self, track: Track, event_builder: EventBuilder) -> Optional[Event]:
        line_section_as_geometry = Line(
            self._line_section.start, self._line_section.end
        )
        intersected_detections = []
        for first_detection, second_detection in zip(
            track.detections[0:-1], track.detections[1:]
        ):
            detection_as_geometry = Line(
                Coordinate(first_detection.x + first_detection.w, first_detection.y),
                Coordinate(second_detection.x + second_detection.w, second_detection.y),
            )
            intersects = self.implementation.line_intersects_line(
                line_section_as_geometry, detection_as_geometry
            )
            if intersects:
                intersected_detections.append(first_detection)

        if intersected_detections:
            selected_detection = intersected_detections[0]
            return event_builder.create_event(selected_detection)

        return None


class AreaTrackIntersector(Intersector):
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

    def intersect(self, track: Track, event_builder: EventBuilder) -> Optional[Event]:
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
                Coordinate(first_detection.x, first_detection.y),
                Coordinate(second_detection.x, second_detection.y),
            )
            intersects = self.implementation.line_intersects_polygon(
                detection_as_geometry, area_as_geometry
            )
            if intersects:
                intersected_detections.append(first_detection)

        if intersected_detections:
            selected_detection = intersected_detections[0]
            return event_builder.create_event(selected_detection)

        return None
