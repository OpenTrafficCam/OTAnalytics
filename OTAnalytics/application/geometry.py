from abc import ABC, abstractmethod
from functools import singledispatchmethod
from typing import Generic, Iterable, TypeVar

from OTAnalytics.domain.geometry import (
    Coordinate,
    Line,
    Polygon,
    RelativeOffsetCoordinate,
)
from OTAnalytics.domain.section import Section
from OTAnalytics.domain.track import Track


class SectionGeometryBuilder:
    def build_as_line(self, section: Section) -> Line:
        return Line(section.get_coordinates())

    def build_as_polygon(self, section: Section) -> Polygon:
        return Polygon(section.get_coordinates())


class TrackGeometryBuilder:
    def build(self, track: Track, offset: RelativeOffsetCoordinate) -> Line:
        coordinates = [
            Coordinate(
                detection.x + offset.x * detection.w,
                detection.y + offset.y * detection.h,
            )
            for detection in track.detections
        ]
        return Line(coordinates)


LINE = TypeVar("LINE")
AREA = TypeVar("AREA")


class GeometryBuilder(ABC, Generic[LINE, AREA]):
    @singledispatchmethod
    @abstractmethod
    def create_section(self) -> LINE | AREA:
        raise NotImplementedError

    @abstractmethod
    def create_track(self, track: Track, offset: RelativeOffsetCoordinate) -> LINE:
        raise NotImplementedError

    @abstractmethod
    def create_line_segments(self, geometry: LINE) -> Iterable[LINE]:
        raise NotImplementedError
