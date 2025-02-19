from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

import pytest

from OTAnalytics.application.analysis.traffic_counting import (
    LEVEL_CLASSIFICATION,
    LEVEL_END_TIME,
    LEVEL_FLOW,
    LEVEL_FROM_SECTION,
    LEVEL_START_TIME,
    LEVEL_TO_SECTION,
    AddSectionInformation,
    CombinedTagger,
    Count,
    CountableAssignments,
    CountByFlow,
    CountDecorator,
    EventPair,
    Exporter,
    ExporterFactory,
    ExportTrafficCounting,
    FillEmptyCount,
    FilterBySectionEnterEvent,
    ModeTagger,
    MultiTag,
    RoadUserAssigner,
    RoadUserAssignment,
    RoadUserAssignments,
    SimpleRoadUserAssigner,
    SingleTag,
    Tag,
    TaggedAssignments,
    Tagger,
    TaggerFactory,
    TimeslotTagger,
    create_export_specification,
    create_timeslot_tag,
)
from OTAnalytics.application.analysis.traffic_counting_specification import (
    CountingSpecificationDto,
    FlowNameDto,
)
from OTAnalytics.application.export_formats.export_mode import OVERWRITE
from OTAnalytics.application.use_cases.create_events import CreateEvents
from OTAnalytics.application.use_cases.section_repository import GetSectionsById
from OTAnalytics.domain.event import Event, EventRepository
from OTAnalytics.domain.flow import Flow, FlowId, FlowRepository
from OTAnalytics.domain.geometry import DirectionVector2D, ImageCoordinate
from OTAnalytics.domain.section import SectionId
from OTAnalytics.domain.track import Track, TrackId
from OTAnalytics.domain.types import EventType
from tests.utils.builders.track_builder import TrackBuilder


@pytest.fixture
def track(track_builder: TrackBuilder) -> Track:
    track_builder.add_occurrence(2000, 1, 2, 0, 0, 0, 0)
    track_builder.append_detection()
    track_builder.append_detection()
    track_builder.append_detection()
    track_builder.append_detection()
    track_builder.append_detection()
    return track_builder.build_track()


@pytest.mark.parametrize(
    "start_time,expected_start_time,expected_end_time",
    [
        ("00:00:00", "00:00:00", "00:15:00"),
        ("00:03:00", "00:00:00", "00:15:00"),
    ],
)
def test_create_timeslot_tag(
    start_time: str,
    expected_start_time: str,
    expected_end_time: str,
) -> None:
    start_date = f"2024-01-01 {start_time}"
    expected_start_date = f"2024-01-01 {expected_start_time}"
    expected_end_date = f"2024-01-01 {expected_end_time}"
    current = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S").replace(
        tzinfo=timezone.utc
    )
    interval = timedelta(minutes=15)
    tag = create_timeslot_tag(current, interval)

    expected_tag = MultiTag(
        frozenset(
            [
                SingleTag(level=LEVEL_START_TIME, id=expected_start_date),
                SingleTag(level=LEVEL_END_TIME, id=expected_end_date),
            ]
        )
    )

    assert tag == expected_tag


class TestCountByFlow:
    def test_to_dict(self) -> None:
        value = 2
        flow_name = "Flow"
        flow = Mock(spec=Flow)
        flow.name = flow_name
        result: dict[Flow, int] = {flow: value}
        count = CountByFlow(result)

        actual = count.to_dict()

        expected = {SingleTag(LEVEL_FLOW, id=flow_name): value}
        assert actual == expected


class TestCountDecorator:
    def test_to_dict(self) -> None:
        other_dict: dict[Tag, int] = {}
        other = Mock(spec=Count)
        other.to_dict.return_value = other_dict
        decorator = CountDecorator(other)

        actual = decorator.to_dict()

        assert actual is other_dict
        other.to_dict.assert_called_once()


class TestFillEmptyCount:
    def test_fill_empty_tags(self) -> None:
        flow_name = "Flow"
        other_dict: dict[Tag, int] = {}
        other = Mock(spec=Count)
        other.to_dict.return_value = other_dict
        flow_tag = SingleTag(LEVEL_FLOW, id=flow_name)
        tags: list[Tag] = [flow_tag]
        filled_dict = {flow_tag: 0}
        count = FillEmptyCount(other, tags)

        actual = count.to_dict()

        assert actual == filled_dict
        other.to_dict.assert_called_once()

    def test_fill_existing_tags(self) -> None:
        flow_name = "Flow"
        mode = "mode"
        tag = MultiTag(
            frozenset(
                [
                    SingleTag(LEVEL_CLASSIFICATION, id=mode),
                    SingleTag(LEVEL_FLOW, id=flow_name),
                ]
            )
        )
        filled_tag = MultiTag(
            frozenset(
                [
                    SingleTag(LEVEL_FLOW, id=flow_name),
                    SingleTag(LEVEL_CLASSIFICATION, id=mode),
                ]
            )
        )
        other_dict: dict[Tag, int] = {tag: 1}
        other = Mock(spec=Count)
        other.to_dict.return_value = other_dict
        tags: list[Tag] = [tag]
        filled_dict = {filled_tag: 1}
        count = FillEmptyCount(other, tags)

        actual = count.to_dict()

        assert dict(actual) == dict(filled_dict)
        other.to_dict.assert_called_once()


class TestAddSectionInformation:
    @pytest.fixture
    def flow_name_info(self) -> dict[str, FlowNameDto]:
        first_flow_dto = FlowNameDto("First Flow", "section a", "section b")
        # second_flow_dto = FlowNameDto("Second Flow", "section c", "section d")
        return {
            first_flow_dto.name: first_flow_dto,
            # second_flow_dto.name: second_flow_dto,
        }

    def test_add_section_info(self, flow_name_info: dict[str, FlowNameDto]) -> None:
        mode = "mode"
        flow = "First Flow"
        tag = MultiTag(
            frozenset(
                [
                    SingleTag(LEVEL_CLASSIFICATION, id=mode),
                    SingleTag(LEVEL_FLOW, id=flow),
                ]
            )
        )

        count = Mock()
        count.to_dict.return_value = {tag: 1}
        add_section_info = AddSectionInformation(count, flow_name_info)
        result = add_section_info.to_dict()
        expected_tag = tag.combine(
            MultiTag(
                frozenset(
                    [
                        SingleTag(
                            LEVEL_FROM_SECTION, flow_name_info[flow].from_section
                        ),
                        SingleTag(LEVEL_TO_SECTION, flow_name_info[flow].to_section),
                    ]
                )
            )
        )
        assert result == {expected_tag: 1}


def create_event(
    track_id: TrackId,
    section: SectionId,
    second: int,
    interpolated_second: int | None = None,
) -> Event:
    real_seconds = second % 60
    minute = int(second / 60)
    year = 2000
    month = 1
    day = 1
    hour = 0
    event_coordinate = ImageCoordinate(0, 0)

    if interpolated_second is None:
        interpolated_real_seconds = real_seconds
        interpolated_minute = minute
    else:
        interpolated_real_seconds = interpolated_second % 60
        interpolated_minute = int(interpolated_second / 60)

    return Event(
        road_user_id=track_id.id,
        road_user_type="car",
        hostname="my_hostname",
        occurrence=datetime(
            year, month, day, hour, minute, second=real_seconds, tzinfo=timezone.utc
        ),
        frame_number=1,
        section_id=section,
        event_coordinate=event_coordinate,
        event_type=EventType.SECTION_ENTER,
        direction_vector=DirectionVector2D(x1=1, x2=1),
        video_name="my_video_name.mp4",
        interpolated_occurrence=datetime(
            year,
            month,
            day,
            hour,
            interpolated_minute,
            interpolated_real_seconds,
            tzinfo=timezone.utc,
        ),
        interpolated_event_coordinate=event_coordinate,
    )


class TestCaseBuilder:
    def __init__(self) -> None:
        self.first_track = TrackId("1")
        self.second_track = TrackId("2")
        self.third_track = TrackId("3")
        self.forth_track = TrackId("4")
        self.fifth_track = TrackId("5")
        self.sixth_track = TrackId("6")
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
            self.__create_same_frame_events(),
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
                    "car",
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
                    "car",
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
                    "car",
                    self.south_to_west,
                    EventPair(first_south, first_west),
                ),
                RoadUserAssignment(
                    self.second_track.id,
                    "car",
                    self.south_to_west,
                    EventPair(second_south, second_west),
                ),
                RoadUserAssignment(
                    self.third_track.id,
                    "car",
                    self.south_to_west,
                    EventPair(third_south, third_west),
                ),
                RoadUserAssignment(
                    self.forth_track.id,
                    "car",
                    self.south_to_west,
                    EventPair(forth_south, forth_west),
                ),
                RoadUserAssignment(
                    self.fifth_track.id,
                    "car",
                    self.north_to_south,
                    EventPair(fifth_north, fifth_south),
                ),
                RoadUserAssignment(
                    self.sixth_track.id,
                    "car",
                    self.north_to_south,
                    EventPair(sixth_north, sixth_south),
                ),
            ]
        )
        return (events, self.flows, expected_result)

    def __create_same_frame_events(
        self,
    ) -> tuple[list[Event], list[Flow], RoadUserAssignments]:
        first_south = create_event(
            track_id=self.first_track,
            section=self.south_section_id,
            second=10,
            interpolated_second=5,
        )
        first_north = create_event(
            track_id=self.first_track,
            section=self.north_section_id,
            second=10,
            interpolated_second=9,
        )
        events = [
            first_north,
            first_south,
        ]
        expected_result: RoadUserAssignments = RoadUserAssignments(
            [
                RoadUserAssignment(
                    self.first_track.id,
                    "car",
                    self.south_to_north,
                    EventPair(first_south, first_north),
                )
            ]
        )

        return events, self.flows, expected_result

    def create_tagging_test_cases(self) -> list[tuple[RoadUserAssignment, Tag]]:
        first_south = create_event(self.first_track, self.south_section_id, 0)
        first_west = create_event(self.first_track, self.west_section_id, 7)
        first_assignment = RoadUserAssignment(
            self.first_track.id,
            "car",
            self.south_to_west,
            EventPair(first_south, first_west),
        )
        first_result = MultiTag(
            frozenset(
                [
                    SingleTag(level=LEVEL_START_TIME, id="2000-01-01 00:00:00"),
                    SingleTag(level=LEVEL_END_TIME, id="2000-01-01 00:01:00"),
                ]
            )
        )

        second_south = create_event(self.first_track, self.south_section_id, 59)
        second_west = create_event(self.second_track, self.west_section_id, 60)
        second_assignment = RoadUserAssignment(
            self.second_track.id,
            "car",
            self.south_to_west,
            EventPair(second_south, second_west),
        )
        second_result = MultiTag(
            frozenset(
                [
                    SingleTag(level=LEVEL_START_TIME, id="2000-01-01 00:00:00"),
                    SingleTag(level=LEVEL_END_TIME, id="2000-01-01 00:01:00"),
                ]
            )
        )

        third_south = create_event(self.third_track, self.south_section_id, 60)
        third_west = create_event(self.third_track, self.west_section_id, 62)
        third_assignment = RoadUserAssignment(
            self.third_track.id,
            "car",
            self.south_to_west,
            EventPair(third_south, third_west),
        )
        third_result = MultiTag(
            frozenset(
                [
                    SingleTag(level=LEVEL_START_TIME, id="2000-01-01 00:01:00"),
                    SingleTag(level=LEVEL_END_TIME, id="2000-01-01 00:02:00"),
                ]
            )
        )

        forth_south = create_event(self.forth_track, self.south_section_id, 120)
        forth_west = create_event(self.forth_track, self.west_section_id, 181)
        forth_assignment = RoadUserAssignment(
            self.forth_track.id,
            "car",
            self.south_to_west,
            EventPair(forth_south, forth_west),
        )
        forth_result = MultiTag(
            frozenset(
                [
                    SingleTag(level=LEVEL_START_TIME, id="2000-01-01 00:02:00"),
                    SingleTag(level=LEVEL_END_TIME, id="2000-01-01 00:03:00"),
                ]
            )
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
                "car",
                self.south_to_west,
                EventPair(first_south, first_west),
            ),
            RoadUserAssignment(
                self.second_track.id,
                "car",
                self.south_to_west,
                EventPair(second_south, second_west),
            ),
            RoadUserAssignment(
                self.third_track.id,
                "car",
                self.south_to_west,
                EventPair(third_south, third_west),
            ),
            RoadUserAssignment(
                self.forth_track.id,
                "car",
                self.south_to_west,
                EventPair(forth_south, forth_west),
            ),
            RoadUserAssignment(
                self.fifth_track.id,
                "car",
                self.north_to_south,
                EventPair(fifth_north, fifth_south),
            ),
            RoadUserAssignment(
                self.sixth_track.id,
                "car",
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
                "car",
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


class TestFilterBySectionEnterEvent:
    def test_assign_filters_by_section_enter_event(self) -> None:
        enter_scene_event = Mock(spec=Event)
        enter_scene_event.event_type = EventType.ENTER_SCENE
        section_enter_event = Mock(spec=Event)
        section_enter_event.event_type = EventType.SECTION_ENTER
        flow = Mock(spec=Flow)

        road_user_assigner = Mock(spec=RoadUserAssigner)

        decorator = FilterBySectionEnterEvent(road_user_assigner)
        decorator.assign([enter_scene_event, section_enter_event], [flow])
        road_user_assigner.assign.assert_called_once_with([section_enter_event], [flow])


class TestSimpleRoadUserAssigner:
    @pytest.mark.parametrize(
        "events, flows, expected_result", create_assignment_test_cases()
    )
    def test_run(
        self,
        events: list[Event],
        flows: list[Flow],
        expected_result: RoadUserAssignments,
    ) -> None:
        """
        https://openproject.platomo.de/projects/otanalytics/work_packages/6321/activity
        """
        analysis = SimpleRoadUserAssigner()
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
        assignment = RoadUserAssignment(
            track.id.id,
            track.classification,
            flow,
            EventPair(first_event, second_event),
        )
        tagger = ModeTagger()

        group_name = tagger.create_tag(assignment)

        assert group_name == SingleTag(
            level=LEVEL_CLASSIFICATION, id=track.classification
        )


class TestTimeTagger:
    @pytest.mark.parametrize(
        "assignment, expected_result", TestCaseBuilder().create_tagging_test_cases()
    )
    def test_create_tag(
        self, assignment: RoadUserAssignment, expected_result: Tag
    ) -> None:
        tagger = TimeslotTagger(interval=timedelta(minutes=1))

        group = tagger.create_tag(assignment)

        assert group == expected_result


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

        assert group_name == MultiTag(frozenset([first_id, second_id]))


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
        get_sections_by_ids = Mock(spec=GetSectionsById)
        create_events = Mock(spec=CreateEvents)
        road_user_assigner = Mock(spec=RoadUserAssigner)
        tagger_factory = Mock(spec=TaggerFactory)
        tagger = Mock(spec=Tagger)
        exporter_factory = Mock(spec=ExporterFactory)
        exporter = Mock(spec=Exporter)
        events: list[Event] = []
        flows: list[Flow] = []
        modes: list[str] = []
        assignments = Mock(spec=RoadUserAssignments)
        tagged_assignments = Mock(spec=TaggedAssignments)
        counts = Mock(spec=Count)
        event_repository.get_all.return_value = events
        flow_repository.get_all.return_value = flows
        get_sections_by_ids.return_value = []
        road_user_assigner.assign.return_value = assignments
        tagger_factory.create_tagger.return_value = tagger
        assignments.tag.return_value = tagged_assignments
        tagged_assignments.count.return_value = counts
        exporter_factory.create_exporter.return_value = exporter
        start = datetime(2023, 1, 1, 0, 0, 0)
        end = datetime(2023, 1, 1, 0, 15, 0)
        counting_specification = CountingSpecificationDto(
            start=start,
            end=end,
            interval_in_minutes=15,
            modes=modes,
            output_format="csv",
            output_file="counts.csv",
            export_mode=OVERWRITE,
        )
        export_specification = create_export_specification(
            flows, counting_specification, get_sections_by_ids
        )
        use_case = ExportTrafficCounting(
            event_repository,
            flow_repository,
            get_sections_by_ids,
            create_events,
            road_user_assigner,
            tagger_factory,
            exporter_factory,
        )

        use_case.export(counting_specification)

        event_repository.get.assert_called_once_with(start_date=start, end_date=end)
        flow_repository.get_all.assert_called_once()
        create_events.assert_called_once()
        road_user_assigner.assign.assert_called_once()
        tagger_factory.create_tagger.assert_called_once_with(counting_specification)
        assignments.tag.assert_called_once_with(tagger)
        tagged_assignments.count.assert_called_once_with(flows)
        exporter_factory.create_exporter.assert_called_once_with(export_specification)
        exporter.export.assert_called_once_with(counts, OVERWRITE)
