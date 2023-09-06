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
