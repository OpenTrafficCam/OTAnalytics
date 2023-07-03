from datetime import datetime
from unittest.mock import Mock

import pytest

from OTAnalytics.application.analysis.traffic_counting import (
    LEVEL_CLASSIFICATION,
    UNCLASSIFIED,
    Count,
    CountableAssignments,
    CountByFlow,
    CountingSpecificationDto,
    EventPair,
    Exporter,
    ExporterFactory,
    ExportTrafficCounting,
    ModeSplitter,
    RoadUserAssigner,
    RoadUserAssignment,
    RoadUserAssignments,
    SingleId,
    SplittedAssignments,
    Splitter,
    SplitterFactory,
)
from OTAnalytics.domain.event import Event, EventRepository
from OTAnalytics.domain.flow import Flow, FlowId, FlowRepository
from OTAnalytics.domain.geometry import DirectionVector2D, ImageCoordinate
from OTAnalytics.domain.section import SectionId
from OTAnalytics.domain.track import Track, TrackId, TrackRepository
from OTAnalytics.domain.types import EventType
from tests.conftest import TrackBuilder


@pytest.fixture
def track(track_builder: TrackBuilder) -> Track:
    track_builder.add_occurrence(2000, 1, 2, 0, 0, 0, 0)
    track_builder.append_detection()
    track_builder.append_detection()
    track_builder.append_detection()
    track_builder.append_detection()
    track_builder.append_detection()
    return track_builder.build_track()


class TestModeSplitter:
    def test_group_name_existing_track(self, track: Track) -> None:
        flow_id = FlowId("0")
        first_event = Mock(spec=Event)
        second_event = Mock(spec=Event)
        track_repository = Mock(spec=TrackRepository)
        track_repository.get_for.return_value = track
        assignment = RoadUserAssignment(
            track.id.id,
            flow_id,
            EventPair(first_event, second_event),
        )
        splitter = ModeSplitter(track_repository)

        group_name = splitter.group_name(assignment)

        assert group_name == SingleId(
            level=LEVEL_CLASSIFICATION, id=track.classification
        )

    def test_group_name_missing_track(self) -> None:
        track_id = 1
        flow_id = FlowId("0")
        first_event = Mock(spec=Event)
        second_event = Mock(spec=Event)
        track_repository = Mock(spec=TrackRepository)
        track_repository.get_for.return_value = None
        assignment = RoadUserAssignment(
            track_id,
            flow_id,
            EventPair(first_event, second_event),
        )
        splitter = ModeSplitter(track_repository)

        group_name = splitter.group_name(assignment)

        assert group_name == SingleId(level=LEVEL_CLASSIFICATION, id=UNCLASSIFIED)


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


class TestCaseBuilder:
    def __init__(self) -> None:
        self.first_track = TrackId(1)
        self.second_track = TrackId(2)
        self.third_track = TrackId(3)
        self.forth_track = TrackId(4)
        self.fifth_track = TrackId(5)
        self.sixth_track = TrackId(6)
        self.south_section_id = SectionId("south")
        self.north_section_id = SectionId("north")
        self.west_section_id = SectionId("west")
        self.east_section_id = SectionId("east")
        self.south_to_north_id = FlowId("south to north")
        self.south_to_north = Flow(
            self.south_to_north_id,
            name=self.south_to_north_id.id,
            start=self.south_section_id,
            end=self.north_section_id,
            distance=10,
        )
        self.south_to_west_id = FlowId("south to west")
        self.south_to_west = Flow(
            self.south_to_west_id,
            name=self.south_to_west_id.id,
            start=self.south_section_id,
            end=self.west_section_id,
            distance=11,
        )
        self.south_to_east_id = FlowId("south to east")
        self.south_to_east = Flow(
            self.south_to_east_id,
            name=self.south_to_east_id.id,
            start=self.south_section_id,
            end=self.east_section_id,
            distance=9,
        )
        self.north_to_south_id = FlowId("north to south")
        self.north_to_south = Flow(
            self.north_to_south_id,
            name=self.north_to_south_id.id,
            start=self.north_section_id,
            end=self.south_section_id,
            distance=10,
        )
        self.flows: list[Flow] = [
            self.south_to_north,
            self.south_to_west,
            self.south_to_east,
            self.north_to_south,
        ]

    def build_assignment_test_cases(self) -> list[tuple]:
        return [
            self.__create_complex_test_case(),
            self.__create_single_track_multiple_selection(),
            self.__create_single_track_single_event(),
            self.__create_tracks_without_match(),
            self.__create_unordered_events(),
        ]

    def __create_single_track_single_event(self) -> tuple:
        events = [
            create_event(self.first_track, self.south_section_id, 0),
        ]
        expected_result: RoadUserAssignments = RoadUserAssignments([])

        return (events, self.flows, expected_result)

    def __create_tracks_without_match(self) -> tuple:
        events = [
            create_event(self.first_track, self.west_section_id, 0),
            create_event(self.first_track, self.south_section_id, 1),
        ]
        expected_result = RoadUserAssignments([])
        return (events, self.flows, expected_result)

    def __create_unordered_events(self) -> tuple:
        first_south = create_event(self.first_track, self.south_section_id, 1)
        first_north = create_event(self.first_track, self.north_section_id, 0)
        events = [
            first_south,
            first_north,
        ]
        expected_result: RoadUserAssignments = RoadUserAssignments(
            [
                RoadUserAssignment(
                    self.first_track.id,
                    self.north_to_south_id,
                    EventPair(first_north, first_south),
                )
            ]
        )

        return (events, self.flows, expected_result)

    def __create_single_track_multiple_selection(self) -> tuple:
        first_south = create_event(self.first_track, self.south_section_id, 0)
        first_north = create_event(self.first_track, self.north_section_id, 1)
        first_west = create_event(self.first_track, self.west_section_id, 2)
        first_east = create_event(self.first_track, self.east_section_id, 3)
        events = [
            first_south,
            first_north,
            first_west,
            first_east,
        ]
        expected_result: RoadUserAssignments = RoadUserAssignments(
            [
                RoadUserAssignment(
                    self.first_track.id,
                    self.south_to_east_id,
                    EventPair(first_south, first_east),
                )
            ]
        )
        return (events, self.flows, expected_result)

    def __create_complex_test_case(self) -> tuple:
        first_south = create_event(self.first_track, self.south_section_id, 0)
        second_south = create_event(self.second_track, self.south_section_id, 1)
        third_south = create_event(self.third_track, self.south_section_id, 2)
        forth_south = create_event(self.forth_track, self.south_section_id, 3)
        fifth_north = create_event(self.fifth_track, self.north_section_id, 4)
        sixth_north = create_event(self.sixth_track, self.north_section_id, 5)
        first_north = create_event(self.first_track, self.north_section_id, 6)
        first_west = create_event(self.first_track, self.west_section_id, 7)
        second_west = create_event(self.second_track, self.west_section_id, 8)
        third_west = create_event(self.third_track, self.west_section_id, 9)
        forth_west = create_event(self.forth_track, self.west_section_id, 10)
        fifth_south = create_event(self.fifth_track, self.south_section_id, 11)
        sixth_south = create_event(self.sixth_track, self.south_section_id, 12)
        events: list[Event] = [
            first_south,
            second_south,
            third_south,
            forth_south,
            fifth_north,
            sixth_north,
            first_north,
            first_west,
            second_west,
            third_west,
            forth_west,
            fifth_south,
            sixth_south,
        ]
        expected_result: RoadUserAssignments = RoadUserAssignments(
            [
                RoadUserAssignment(
                    self.first_track.id,
                    self.south_to_west_id,
                    EventPair(first_south, first_west),
                ),
                RoadUserAssignment(
                    self.second_track.id,
                    self.south_to_west_id,
                    EventPair(second_south, second_west),
                ),
                RoadUserAssignment(
                    self.third_track.id,
                    self.south_to_west_id,
                    EventPair(third_south, third_west),
                ),
                RoadUserAssignment(
                    self.forth_track.id,
                    self.south_to_west_id,
                    EventPair(forth_south, forth_west),
                ),
                RoadUserAssignment(
                    self.fifth_track.id,
                    self.north_to_south_id,
                    EventPair(fifth_north, fifth_south),
                ),
                RoadUserAssignment(
                    self.sixth_track.id,
                    self.north_to_south_id,
                    EventPair(sixth_north, sixth_south),
                ),
            ]
        )
        return (events, self.flows, expected_result)

    def create_counting_test_cases(self) -> list[tuple]:
        first_south = create_event(self.first_track, self.south_section_id, 0)
        second_south = create_event(self.second_track, self.south_section_id, 1)
        third_south = create_event(self.third_track, self.south_section_id, 2)
        forth_south = create_event(self.forth_track, self.south_section_id, 3)
        fifth_north = create_event(self.fifth_track, self.north_section_id, 4)
        sixth_north = create_event(self.sixth_track, self.north_section_id, 5)
        first_east = create_event(self.first_track, self.east_section_id, 6)
        first_west = create_event(self.first_track, self.west_section_id, 7)
        second_west = create_event(self.second_track, self.west_section_id, 8)
        third_west = create_event(self.third_track, self.west_section_id, 9)
        forth_west = create_event(self.forth_track, self.west_section_id, 10)
        fifth_south = create_event(self.fifth_track, self.south_section_id, 11)
        sixth_south = create_event(self.sixth_track, self.south_section_id, 12)
        multiple_assignments: list[RoadUserAssignment] = [
            RoadUserAssignment(
                self.first_track.id,
                self.south_to_west_id,
                EventPair(first_south, first_west),
            ),
            RoadUserAssignment(
                self.second_track.id,
                self.south_to_west_id,
                EventPair(second_south, second_west),
            ),
            RoadUserAssignment(
                self.third_track.id,
                self.south_to_west_id,
                EventPair(third_south, third_west),
            ),
            RoadUserAssignment(
                self.forth_track.id,
                self.south_to_west_id,
                EventPair(forth_south, forth_west),
            ),
            RoadUserAssignment(
                self.fifth_track.id,
                self.north_to_south_id,
                EventPair(fifth_north, fifth_south),
            ),
            RoadUserAssignment(
                self.sixth_track.id,
                self.north_to_south_id,
                EventPair(sixth_north, sixth_south),
            ),
        ]
        some_expected_result = CountByFlow(
            {
                self.south_to_north_id: 0,
                self.north_to_south_id: 2,
                self.south_to_west_id: 4,
                self.south_to_east_id: 0,
            }
        )
        single_assignment: list[RoadUserAssignment] = [
            RoadUserAssignment(
                self.first_track.id,
                self.south_to_east_id,
                EventPair(first_south, first_east),
            )
        ]
        single_assignment_result = CountByFlow(
            {
                self.south_to_north_id: 0,
                self.north_to_south_id: 0,
                self.south_to_west_id: 0,
                self.south_to_east_id: 1,
            }
        )
        no_assignment: list[RoadUserAssignment] = []
        no_assignment_result = CountByFlow(
            {
                self.south_to_north_id: 0,
                self.north_to_south_id: 0,
                self.south_to_west_id: 0,
                self.south_to_east_id: 0,
            }
        )
        return [
            (multiple_assignments, self.flows, some_expected_result),
            (
                single_assignment,
                self.flows,
                single_assignment_result,
            ),
            (
                no_assignment,
                self.flows,
                no_assignment_result,
            ),
        ]


def create_assignment_test_cases() -> list[tuple]:
    return TestCaseBuilder().build_assignment_test_cases()


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
    return TestCaseBuilder().create_counting_test_cases()


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
                first_groupd: CountableAssignments([car_assignment]),
                second_groupd: CountableAssignments([bike_assignment]),
            }
        )


class TestCountableAssignments:
    @pytest.mark.parametrize(
        "assignments, flows, expected_result", create_counting_test_cases()
    )
    def test_run(
        self,
        assignments: list[RoadUserAssignment],
        flows: list[Flow],
        expected_result: dict,
    ) -> None:
        counter = CountableAssignments(assignments)
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
