from functools import singledispatchmethod
from typing import Callable, Iterable, Mapping

from shapely import LineString, Polygon, contains_xy, prepare

from OTAnalytics.application.analysis.intersect import RunIntersect
from OTAnalytics.application.geometry import GeometryBuilder
from OTAnalytics.application.use_cases.track_repository import (
    GetTracksWithoutSingleDetections,
)
from OTAnalytics.domain.event import Event, EventBuilder, SectionEventBuilder
from OTAnalytics.domain.geometry import (
    DirectionVector2D,
    RelativeOffsetCoordinate,
    apply_offset,
    calculate_direction_vector,
)
from OTAnalytics.domain.intersect import Intersector, IntersectParallelizationStrategy
from OTAnalytics.domain.section import Area, IntersectionVisitor, LineSection, Section
from OTAnalytics.domain.track import Track, TrackId
from OTAnalytics.domain.types import EventType


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


class ShapelyIntersectBySmallestTrackSegments(Intersector):
    """
    Implements the intersection strategy by splitting up the track in its smallest
    segments and intersecting each of them with the section.

    The smallest segment of a track is to generate a Line with the coordinates of
    two neighboring detections in the track.

    """

    def __init__(
        self,
        geometry_builder: GeometryBuilder[LineString, Polygon],
        track_lookup_table: ShapelyTrackLookupTable,
        calculate_direction_vector_: Callable[
            [float, float, float, float], DirectionVector2D
        ] = calculate_direction_vector,
    ) -> None:
        self._geometry_builder = geometry_builder
        self._calculate_direction_vector = calculate_direction_vector_
        self._track_table: ShapelyTrackLookupTable = track_lookup_table
        self._segment_lookup_table: dict[TrackId, Iterable[LineString]] = {}

    def _lookup_segment(self, track: Track) -> Iterable[LineString]:
        if segments := self._segment_lookup_table.get(track.id):
            return segments
        track_geometry = self._track_table.look_up(track)
        new_segments = self._geometry_builder.create_line_segments(track_geometry)
        self._segment_lookup_table[track.id] = new_segments
        return new_segments

    def intersect(
        self,
        tracks: Iterable[Track],
        section: Section,
        event_builder: EventBuilder,
    ) -> list[Event]:
        events: list[Event] = []
        section_geometry: LineString = self._geometry_builder.create_section(section)
        for track in tracks:
            track_geometry = self._track_table.look_up(track)
            track_segments = self._lookup_segment(track)
            if not track_geometry.intersects(section_geometry):
                continue
            event_builder.add_road_user_type(track.classification)

            for index, segment in enumerate(track_segments):
                if segment.intersects(section_geometry):
                    x1, y1 = segment.coords[0]
                    x2, y2 = segment.coords[1]
                    direction_vector = self._calculate_direction_vector(x1, y1, x2, y2)
                    event_builder.add_event_type(EventType.SECTION_ENTER)
                    event_builder.add_direction_vector(direction_vector)
                    event_builder.add_event_coordinate(x2, y2)
                    events.append(
                        event_builder.create_event(track.detections[index + 1])
                    )
        return events


class ShapelyIntersectAreaByTrackPoints(Intersector):
    def __init__(
        self,
        geometry_builder: GeometryBuilder[LineString, Polygon],
        track_lookup_table: ShapelyTrackLookupTable,
        calculate_direction_vector_: Callable[
            [float, float, float, float], DirectionVector2D
        ] = calculate_direction_vector,
    ) -> None:
        self._geometry_builder = geometry_builder
        self._calculate_direction_vector = calculate_direction_vector_
        self._track_table = track_lookup_table

    def intersect(
        self, tracks: Iterable[Track], section: Section, event_builder: EventBuilder
    ) -> list[Event]:
        events = []

        section_geometry = self._geometry_builder.create_section(section)
        prepare(section_geometry)

        for track in tracks:
            track_coordinates = self._track_table.look_up(track).coords
            section_entered_mask = contains_xy(section_geometry, track_coordinates)

            track_starts_inside_area = section_entered_mask[0]
            event_builder.add_road_user_type(track.classification)
            if track_starts_inside_area:
                first_detection = track.first_detection
                first_coord_x, first_coord_y = track_coordinates[0]
                second_coord_x, second_coord_y = track_coordinates[1]
                event_builder.add_event_type(EventType.SECTION_ENTER)
                event_builder.add_direction_vector(
                    self._calculate_direction_vector(
                        first_coord_x, first_coord_y, second_coord_x, second_coord_y
                    )
                )
                event_builder.add_event_coordinate(first_coord_x, first_coord_y)
                event = event_builder.create_event(first_detection)
                events.append(event)

            section_currently_entered = track_starts_inside_area

            for current_index, current_detection in enumerate(
                track.detections[1:], start=1
            ):
                entered = section_entered_mask[current_index]
                if section_currently_entered == entered:
                    continue
                current_x, current_y = track_coordinates[current_index]
                prev_x, prev_y = track_coordinates[current_index - 1]

                event_builder.add_direction_vector(
                    self._calculate_direction_vector(
                        prev_x, prev_y, current_x, current_y
                    )
                )
                event_builder.add_event_coordinate(current_x, current_y)

                if entered:
                    event_builder.add_event_type(EventType.SECTION_ENTER)
                else:
                    event_builder.add_event_type(EventType.SECTION_LEAVE)

                event = event_builder.create_event(current_detection)
                events.append(event)
                section_currently_entered = entered

        return events


class ShapelyCreateIntersectionEvents(IntersectionVisitor[Event]):
    def __init__(
        self,
        intersect_line_section: Intersector,
        intersect_area_section: Intersector,
        geometry_builder: GeometryBuilder,
        tracks: Iterable[Track],
        sections: Iterable[Section],
        event_builder: SectionEventBuilder,
    ):
        self._intersect_line_section = intersect_line_section
        self._intersect_area_section = intersect_area_section
        self._geometry_builder = geometry_builder
        self._tracks = tracks
        self._sections = sections
        self._event_builder = event_builder

    def create(self) -> list[Event]:
        events = []

        for section in self._sections:
            events.extend(section.accept(self))
        return events

    def intersect_line_section(self, section: LineSection) -> list[Event]:
        self._event_builder.add_section_id(section.id)
        return self._intersect_line_section.intersect(
            self._tracks, section, self._event_builder
        )

    def intersect_area_section(self, section: Area) -> list[Event]:
        self._event_builder.add_section_id(section.id)
        return self._intersect_area_section.intersect(
            self._tracks, section, self._event_builder
        )


class ShapelyRunIntersect(RunIntersect):
    def __init__(
        self,
        intersect_parallelizer: IntersectParallelizationStrategy,
        get_tracks: GetTracksWithoutSingleDetections,
    ) -> None:
        self._intersect_parallelizer = intersect_parallelizer
        self._get_tracks = get_tracks

    def __call__(self, sections: Iterable[Section]) -> list[Event]:
        filtered_tracks = self._get_tracks.as_dataset()

        batches = filtered_tracks.split(self._intersect_parallelizer.num_processes)

        tasks = [(batch, sections) for batch in batches]
        return self._intersect_parallelizer.execute(_create_events, tasks)


def _create_events(tracks: Iterable[Track], sections: Iterable[Section]) -> list[Event]:
    grouped_sections = group_sections_by_offset(sections)
    events = []
    for offset, section_group in grouped_sections.items():
        geometry_builder = ShapelyGeometryBuilder()
        track_lookup_table = ShapelyTrackLookupTable(dict(), geometry_builder, offset)
        line_section_intersection_strategy = ShapelyIntersectBySmallestTrackSegments(
            geometry_builder, track_lookup_table
        )
        area_section_intersection_strategy = ShapelyIntersectAreaByTrackPoints(
            geometry_builder, track_lookup_table
        )
        event_builder = SectionEventBuilder()

        create_intersection_events = ShapelyCreateIntersectionEvents(
            intersect_line_section=line_section_intersection_strategy,
            intersect_area_section=area_section_intersection_strategy,
            geometry_builder=geometry_builder,
            tracks=tracks,
            sections=section_group,
            event_builder=event_builder,
        )
        events.extend(create_intersection_events.create())
    return events


def group_sections_by_offset(
    sections: Iterable[Section],
) -> Mapping[RelativeOffsetCoordinate, Iterable[Section]]:
    grouped_sections: dict[RelativeOffsetCoordinate, list[Section]] = {}
    for section in sections:
        offset = section.get_offset(EventType.SECTION_ENTER)
        if section_group := grouped_sections.get(offset, []):
            section_group.append(section)
        else:
            grouped_sections[offset] = [section]
    return grouped_sections
