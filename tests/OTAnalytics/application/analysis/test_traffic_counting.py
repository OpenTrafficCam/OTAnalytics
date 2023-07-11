from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest

from OTAnalytics.application.analysis.traffic_counting import (
    LEVEL_CLASSIFICATION,
    LEVEL_END_TIME,
    LEVEL_START_TIME,
    UNCLASSIFIED,
    CombinedTagger,
    Count,
    CountableAssignments,
    CountByFlow,
    CountingSpecificationDto,
    EventPair,
    Exporter,
    ExporterFactory,
    ExportTrafficCounting,
    ModeTagger,
    MultiTag,
    RoadUserAssigner,
    RoadUserAssignment,
    RoadUserAssignments,
    SingleTag,
    Tag,
    TaggedAssignments,
    Tagger,
    TaggerFactory,
    TimeslotTagger,
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


def create_event(
    track_id: TrackId,
    section: SectionId,
    second: int,
) -> Event:
    real_seconds = second % 60
    minute = int(second / 60)
    return Event(
        road_user_id=track_id.id,
        road_user_type="car",
        hostname="my_hostname",
        occurrence=datetime(2020, 1, 1, 0, minute, second=real_seconds),
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

    def build_assignment_test_cases(
        self,
    ) -> list[tuple[list[Event], list[Flow], RoadUserAssignments]]:
        return [
            self.__create_complex_test_case(),
            self.__create_single_track_multiple_selection(),
            self.__create_single_track_single_event(),
            self.__create_tracks_without_match(),
            self.__create_unordered_events(),
        ]

    def __create_single_track_single_event(
        self,
    ) -> tuple[list[Event], list[Flow], RoadUserAssignments]:
        events = [
            create_event(self.first_track, self.south_section_id, 0),
        ]
        expected_result: RoadUserAssignments = RoadUserAssignments([])

        return (events, self.flows, expected_result)

    def __create_tracks_without_match(
        self,
    ) -> tuple[list[Event], list[Flow], RoadUserAssignments]:
        events = [
            create_event(self.first_track, self.west_section_id, 0),
            create_event(self.first_track, self.south_section_id, 1),
        ]
        expected_result = RoadUserAssignments([])
        return (events, self.flows, expected_result)

    def __create_unordered_events(
        self,
    ) -> tuple[list[Event], list[Flow], RoadUserAssignments]:
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
                    self.north_to_south,
                    EventPair(first_north, first_south),
                )
            ]
        )

        return (events, self.flows, expected_result)

    def __create_single_track_multiple_selection(
        self,
    ) -> tuple[list[Event], list[Flow], RoadUserAssignments]:
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
                    self.south_to_east,
                    EventPair(first_south, first_east),
                )
            ]
        )
        return (events, self.flows, expected_result)

    def __create_complex_test_case(
        self,
    ) -> tuple[list[Event], list[Flow], RoadUserAssignments]:
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
                    self.south_to_west,
                    EventPair(first_south, first_west),
                ),
                RoadUserAssignment(
                    self.second_track.id,
                    self.south_to_west,
                    EventPair(second_south, second_west),
                ),
                RoadUserAssignment(
                    self.third_track.id,
                    self.south_to_west,
                    EventPair(third_south, third_west),
                ),
                RoadUserAssignment(
                    self.forth_track.id,
                    self.south_to_west,
                    EventPair(forth_south, forth_west),
                ),
                RoadUserAssignment(
                    self.fifth_track.id,
                    self.north_to_south,
                    EventPair(fifth_north, fifth_south),
                ),
                RoadUserAssignment(
                    self.sixth_track.id,
                    self.north_to_south,
                    EventPair(sixth_north, sixth_south),
                ),
            ]
        )
        return (events, self.flows, expected_result)

    def create_tagging_test_cases(self) -> list[tuple[RoadUserAssignment, Tag]]:
        first_south = create_event(self.first_track, self.south_section_id, 0)
        first_west = create_event(self.first_track, self.west_section_id, 7)
        first_assignment = RoadUserAssignment(
            self.first_track.id,
            self.south_to_west,
            EventPair(first_south, first_west),
        )
        first_result = MultiTag(
            [
                SingleTag(level=LEVEL_START_TIME, id="00:00"),
                SingleTag(level=LEVEL_END_TIME, id="00:01"),
            ]
        )

        second_south = create_event(self.first_track, self.south_section_id, 59)
        second_west = create_event(self.second_track, self.west_section_id, 60)
        second_assignment = RoadUserAssignment(
            self.second_track.id,
            self.south_to_west,
            EventPair(second_south, second_west),
        )
        second_result = MultiTag(
            [
                SingleTag(level=LEVEL_START_TIME, id="00:00"),
                SingleTag(level=LEVEL_END_TIME, id="00:01"),
            ]
        )

        third_south = create_event(self.third_track, self.south_section_id, 60)
        third_west = create_event(self.third_track, self.west_section_id, 62)
        third_assignment = RoadUserAssignment(
            self.third_track.id,
            self.south_to_west,
            EventPair(third_south, third_west),
        )
        third_result = MultiTag(
            [
                SingleTag(level=LEVEL_START_TIME, id="00:01"),
                SingleTag(level=LEVEL_END_TIME, id="00:02"),
            ]
        )

        forth_south = create_event(self.forth_track, self.south_section_id, 120)
        forth_west = create_event(self.forth_track, self.west_section_id, 181)
        forth_assignment = RoadUserAssignment(
            self.forth_track.id,
            self.south_to_west,
            EventPair(forth_south, forth_west),
        )
        forth_result = MultiTag(
            [
                SingleTag(level=LEVEL_START_TIME, id="00:02"),
                SingleTag(level=LEVEL_END_TIME, id="00:03"),
            ]
        )
        return [
            (first_assignment, first_result),
            (second_assignment, second_result),
            (third_assignment, third_result),
            (forth_assignment, forth_result),
        ]

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
                self.south_to_west,
                EventPair(first_south, first_west),
            ),
            RoadUserAssignment(
                self.second_track.id,
                self.south_to_west,
                EventPair(second_south, second_west),
            ),
            RoadUserAssignment(
                self.third_track.id,
                self.south_to_west,
                EventPair(third_south, third_west),
            ),
            RoadUserAssignment(
                self.forth_track.id,
                self.south_to_west,
                EventPair(forth_south, forth_west),
            ),
            RoadUserAssignment(
                self.fifth_track.id,
                self.north_to_south,
                EventPair(fifth_north, fifth_south),
            ),
            RoadUserAssignment(
                self.sixth_track.id,
                self.north_to_south,
                EventPair(sixth_north, sixth_south),
            ),
        ]
        some_expected_result = CountByFlow(
            {
                self.south_to_north: 0,
                self.north_to_south: 2,
                self.south_to_west: 4,
                self.south_to_east: 0,
            }
        )
        single_assignment: list[RoadUserAssignment] = [
            RoadUserAssignment(
                self.first_track.id,
                self.south_to_east,
                EventPair(first_south, first_east),
            )
        ]
        single_assignment_result = CountByFlow(
            {
                self.south_to_north: 0,
                self.north_to_south: 0,
                self.south_to_west: 0,
                self.south_to_east: 1,
            }
        )
        no_assignment: list[RoadUserAssignment] = []
        no_assignment_result = CountByFlow(
            {
                self.south_to_north: 0,
                self.north_to_south: 0,
                self.south_to_west: 0,
                self.south_to_east: 0,
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


def create_assignment_test_cases() -> (
    list[tuple[list[Event], list[Flow], RoadUserAssignments]]
):
    return TestCaseBuilder().build_assignment_test_cases()


class TestRoadUserAssigner:
    @pytest.mark.parametrize(
        "events, flows, expected_result", create_assignment_test_cases()
    )
    def test_run(
        self,
        events: list[Event],
        flows: list[Flow],
        expected_result: RoadUserAssignments,
    ) -> None:
        analysis = RoadUserAssigner()
        result = analysis.assign(events, flows)

        assert result == expected_result


def create_counting_test_cases() -> list[tuple]:
    return TestCaseBuilder().create_counting_test_cases()


class TestRoadUserAssignment:
    def test_tag(self) -> None:
        first_groupd = SingleTag(level="mode", id="car")
        second_groupd = SingleTag(level="mode", id="bike")
        car_assignment = Mock(spec=RoadUserAssignment)
        bike_assignment = Mock(spec=RoadUserAssignment)
        mode = Mock(spec=Tagger)
        mode.create_tag.side_effect = [first_groupd, second_groupd]
        assignments = RoadUserAssignments([car_assignment, bike_assignment])

        tagged = assignments.tag(by=mode)

        assert tagged == TaggedAssignments(
            {
                first_groupd: CountableAssignments([car_assignment]),
                second_groupd: CountableAssignments([bike_assignment]),
            }
        )


class TestModeTagger:
    def test_create_tag_existing_track(self, track: Track) -> None:
        flow = Mock(spec=Flow)
        first_event = Mock(spec=Event)
        second_event = Mock(spec=Event)
        track_repository = Mock(spec=TrackRepository)
        track_repository.get_for.return_value = track
        assignment = RoadUserAssignment(
            track.id.id,
            flow,
            EventPair(first_event, second_event),
        )
        tagger = ModeTagger(track_repository)

        group_name = tagger.create_tag(assignment)

        assert group_name == SingleTag(
            level=LEVEL_CLASSIFICATION, id=track.classification
        )

    def test_create_tag_missing_track(self) -> None:
        track_id = 1
        flow = Mock(spec=Flow)
        first_event = Mock(spec=Event)
        second_event = Mock(spec=Event)
        track_repository = Mock(spec=TrackRepository)
        track_repository.get_for.return_value = None
        assignment = RoadUserAssignment(
            track_id,
            flow,
            EventPair(first_event, second_event),
        )
        tagger = ModeTagger(track_repository)

        group_name = tagger.create_tag(assignment)

        assert group_name == SingleTag(level=LEVEL_CLASSIFICATION, id=UNCLASSIFIED)


class TestTimeTagger:
    @pytest.mark.parametrize(
        "assignment, expected_result", TestCaseBuilder().create_tagging_test_cases()
    )
    def test_create_tag(
        self, assignment: RoadUserAssignment, expected_result: Tag
    ) -> None:
        tagger = TimeslotTagger(interval=timedelta(minutes=1))

        group_name = tagger.create_tag(assignment)

        assert group_name == expected_result


class TestCombinedTagger:
    def test_create_tag(self) -> None:
        first_id = SingleTag(level=LEVEL_START_TIME, id="00:00")
        second_id = SingleTag(level=LEVEL_CLASSIFICATION, id="car")
        first = Mock(spec=Tagger)
        second = Mock(spec=Tagger)
        first.create_tag.return_value = first_id
        second.create_tag.return_value = second_id
        assignment = Mock(spec=RoadUserAssignment)
        tagger = CombinedTagger(first, second)

        group_name = tagger.create_tag(assignment)

        assert group_name == MultiTag([first_id, second_id])


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
        tagger_factory = Mock(spec=TaggerFactory)
        tagger = Mock(spec=Tagger)
        exporter_factory = Mock(spec=ExporterFactory)
        exporter = Mock(spec=Exporter)
        events: list[Event] = []
        flows: list[Flow] = []
        assignments = Mock(spec=RoadUserAssignments)
        tagged_assignments = Mock(spec=TaggedAssignments)
        counts = Mock(spec=Count)
        event_repository.get_all.return_value = events
        flow_repository.get_all.return_value = flows
        road_user_assigner.assign.return_value = assignments
        tagger_factory.create_tagger.return_value = tagger
        assignments.tag.return_value = tagged_assignments
        tagged_assignments.count.return_value = counts
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
            tagger_factory,
            exporter_factory,
        )

        use_case.export(specification)

        event_repository.get_all.assert_called_once()
        flow_repository.get_all.assert_called_once()
        road_user_assigner.assign.assert_called_once()
        tagger_factory.create_tagger.assert_called_once_with(specification)
        assignments.tag.assert_called_once_with(tagger)
        tagged_assignments.count.assert_called_once_with(flows)
        exporter_factory.create_exporter.assert_called_once_with(specification)
        exporter.export.assert_called_once_with(counts)
