from functools import singledispatchmethod
from typing import Callable, Iterable

from shapely import LineString, Polygon

from OTAnalytics.application.geometry import GeometryBuilder
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate, apply_offset
from OTAnalytics.domain.section import Area, LineSection
from OTAnalytics.domain.track import Track, TrackId


class ShapelyGeometryBuilder(GeometryBuilder[LineString, Polygon]):
    def __init__(
        self,
        apply_offset_: Callable[
            [float, float, float, float, RelativeOffsetCoordinate], tuple[float, float]
        ] = apply_offset,
    ):
        self._apply_offset = apply_offset_

    @singledispatchmethod
    def create_section(self) -> LineString | Polygon:
        raise NotImplementedError

    @create_section.register
    def _(self, section: LineSection) -> LineString:
        return LineString([(coord.x, coord.y) for coord in section.get_coordinates()])

    @create_section.register
    def _(self, section: Area) -> Polygon:
        return Polygon([(coord.x, coord.y) for coord in section.get_coordinates()])

    def create_track(
        self, track: Track, offset: RelativeOffsetCoordinate
    ) -> LineString:
        return LineString(
            [
                self._apply_offset(
                    detection.x, detection.y, detection.w, detection.h, offset
                )
                for detection in track.detections
            ]
        )

    def create_line_segments(self, geometry: LineString) -> Iterable[LineString]:
        line_segments: list[LineString] = []

        for _current, _next in zip(geometry.coords[0:-1], geometry.coords[1:]):
            line_segments.append(LineString([_current, _next]))
        return line_segments


class ShapelyTrackLookupTable:
    def __init__(
        self,
        lookup_table: dict[TrackId, LineString],
        geometry_builder: GeometryBuilder[LineString, Polygon],
        offset: RelativeOffsetCoordinate,
    ):
        self._table = lookup_table
        self._geometry_builder = geometry_builder
        self._offset = offset

    def look_up(self, track: Track) -> LineString:
        if line := self._table.get(track.id):
            return line
        new_line = self._geometry_builder.create_track(track, self._offset)

        self._table[track.id] = new_line
        return new_line
