from datetime import datetime
from unittest.mock import Mock

import pytest

from OTAnalytics.application.analysis.traffic_counting import (
    CounterFilter,
    FilteredCounter,
    GroupedCount,
    GroupedCounter,
    SimpleCount,
    SimpleCounter,
    TrafficCounter,
)
from OTAnalytics.domain.event import Event
from OTAnalytics.domain.flow import Flow, FlowId
from OTAnalytics.domain.geometry import DirectionVector2D, ImageCoordinate
from OTAnalytics.domain.section import Section, SectionId
from OTAnalytics.domain.track import TrackId
from OTAnalytics.domain.types import EventType


def create_event(
    track_id: TrackId,
    section: SectionId,
) -> Event:
    return Event(
        road_user_id=track_id.id,
        road_user_type="car",
        hostname="my_hostname",
        occurrence=datetime(2020, 1, 1, 0, 0, 0),
        frame_number=1,
        section_id=section,
        event_coordinate=ImageCoordinate(0, 0),
        event_type=EventType.SECTION_ENTER,
        direction_vector=DirectionVector2D(x1=1, x2=1),
        video_name="my_video_name.mp4",
    )


def create_test_cases() -> list[tuple]:
    first_track = TrackId(1)
    second_track = TrackId(2)
    third_track = TrackId(3)
    forth_track = TrackId(4)
    fifth_track = TrackId(5)
    sixth_track = TrackId(6)
    south_section_id = SectionId("south")
    north_section_id = SectionId("north")
    west_section_id = SectionId("west")
    east_section_id = SectionId("east")
    south_section = Mock(spec=Section)
    north_section = Mock(spec=Section)
    west_section = Mock(spec=Section)
    east_section = Mock(spec=Section)
    south_section.id = south_section_id
    north_section.id = north_section_id
    west_section.id = west_section_id
    east_section.id = east_section_id
    south_to_north_id = FlowId("south to north")
    south_to_north = Flow(
        south_to_north_id,
        start=south_section,
        end=north_section,
        distance=10,
    )
    south_to_west_id = FlowId("south to west")
    south_to_west = Flow(
        south_to_west_id,
        start=south_section,
        end=west_section,
        distance=11,
    )
    south_to_east_id = FlowId("south to east")
    south_to_east = Flow(
        south_to_east_id,
        start=south_section,
        end=east_section,
        distance=9,
    )
    north_to_south_id = FlowId("north to south")
    north_to_south = Flow(
        north_to_south_id,
        start=north_section,
        end=south_section,
        distance=10,
    )
    flows: list[Flow] = [south_to_north, south_to_west, south_to_east, north_to_south]

    some_events: list[Event] = [
        create_event(first_track, south_section_id),
        create_event(second_track, south_section_id),
        create_event(third_track, south_section_id),
        create_event(forth_track, south_section_id),
        create_event(fifth_track, north_section_id),
        create_event(sixth_track, north_section_id),
        create_event(first_track, north_section_id),
        create_event(first_track, west_section_id),
        create_event(second_track, west_section_id),
        create_event(third_track, west_section_id),
        create_event(forth_track, west_section_id),
        create_event(fifth_track, south_section_id),
        create_event(sixth_track, south_section_id),
    ]
    some_expected_result = SimpleCount(
        {
            south_to_north_id: 0,
            north_to_south_id: 2,
            south_to_west_id: 4,
            south_to_east_id: 0,
        }
    )
    single_track_multiple_sections_events = [
        create_event(first_track, south_section_id),
        create_event(first_track, north_section_id),
        create_event(first_track, west_section_id),
        create_event(first_track, east_section_id),
    ]
    single_track_multiple_sections_result = SimpleCount(
        {
            south_to_north_id: 0,
            north_to_south_id: 0,
            south_to_west_id: 1,
            south_to_east_id: 0,
        }
    )
    single_track_single_sections_events = [
        create_event(first_track, south_section_id),
    ]
    single_track_single_sections_result = SimpleCount(
        {
            south_to_north_id: 0,
            north_to_south_id: 0,
            south_to_west_id: 0,
            south_to_east_id: 0,
        }
    )
    return [
        (some_events, flows, some_expected_result),
        (
            single_track_multiple_sections_events,
            flows,
            single_track_multiple_sections_result,
        ),
        (
            single_track_single_sections_events,
            flows,
            single_track_single_sections_result,
        ),
    ]


class TestSimpleCounter:
    @pytest.mark.parametrize("events, flows, expected_result", create_test_cases())
    def test_run(
        self, events: list[Event], flows: list[Flow], expected_result: dict
    ) -> None:
        analysis = SimpleCounter()
        result = analysis.count(events, flows)

        assert result == expected_result


class TestFilteredCounter:
    def test_filter_before_count(self) -> None:
        counter_filter = Mock(sepc=CounterFilter)
        counter = Mock(spec=TrafficCounter)
        events = Mock()
        flows = Mock()
        filtered_events = Mock()
        counter_filter.filter.return_value = filtered_events
        filtered_counter = FilteredCounter(filter=counter_filter, counter=counter)

        filtered_counter.count(events, flows)

        counter_filter.filter.assert_called_with(events)
        counter.count.assert_called_with(filtered_events, flows)


class TestGroupedCounter:
    def test_count_per_group(self) -> None:
        first_group = Mock(spec=TrafficCounter)
        second_group = Mock(spec=TrafficCounter)
        events = Mock()
        flows = Mock()
        first_counts = Mock()
        second_counts = Mock()
        first_group.count.return_value = first_counts
        second_group.count.return_value = second_counts
        first_group_name = "first"
        second_group_name = "second"
        grouped_counters: dict[str, TrafficCounter] = {
            first_group_name: first_group,
            second_group_name: second_group,
        }
        group_counter = GroupedCounter(groups=grouped_counters)

        result = group_counter.count(events, flows)

        assert result == GroupedCount(
            {
                first_group_name: first_counts,
                second_group_name: second_counts,
            }
        )
