from datetime import datetime
from typing import Callable, Iterable, Protocol

from OTAnalytics.application.analysis.intersect import (
    IntersectionError,
    RunIntersect,
    group_sections_by_offset,
)
from OTAnalytics.domain.event import Event, EventBuilder, SectionEventBuilder
from OTAnalytics.domain.geometry import (
    Coordinate,
    DirectionVector2D,
    RelativeOffsetCoordinate,
    calculate_direction_vector,
)
from OTAnalytics.domain.intersect import Intersector, IntersectParallelizationStrategy
from OTAnalytics.domain.section import Area, LineSection, Section
from OTAnalytics.domain.track_dataset.track_dataset import TrackDataset
from OTAnalytics.domain.types import EventType


class IntersectByIntersectionPoints(Intersector):
    """Use intersection points of tracks and sections to create events.

    This strategy is intended to be used with LineSections.
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
                detection = track.get_detection(intersection_point.upper_index)
                previous_detection = track.get_detection(intersection_point.lower_index)
                current_coord = detection.get_coordinate(offset)
                prev_coord = previous_detection.get_coordinate(offset)
                direction_vector = self._calculate_direction_vector(
                    prev_coord.x,
                    prev_coord.y,
                    current_coord.x,
                    current_coord.y,
                )
                interpolated_occurrence = self._get_interpolated_occurrence(
                    previous=previous_detection.occurrence,
                    current=detection.occurrence,
                    relative_position=intersection_point.relative_position,
                )
                interpolated_event_coordinate = self._get_interpolated_event_coordinate(
                    previous=prev_coord,
                    current=current_coord,
                    relative_position=intersection_point.relative_position,
                )
                event_builder.add_event_type(EventType.SECTION_ENTER)
                event_builder.add_direction_vector(direction_vector)
                event_builder.add_event_coordinate(current_coord.x, current_coord.y)
                event_builder.add_interpolated_occurrence(interpolated_occurrence)
                event_builder.add_interpolated_event_coordinate(
                    interpolated_event_coordinate.x, interpolated_event_coordinate.y
                )
                events.append(event_builder.create_event(detection))

        return events

    def _get_interpolated_occurrence(
        self, previous: datetime, current: datetime, relative_position: float
    ) -> datetime:
        return previous + (current - previous) * relative_position

    def _get_interpolated_event_coordinate(
        self, previous: Coordinate, current: Coordinate, relative_position: float
    ) -> Coordinate:
        interpolated_x = previous.x + relative_position * (current.x - previous.x)
        interpolated_y = previous.y + relative_position * (current.y - previous.y)
        return Coordinate(interpolated_x, interpolated_y)


class IntersectAreaByTrackPoints(Intersector):
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
                    event_builder.add_interpolated_event_coordinate(
                        current_coord.x, current_coord.y
                    )
                    event_builder.add_interpolated_occurrence(
                        current_detection.occurrence
                    )

                    if entered:
                        event_builder.add_event_type(EventType.SECTION_ENTER)
                    else:
                        event_builder.add_event_type(EventType.SECTION_LEAVE)

                    event = event_builder.create_event(current_detection)
                    events.append(event)
                    section_currently_entered = entered

        return events


class RunCreateIntersectionEvents:
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


class GetTracks(Protocol):
    def as_dataset(self) -> TrackDataset: ...


class BatchedTracksRunIntersect(RunIntersect):
    def __init__(
        self,
        intersect_parallelizer: IntersectParallelizationStrategy,
        get_tracks: GetTracks,
    ) -> None:
        self._intersect_parallelizer = intersect_parallelizer
        self._get_tracks = get_tracks

    def __call__(self, sections: Iterable[Section]) -> list[Event]:
        filtered_tracks = self._get_tracks.as_dataset()
        filtered_tracks.calculate_geometries_for(
            {_section.get_offset(EventType.SECTION_ENTER) for _section in sections}
        )

        batches = filtered_tracks.split(self._intersect_parallelizer.num_processes)

        tasks = [(batch, sections) for batch in batches]
        return self._intersect_parallelizer.execute(_create_events, tasks)


def _create_events(tracks: TrackDataset, sections: Iterable[Section]) -> list[Event]:
    events = []
    event_builder = SectionEventBuilder()

    create_intersection_events = RunCreateIntersectionEvents(
        intersect_line_section=IntersectByIntersectionPoints(),
        intersect_area_section=IntersectAreaByTrackPoints(),
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
