from datetime import datetime
from unittest.mock import Mock

import pytest

from OTAnalytics.application.analysis.traffic_counting import (
    Count,
    CounterFilter,
    FilteredCounter,
    GroupedCount,
    GroupedCounter,
    RoadUserAssignement,
    RoadUserAssigner,
    SimpleCount,
    SimpleCounter,
    TrafficCounter,
    TrafficCounting,
)
from OTAnalytics.domain.event import Event, EventRepository
from OTAnalytics.domain.flow import Flow, FlowId, FlowRepository
from OTAnalytics.domain.geometry import DirectionVector2D, ImageCoordinate
from OTAnalytics.domain.section import SectionId
from OTAnalytics.domain.track import TrackId
from OTAnalytics.domain.types import EventType


def create_event(
    track_id: TrackId,
    section: SectionId,
    second: int,
) -> Event:
    return Event(
        road_user_id=track_id.id,
        road_user_type="car",
        hostname="my_hostname",
        occurrence=datetime(2020, 1, 1, 0, 0, second=second),
        frame_number=1,
        section_id=section,
        event_coordinate=ImageCoordinate(0, 0),
        event_type=EventType.SECTION_ENTER,
        direction_vector=DirectionVector2D(x1=1, x2=1),
        video_name="my_video_name.mp4",
    )


def create_assignement_test_cases() -> list[tuple]:
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
    south_to_north_id = FlowId("south to north")
    south_to_north = Flow(
        south_to_north_id,
        name=south_to_north_id.id,
        start=south_section_id,
        end=north_section_id,
        distance=10,
    )
    south_to_west_id = FlowId("south to west")
    south_to_west = Flow(
        south_to_west_id,
        name=south_to_west_id.id,
        start=south_section_id,
        end=west_section_id,
        distance=11,
    )
    south_to_east_id = FlowId("south to east")
    south_to_east = Flow(
        south_to_east_id,
        name=south_to_east_id.id,
        start=south_section_id,
        end=east_section_id,
        distance=9,
    )
    north_to_south_id = FlowId("north to south")
    north_to_south = Flow(
        north_to_south_id,
        name=north_to_south_id.id,
        start=north_section_id,
        end=south_section_id,
        distance=10,
    )
    flows: list[Flow] = [south_to_north, south_to_west, south_to_east, north_to_south]

    some_events: list[Event] = [
        create_event(first_track, south_section_id, 0),
        create_event(second_track, south_section_id, 1),
        create_event(third_track, south_section_id, 2),
        create_event(forth_track, south_section_id, 3),
        create_event(fifth_track, north_section_id, 4),
        create_event(sixth_track, north_section_id, 5),
        create_event(first_track, north_section_id, 6),
        create_event(first_track, west_section_id, 7),
        create_event(second_track, west_section_id, 8),
        create_event(third_track, west_section_id, 9),
        create_event(forth_track, west_section_id, 10),
        create_event(fifth_track, south_section_id, 11),
        create_event(sixth_track, south_section_id, 12),
    ]
    some_expected_result: list[RoadUserAssignement] = [
        RoadUserAssignement(first_track.id, south_to_west_id),
        RoadUserAssignement(second_track.id, south_to_west_id),
        RoadUserAssignement(third_track.id, south_to_west_id),
        RoadUserAssignement(forth_track.id, south_to_west_id),
        RoadUserAssignement(fifth_track.id, north_to_south_id),
        RoadUserAssignement(sixth_track.id, north_to_south_id),
    ]
    single_track_multiple_sections_events = [
        create_event(first_track, south_section_id, 0),
        create_event(first_track, north_section_id, 1),
        create_event(first_track, west_section_id, 2),
        create_event(first_track, east_section_id, 3),
    ]
    single_track_multiple_sections_result: list[RoadUserAssignement] = [
        RoadUserAssignement(first_track.id, south_to_east_id)
    ]
    single_track_single_sections_events = [
        create_event(first_track, south_section_id, 0),
    ]
    single_track_single_sections_result: list[RoadUserAssignement] = []
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


class TestRoadUserAssigner:
    @pytest.mark.parametrize(
        "events, flows, expected_result", create_assignement_test_cases()
    )
    def test_run(
        self, events: list[Event], flows: list[Flow], expected_result: dict
    ) -> None:
        analysis = RoadUserAssigner()
        result = analysis.assign(events, flows)

        assert result == expected_result


def create_counting_test_cases() -> list[tuple]:
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
    south_to_north_id = FlowId("south to north")
    south_to_north = Flow(
        south_to_north_id,
        name=south_to_north_id.id,
        start=south_section_id,
        end=north_section_id,
        distance=10,
    )
    south_to_west_id = FlowId("south to west")
    south_to_west = Flow(
        south_to_west_id,
        name=south_to_west_id.id,
        start=south_section_id,
        end=west_section_id,
        distance=11,
    )
    south_to_east_id = FlowId("south to east")
    south_to_east = Flow(
        south_to_east_id,
        name=south_to_east_id.id,
        start=south_section_id,
        end=east_section_id,
        distance=9,
    )
    north_to_south_id = FlowId("north to south")
    north_to_south = Flow(
        north_to_south_id,
        name=north_to_south_id.id,
        start=north_section_id,
        end=south_section_id,
        distance=10,
    )
    flows: list[Flow] = [south_to_north, south_to_west, south_to_east, north_to_south]

    some_assignements: list[RoadUserAssignement] = [
        RoadUserAssignement(first_track.id, south_to_west_id),
        RoadUserAssignement(second_track.id, south_to_west_id),
        RoadUserAssignement(third_track.id, south_to_west_id),
        RoadUserAssignement(forth_track.id, south_to_west_id),
        RoadUserAssignement(fifth_track.id, north_to_south_id),
        RoadUserAssignement(sixth_track.id, north_to_south_id),
    ]
    some_expected_result = SimpleCount(
        {
            south_to_north_id: 0,
            north_to_south_id: 2,
            south_to_west_id: 4,
            south_to_east_id: 0,
        }
    )
    single_assignement = [RoadUserAssignement(first_track.id, south_to_east_id)]
    single_assignement_result = SimpleCount(
        {
            south_to_north_id: 0,
            north_to_south_id: 0,
            south_to_west_id: 0,
            south_to_east_id: 1,
        }
    )
    no_assignement: list[RoadUserAssignement] = []
    no_assignement_result = SimpleCount(
        {
            south_to_north_id: 0,
            north_to_south_id: 0,
            south_to_west_id: 0,
            south_to_east_id: 0,
        }
    )
    return [
        (some_assignements, flows, some_expected_result),
        (
            single_assignement,
            flows,
            single_assignement_result,
        ),
        (
            no_assignement,
            flows,
            no_assignement_result,
        ),
    ]


class TestSimpleCounter:
    @pytest.mark.parametrize(
        "assignements, flows, expected_result", create_counting_test_cases()
    )
    def test_run(
        self,
        assignements: list[RoadUserAssignement],
        flows: list[Flow],
        expected_result: dict,
    ) -> None:
        analysis = SimpleCounter()
        result = analysis.count(assignements, flows)

        assert result == expected_result


class TestFilteredCounter:
    def test_filter_before_count(self) -> None:
        counter_filter = Mock(sepc=CounterFilter)
        counter = Mock(spec=TrafficCounter)
        assignements = Mock()
        flows = Mock()
        filtered_events = Mock()
        counter_filter.filter.return_value = filtered_events
        filtered_counter = FilteredCounter(filter=counter_filter, counter=counter)

        filtered_counter.count(assignements, flows)

        counter_filter.filter.assert_called_with(assignements)
        counter.count.assert_called_with(filtered_events, flows)


class TestGroupedCounter:
    def test_count_per_group(self) -> None:
        first_group = Mock(spec=TrafficCounter)
        second_group = Mock(spec=TrafficCounter)
        assignements = Mock()
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

        result = group_counter.count(assignements, flows)

        assert result == GroupedCount(
            {
                first_group_name: first_counts,
                second_group_name: second_counts,
            }
        )


class TestTrafficCounting:
    def test_count_traffic(self) -> None:
        event_repository = Mock(spec=EventRepository)
        flow_repository = Mock(spec=FlowRepository)
        road_user_assigner = Mock(spec=RoadUserAssigner)
        counter = Mock(spec=TrafficCounter)
        events: list[Event] = []
        flows: list[Flow] = []
        expected_counts = Mock(spec=Count)
        event_repository.get_all.return_value = events
        flow_repository.get_all.return_value = flows
        counter.count.return_value = expected_counts
        use_case = TrafficCounting(
            event_repository,
            flow_repository,
            road_user_assigner,
            counter,
        )

        counts = use_case.count()

        assert counts == expected_counts
        event_repository.get_all.assert_called_once()
        flow_repository.get_all.assert_called_once()
        road_user_assigner.assign.assert_called_once()
        counter.count.assert_called_once()
