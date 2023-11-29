from functools import singledispatchmethod
from typing import Callable, Iterable

from shapely import LineString, Polygon

from OTAnalytics.application.analysis.intersect import (
    RunIntersect,
    group_sections_by_offset,
)
from OTAnalytics.application.geometry import GeometryBuilder
from OTAnalytics.application.use_cases.track_repository import GetAllTracks
from OTAnalytics.domain.event import Event, EventBuilder, SectionEventBuilder
from OTAnalytics.domain.geometry import (
    DirectionVector2D,
    RelativeOffsetCoordinate,
    apply_offset,
    calculate_direction_vector,
)
from OTAnalytics.domain.intersect import Intersector, IntersectParallelizationStrategy
from OTAnalytics.domain.section import Area, IntersectionVisitor, LineSection, Section
from OTAnalytics.domain.track import Track, TrackDataset, TrackId
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


class IntersectionError(Exception):
    pass


class ShapelyIntersectBySmallestTrackSegments(Intersector):
    """
    Implements the intersection strategy by splitting up the track in its smallest
    segments and intersecting each of them with the section.

    The smallest segment of a track is to generate a Line with the coordinates of
    two neighboring detections in the track.

    """

    def __init__(
        self,
        calculate_direction_vector_: Callable[
            [float, float, float, float], DirectionVector2D
        ] = calculate_direction_vector,
    ) -> None:
        self._calculate_direction_vector = calculate_direction_vector_

    def intersect(
        self,
        track_dataset: TrackDataset,
        sections: Iterable[Section],
        event_builder: EventBuilder,
    ) -> list[Event]:
        sections_grouped_by_offset = group_sections_by_offset(
            sections, EventType.SECTION_ENTER
        )
        events = []
        for offset, section_group in sections_grouped_by_offset.items():
            events.extend(
                self.__do_intersect(track_dataset, section_group, offset, event_builder)
            )
        return events

    def __do_intersect(
        self,
        track_dataset: TrackDataset,
        sections: list[Section],
        offset: RelativeOffsetCoordinate,
        event_builder: EventBuilder,
    ) -> list[Event]:
        intersection_result = track_dataset.intersection_points(sections, offset)

        events: list[Event] = []
        for track_id, intersection_points in intersection_result.items():
            if not (track := track_dataset.get_for(track_id)):
                raise IntersectionError(
                    "Track not found. Unable to create intersection event "
                    f"for track {track_id}."
                )
            event_builder.add_road_user_type(track.classification)
            for section_id, intersection_point in intersection_points:
                event_builder.add_section_id(section_id)
                detection = track.detections[intersection_point.index]
                current_coord = detection.get_coordinate(offset)
                prev_coord = track.detections[
                    intersection_point.index - 1
                ].get_coordinate(offset)
                direction_vector = self._calculate_direction_vector(
                    prev_coord.x,
                    prev_coord.y,
                    current_coord.x,
                    current_coord.y,
                )
                event_builder.add_event_type(EventType.SECTION_ENTER)
                event_builder.add_direction_vector(direction_vector)
                event_builder.add_event_coordinate(detection.x, detection.y)
                events.append(event_builder.create_event(detection))
        return events


class ShapelyIntersectAreaByTrackPoints(Intersector):
    def __init__(
        self,
        calculate_direction_vector_: Callable[
            [float, float, float, float], DirectionVector2D
        ] = calculate_direction_vector,
    ) -> None:
        self._calculate_direction_vector = calculate_direction_vector_

    def intersect(
        self,
        track_dataset: TrackDataset,
        sections: Iterable[Section],
        event_builder: EventBuilder,
    ) -> list[Event]:
        sections_grouped_by_offset = group_sections_by_offset(
            sections, EventType.SECTION_ENTER
        )
        events = []
        for offset, section_group in sections_grouped_by_offset.items():
            events.extend(
                self.__do_intersect(track_dataset, section_group, offset, event_builder)
            )
        return events

    def __do_intersect(
        self,
        track_dataset: TrackDataset,
        sections: list[Section],
        offset: RelativeOffsetCoordinate,
        event_builder: EventBuilder,
    ) -> list[Event]:
        contained_by_sections_result = track_dataset.contained_by_sections(
            sections, offset
        )

        events = []
        for (
            track_id,
            contained_by_sections_masks,
        ) in contained_by_sections_result.items():
            if not (track := track_dataset.get_for(track_id)):
                raise IntersectionError(
                    "Track not found. Unable to create intersection event "
                    f"for track {track_id}."
                )
            track_detections = track.detections
            for section_id, section_entered_mask in contained_by_sections_masks:
                event_builder.add_section_id(section_id)
                event_builder.add_road_user_type(track.classification)

                track_starts_inside_area = section_entered_mask[0]
                if track_starts_inside_area:
                    first_detection = track_detections[0]
                    first_coord = first_detection.get_coordinate(offset)
                    second_coord = track_detections[1].get_coordinate(offset)

                    event_builder.add_event_type(EventType.SECTION_ENTER)
                    event_builder.add_direction_vector(
                        self._calculate_direction_vector(
                            first_coord.x,
                            first_coord.y,
                            second_coord.x,
                            second_coord.y,
                        )
                    )
                    event_builder.add_event_coordinate(
                        first_detection.x, first_detection.y
                    )
                    event = event_builder.create_event(first_detection)
                    events.append(event)

                section_currently_entered = track_starts_inside_area
                for current_index, current_detection in enumerate(
                    track_detections[1:], start=1
                ):
                    entered = section_entered_mask[current_index]
                    if section_currently_entered == entered:
                        continue

                    prev_coord = track_detections[current_index - 1].get_coordinate(
                        offset
                    )
                    current_coord = current_detection.get_coordinate(offset)

                    event_builder.add_direction_vector(
                        self._calculate_direction_vector(
                            prev_coord.x,
                            prev_coord.y,
                            current_coord.x,
                            current_coord.y,
                        )
                    )
                    event_builder.add_event_coordinate(current_coord.x, current_coord.y)

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
        track_dataset: TrackDataset,
        sections: Iterable[Section],
        event_builder: SectionEventBuilder,
    ):
        self._intersect_line_section = intersect_line_section
        self._intersect_area_section = intersect_area_section
        self._track_dataset = track_dataset
        self._sections = sections
        self._event_builder = event_builder

    def create(self) -> list[Event]:
        events = []
        line_sections, area_sections = separate_sections(self._sections)
        events.extend(
            self._intersect_line_section.intersect(
                self._track_dataset, line_sections, self._event_builder
            )
        )
        events.extend(
            self._intersect_area_section.intersect(
                self._track_dataset, area_sections, self._event_builder
            )
        )
        return events

    def intersect_line_section(self, section: LineSection) -> list[Event]:
        raise NotImplementedError

    def intersect_area_section(self, section: Area) -> list[Event]:
        raise NotImplementedError


class ShapelyRunIntersect(RunIntersect):
    def __init__(
        self,
        intersect_parallelizer: IntersectParallelizationStrategy,
        get_tracks: GetAllTracks,
    ) -> None:
        self._intersect_parallelizer = intersect_parallelizer
        self._get_tracks = get_tracks

    def __call__(self, sections: Iterable[Section]) -> list[Event]:
        filtered_tracks = self._get_tracks.as_dataset()

        batches = filtered_tracks.split(self._intersect_parallelizer.num_processes)

        tasks = [(batch, sections) for batch in batches]
        return self._intersect_parallelizer.execute(_create_events, tasks)


def _create_events(tracks: TrackDataset, sections: Iterable[Section]) -> list[Event]:
    events = []
    event_builder = SectionEventBuilder()

    create_intersection_events = ShapelyCreateIntersectionEvents(
        intersect_line_section=ShapelyIntersectBySmallestTrackSegments(),
        intersect_area_section=ShapelyIntersectAreaByTrackPoints(),
        track_dataset=tracks,
        sections=sections,
        event_builder=event_builder,
    )
    events.extend(create_intersection_events.create())
    return events


def separate_sections(
    sections: Iterable[Section],
) -> tuple[Iterable[LineSection], Iterable[Area]]:
    line_sections = []
    area_sections = []
    for section in sections:
        if isinstance(section, LineSection):
            line_sections.append(section)
        elif isinstance(section, Area):
            area_sections.append(section)
        else:
            raise TypeError(
                "Unable to separate section. "
                f"Unknown section type for section {section.name} "
                f"with type {type(section)}"
            )

    return line_sections, area_sections
