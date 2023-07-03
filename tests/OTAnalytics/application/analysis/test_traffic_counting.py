from datetime import datetime
from unittest.mock import Mock

import pytest

from OTAnalytics.application.analysis.traffic_counting import (
    Count,
    CountableRoadUserAssignments,
    CountingSpecificationDto,
    Exporter,
    ExporterFactory,
    ExportTrafficCounting,
    RoadUserAssigner,
    RoadUserAssignment,
    RoadUserAssignments,
    SimpleCount,
    SingleId,
    SplittedAssignments,
    Splitter,
    SplitterFactory,
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


def create_assignment_test_cases() -> list[tuple]:
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
    some_expected_result: RoadUserAssignments = RoadUserAssignments(
        [
            RoadUserAssignment(first_track.id, south_to_west_id),
            RoadUserAssignment(second_track.id, south_to_west_id),
            RoadUserAssignment(third_track.id, south_to_west_id),
            RoadUserAssignment(forth_track.id, south_to_west_id),
            RoadUserAssignment(fifth_track.id, north_to_south_id),
            RoadUserAssignment(sixth_track.id, north_to_south_id),
        ]
    )
    single_track_multiple_sections_events = [
        create_event(first_track, south_section_id, 0),
        create_event(first_track, north_section_id, 1),
        create_event(first_track, west_section_id, 2),
        create_event(first_track, east_section_id, 3),
    ]
    single_track_multiple_sections_result: RoadUserAssignments = RoadUserAssignments(
        [RoadUserAssignment(first_track.id, south_to_east_id)]
    )
    single_track_single_sections_events = [
        create_event(first_track, south_section_id, 0),
    ]
    single_track_single_sections_result: RoadUserAssignments = RoadUserAssignments([])
    track_without_match_events = [
        create_event(first_track, west_section_id, 0),
        create_event(first_track, south_section_id, 1),
    ]
    track_without_match_result = RoadUserAssignments([])
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
        (
            track_without_match_events,
            flows,
            track_without_match_result,
        ),
    ]


class TestRoadUserAssigner:
    @pytest.mark.parametrize(
        "events, flows, expected_result", create_assignment_test_cases()
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

    some_assignments: list[RoadUserAssignment] = [
        RoadUserAssignment(first_track.id, south_to_west_id),
        RoadUserAssignment(second_track.id, south_to_west_id),
        RoadUserAssignment(third_track.id, south_to_west_id),
        RoadUserAssignment(forth_track.id, south_to_west_id),
        RoadUserAssignment(fifth_track.id, north_to_south_id),
        RoadUserAssignment(sixth_track.id, north_to_south_id),
    ]
    some_expected_result = SimpleCount(
        {
            south_to_north_id: 0,
            north_to_south_id: 2,
            south_to_west_id: 4,
            south_to_east_id: 0,
        }
    )
    single_assignment: list[RoadUserAssignment] = [
        RoadUserAssignment(first_track.id, south_to_east_id)
    ]
    single_assignment_result = SimpleCount(
        {
            south_to_north_id: 0,
            north_to_south_id: 0,
            south_to_west_id: 0,
            south_to_east_id: 1,
        }
    )
    no_assignment: list[RoadUserAssignment] = []
    no_assignment_result = SimpleCount(
        {
            south_to_north_id: 0,
            north_to_south_id: 0,
            south_to_west_id: 0,
            south_to_east_id: 0,
        }
    )
    return [
        (some_assignments, flows, some_expected_result),
        (
            single_assignment,
            flows,
            single_assignment_result,
        ),
        (
            no_assignment,
            flows,
            no_assignment_result,
        ),
    ]


class TestRoadUserAssignment:
    def test_split(self) -> None:
        first_groupd = SingleId(level="mode", id="car")
        second_groupd = SingleId(level="mode", id="bike")
        car_assignment = Mock(spec=RoadUserAssignment)
        bike_assignment = Mock(spec=RoadUserAssignment)
        mode = Mock(spec=Splitter)
        mode.group_name.side_effect = [first_groupd, second_groupd]
        assignments = RoadUserAssignments([car_assignment, bike_assignment])

        splitted = assignments.split(by=mode)

        assert splitted == SplittedAssignments(
            {
                first_groupd: CountableRoadUserAssignments([car_assignment]),
                second_groupd: CountableRoadUserAssignments([bike_assignment]),
            }
        )


class TestCountableRoadUserAssignments:
    @pytest.mark.parametrize(
        "assignments, flows, expected_result", create_counting_test_cases()
    )
    def test_run(
        self,
        assignments: list[RoadUserAssignment],
        flows: list[Flow],
        expected_result: dict,
    ) -> None:
        counter = CountableRoadUserAssignments(assignments)
        result = counter.count(flows)

        assert result == expected_result


class TestTrafficCounting:
    def test_count_traffic(self) -> None:
        event_repository = Mock(spec=EventRepository)
        flow_repository = Mock(spec=FlowRepository)
        road_user_assigner = Mock(spec=RoadUserAssigner)
        splitter_factory = Mock(spec=SplitterFactory)
        splitter = Mock(spec=Splitter)
        exporter_factory = Mock(spec=ExporterFactory)
        exporter = Mock(spec=Exporter)
        events: list[Event] = []
        flows: list[Flow] = []
        assignments = Mock(spec=RoadUserAssignments)
        splitted_assignments = Mock(spec=SplittedAssignments)
        counts = Mock(spec=Count)
        event_repository.get_all.return_value = events
        flow_repository.get_all.return_value = flows
        road_user_assigner.assign.return_value = assignments
        splitter_factory.create_splitter.return_value = splitter
        assignments.split.return_value = splitted_assignments
        splitted_assignments.count.return_value = counts
        exporter_factory.create_exporter.return_value = exporter
        specification = CountingSpecificationDto(
            interval_in_minutes=15,
            format="csv",
            output_file="counts.csv",
        )
        use_case = ExportTrafficCounting(
            event_repository,
            flow_repository,
            road_user_assigner,
            splitter_factory,
            exporter_factory,
        )

        use_case.export(specification)

        event_repository.get_all.assert_called_once()
        flow_repository.get_all.assert_called_once()
        road_user_assigner.assign.assert_called_once()
        splitter_factory.create_splitter.assert_called_once_with(specification)
        assignments.split.assert_called_once_with(splitter)
        splitted_assignments.count.assert_called_once_with(flows)
        exporter_factory.create_exporter.assert_called_once_with(specification)
        exporter.export.assert_called_once()
