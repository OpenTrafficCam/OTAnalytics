from datetime import datetime
from unittest.mock import Mock

import pytest

from OTAnalytics.application.ui.frame_control import DEFAULT_EVENT_TYPES
from OTAnalytics.domain.event import (
    DATE_FORMAT,
    DIRECTION_VECTOR,
    EVENT_COORDINATE,
    EVENT_TYPE,
    FRAME_NUMBER,
    HOSTNAME,
    INTERPOLATED_EVENT_COORDINATE,
    INTERPOLATED_OCCURRENCE,
    OCCURRENCE,
    ROAD_USER_ID,
    ROAD_USER_TYPE,
    SECTION_ID,
    VIDEO_NAME,
    Event,
    EventBuilder,
    EventRepository,
    EventRepositoryEvent,
    ImproperFormattedFilename,
    IncompleteEventBuilderSetup,
    SceneEventBuilder,
    SectionEventBuilder,
)
from OTAnalytics.domain.geometry import DirectionVector2D, ImageCoordinate
from OTAnalytics.domain.section import Section, SectionId
from OTAnalytics.domain.track import Detection, TrackId
from OTAnalytics.domain.types import EventType, EventTypeParseError
from tests.utils.builders import event_builder

SECTION_ID_1 = SectionId("section 1")
SECTION_ID_2 = SectionId("section 2")
ROAD_USER_ID_1 = TrackId("road_user_1")
ROAD_USER_ID_2 = TrackId("road_user_2")

EVENT_OCCURRENCE = datetime(2022, 1, 1, 0, 0, 0, 0)
INTERPOLATED_EVENT_OCCURRENCE = datetime(2022, 12, 31, 23, 59, 59, 0)


@pytest.fixture
def valid_detection() -> Detection:
    detection = Mock(spec=Detection)
    detection.classification = "car"
    detection.confidence = 0.5
    detection.x = 0.0
    detection.y = 0.0
    detection.w = 15.3
    detection.h = 30.5
    detection.frame = 1
    detection.occurrence = datetime(2022, 1, 1, 0, 0, 0, 0)
    detection.interpolated_detection = False
    detection.track_id = TrackId("1")
    detection.video_name = "myhostname_something.mp4"
    return detection


class TestEventType:
    def test_serialize(self) -> None:
        event_type = EventType.ENTER_SCENE
        assert event_type.serialize() == event_type.value

    def test_parse_valid_string(self) -> None:
        event_type = "section-enter"
        assert EventType.parse(event_type) == EventType.SECTION_ENTER

    def test_parse_not_existing_event_type(self) -> None:
        event_type = "foo-bar"
        with pytest.raises(EventTypeParseError):
            EventType.parse(event_type)


class TestEvent:
    @pytest.mark.parametrize("frame", [-1, 0])
    def test_instantiate_event_with_invalid_frame_number(self, frame: int) -> None:
        event_coordinate = ImageCoordinate(0, 0)
        with pytest.raises(ValueError):
            Event(
                road_user_id="1",
                road_user_type="car",
                hostname="my_hostname",
                occurrence=EVENT_OCCURRENCE,
                frame_number=frame,
                section_id=SectionId("N"),
                event_coordinate=event_coordinate,
                event_type=EventType.SECTION_ENTER,
                direction_vector=DirectionVector2D(1, 0),
                video_name="my_video_name.mp4",
                interpolated_occurrence=EVENT_OCCURRENCE,
                interpolated_event_coordinate=event_coordinate,
            )

    def test_instantiate_with_valid_args(self) -> None:
        event_coordinate = ImageCoordinate(0, 0)
        direction = DirectionVector2D(1, 0)
        event = Event(
            road_user_id="1",
            road_user_type="car",
            hostname="my_hostname",
            occurrence=EVENT_OCCURRENCE,
            frame_number=1,
            section_id=SectionId("N"),
            event_coordinate=event_coordinate,
            event_type=EventType.SECTION_ENTER,
            direction_vector=direction,
            video_name="my_video_name.mp4",
            interpolated_occurrence=EVENT_OCCURRENCE,
            interpolated_event_coordinate=event_coordinate,
        )
        assert event.road_user_id == "1"
        assert event.road_user_type == "car"
        assert event.hostname == "my_hostname"
        assert event.occurrence == EVENT_OCCURRENCE
        assert event.frame_number == 1
        assert event.section_id == SectionId("N")
        assert event.event_coordinate == event_coordinate
        assert event.event_type == EventType.SECTION_ENTER
        assert event.direction_vector == direction
        assert event.video_name == "my_video_name.mp4"

    def test_to_dict(self) -> None:
        road_user_id = "1"
        road_user_type = "car"
        hostname = "myhostname"
        occurrence = EVENT_OCCURRENCE
        frame_number = 1
        section_id = SectionId("N")
        event_coordinate = ImageCoordinate(1, 0)
        interpolated_event_coordinate = ImageCoordinate(0.5, 0)
        direction_vector = DirectionVector2D(1, 0)
        video_name = "my_video_name.mp4"
        event = Event(
            road_user_id=road_user_id,
            road_user_type=road_user_type,
            hostname=hostname,
            occurrence=occurrence,
            frame_number=frame_number,
            section_id=section_id,
            event_coordinate=event_coordinate,
            event_type=EventType.SECTION_ENTER,
            direction_vector=direction_vector,
            video_name=video_name,
            interpolated_occurrence=INTERPOLATED_EVENT_OCCURRENCE,
            interpolated_event_coordinate=interpolated_event_coordinate,
        )
        event_dict = event.to_dict()
        expected = {
            ROAD_USER_ID: road_user_id,
            ROAD_USER_TYPE: road_user_type,
            HOSTNAME: hostname,
            OCCURRENCE: occurrence.strftime(DATE_FORMAT),
            FRAME_NUMBER: frame_number,
            SECTION_ID: section_id.serialize(),
            EVENT_COORDINATE: [event_coordinate.x, event_coordinate.y],
            EVENT_TYPE: EventType.SECTION_ENTER.value,
            DIRECTION_VECTOR: [direction_vector.x1, direction_vector.x2],
            VIDEO_NAME: video_name,
            INTERPOLATED_OCCURRENCE: INTERPOLATED_EVENT_OCCURRENCE.strftime(
                DATE_FORMAT
            ),
            INTERPOLATED_EVENT_COORDINATE: [
                interpolated_event_coordinate.x,
                interpolated_event_coordinate.y,
            ],
        }

        assert event_dict == expected


class TestEventBuilder:
    def test_extract_hostname(self) -> None:
        video_name = "myhostname_2022-12-13_13-00-00.mp4"
        assert EventBuilder.extract_hostname(video_name) == "myhostname"

    def test_extract_hostname_wrong_format(self) -> None:
        wrong_formatted_name = "myhostname.mp4"
        with pytest.raises(ImproperFormattedFilename):
            EventBuilder.extract_hostname(wrong_formatted_name)


class TestSectionEventBuilder:
    def test_create_event_without_adds(self, valid_detection: Detection) -> None:
        event_builder = SectionEventBuilder()
        with pytest.raises(IncompleteEventBuilderSetup):
            event_builder.create_event(valid_detection)

    def test_create_event_without_event_type_added(
        self, valid_detection: Detection
    ) -> None:
        event_builder = SectionEventBuilder()
        event_builder.add_section_id(SectionId("N"))
        event_builder.add_direction_vector(Mock())
        with pytest.raises(IncompleteEventBuilderSetup):
            event_builder.create_event(valid_detection)

    def test_create_event_without_direction_vector_added(
        self, valid_detection: Detection
    ) -> None:
        event_builder = SectionEventBuilder()
        event_builder.add_section_id(SectionId("N"))
        event_builder.add_event_type(EventType.SECTION_ENTER)
        with pytest.raises(IncompleteEventBuilderSetup):
            event_builder.create_event(valid_detection)

    def test_create_event_without_section_id_added(
        self, valid_detection: Detection
    ) -> None:
        event_builder = SectionEventBuilder()
        event_builder.add_direction_vector(Mock())
        event_builder.add_event_type(EventType.SECTION_ENTER)
        with pytest.raises(IncompleteEventBuilderSetup):
            event_builder.create_event(valid_detection)

    def test_create_event_without_event_coordinate_added(
        self, valid_detection: Detection
    ) -> None:
        event_builder = SectionEventBuilder()
        event_builder.add_direction_vector(Mock())
        event_builder.add_event_type(EventType.SECTION_ENTER)
        event_builder.add_section_id(SectionId("N"))
        with pytest.raises(IncompleteEventBuilderSetup):
            event_builder.create_event(valid_detection)

    def test_create_event_with_correctly_initialised_builder(
        self, valid_detection: Detection
    ) -> None:
        event_builder = SectionEventBuilder()
        event_builder.add_section_id(SectionId("N"))

        direction_vector = Mock(spec=DirectionVector2D)
        event_builder.add_direction_vector(direction_vector)

        event_builder.add_event_type(EventType.SECTION_ENTER)
        event_builder.add_road_user_type("car")
        event_builder.add_event_coordinate(1, 1)
        event_builder.add_interpolated_occurrence(INTERPOLATED_EVENT_OCCURRENCE)
        event_builder.add_interpolated_event_coordinate(1, 1)
        event = event_builder.create_event(valid_detection)

        assert event.road_user_id == valid_detection.track_id.id
        assert event.road_user_type == valid_detection.classification
        assert event.hostname == "myhostname"
        assert event.occurrence == valid_detection.occurrence
        assert event.frame_number == valid_detection.frame
        assert event.section_id == SectionId("N")
        assert event.event_coordinate == ImageCoordinate(1, 1)
        assert event.event_type == EventType.SECTION_ENTER
        assert event.direction_vector == direction_vector
        assert event.video_name == valid_detection.video_name
        assert event.interpolated_occurrence == INTERPOLATED_EVENT_OCCURRENCE


class TestSceneEventBuilder:
    def test_create_event_without_adds(self, valid_detection: Detection) -> None:
        event_builder = SceneEventBuilder()
        with pytest.raises(IncompleteEventBuilderSetup):
            event_builder.create_event(valid_detection)

    def test_create_event_without_event_type_added(
        self, valid_detection: Detection
    ) -> None:
        event_builder = SceneEventBuilder()
        event_builder.add_direction_vector(Mock())
        with pytest.raises(IncompleteEventBuilderSetup):
            event_builder.create_event(valid_detection)

    def test_create_event_without_direction_vector_added(
        self, valid_detection: Detection
    ) -> None:
        event_builder = SceneEventBuilder()
        event_builder.add_event_type(EventType.SECTION_ENTER)
        with pytest.raises(IncompleteEventBuilderSetup):
            event_builder.create_event(valid_detection)

    def test_create_event_without_event_coordinate_added(
        self, valid_detection: Detection
    ) -> None:
        event_builder = SceneEventBuilder()
        event_builder.add_direction_vector(Mock())
        event_builder.add_event_type(EventType.SECTION_ENTER)
        with pytest.raises(IncompleteEventBuilderSetup):
            event_builder.create_event(valid_detection)

    def test_create_event_with_correctly_initialised_builder(
        self, valid_detection: Detection
    ) -> None:
        event_builder = SceneEventBuilder()
        direction_vector = Mock(spec=DirectionVector2D)
        event_builder.add_direction_vector(direction_vector)
        event_builder.add_event_type(EventType.ENTER_SCENE)
        event_builder.add_event_coordinate(0, 0)
        event_builder.add_road_user_type("car")
        event = event_builder.create_event(valid_detection)

        assert event.road_user_id == valid_detection.track_id.id
        assert event.road_user_type == "car"
        assert event.hostname == "myhostname"
        assert event.occurrence == valid_detection.occurrence
        assert event.frame_number == valid_detection.frame
        assert event.section_id is None
        assert event.event_coordinate == ImageCoordinate(
            valid_detection.x, valid_detection.y
        )
        assert event.event_type == EventType.ENTER_SCENE
        assert event.direction_vector == direction_vector
        assert event.video_name == valid_detection.video_name
        assert event.event_coordinate == ImageCoordinate(0, 0)


def enter_scene_event_1() -> Event:
    return (
        event_builder.EventBuilder()
        .clean_section_id()
        .add_event_type(EventType.ENTER_SCENE.value)
        .add_second(1)
        .add_road_user_id(ROAD_USER_ID_1.id)
        .build_section_event()
    )


def event_1_section_1() -> Event:
    return (
        event_builder.EventBuilder()
        .add_section_id(SECTION_ID_1.id)
        .add_event_type(EventType.SECTION_ENTER.value)
        .add_second(1)
        .add_road_user_id(ROAD_USER_ID_1.id)
        .build_section_event()
    )


def event_1_section_2() -> Event:
    return (
        event_builder.EventBuilder()
        .add_section_id(SECTION_ID_2.id)
        .add_event_type(EventType.SECTION_ENTER.value)
        .add_second(2)
        .add_road_user_id(ROAD_USER_ID_1.id)
        .build_section_event()
    )


def event_2_section_1() -> Event:
    return (
        event_builder.EventBuilder()
        .add_section_id(SECTION_ID_1.id)
        .add_event_type(EventType.SECTION_LEAVE.value)
        .add_second(3)
        .add_road_user_id(ROAD_USER_ID_1.id)
        .build_section_event()
    )


def event_2_section_2() -> Event:
    return (
        event_builder.EventBuilder()
        .add_section_id(SECTION_ID_2.id)
        .add_event_type(EventType.SECTION_LEAVE.value)
        .add_second(4)
        .add_road_user_id(ROAD_USER_ID_1.id)
        .build_section_event()
    )


def event_3_section_1_road_user_2() -> Event:
    return (
        event_builder.EventBuilder()
        .add_section_id(SECTION_ID_1.id)
        .add_event_type(EventType.SECTION_ENTER.value)
        .add_second(1)
        .add_road_user_id(ROAD_USER_ID_2.id)
        .build_section_event()
    )


def event_3_section_2_road_user_2() -> Event:
    return (
        event_builder.EventBuilder()
        .add_section_id(SECTION_ID_2.id)
        .add_event_type(EventType.SECTION_LEAVE.value)
        .add_second(2)
        .add_road_user_id(ROAD_USER_ID_2.id)
        .build_section_event()
    )


def all_events() -> list[Event]:
    return [
        event_1_section_1(),
        event_2_section_1(),
        event_1_section_2(),
        event_2_section_2(),
    ]


class TestEventRepository:
    def test_add(self) -> None:
        event = event_1_section_1()
        subject = Mock()
        repository = EventRepository(subject)

        repository.add(event)

        assert event in repository.get_all()
        subject.notify.assert_called_with(EventRepositoryEvent([event], []))

    def test_add_same_event_twice(self) -> None:
        event_1_1 = event_1_section_1()
        event_1_2 = event_1_section_1()
        subject = Mock()
        repository = EventRepository(subject)

        repository.add(event_1_1)
        repository.add(event_1_2)

        actual = repository.get_all()
        expected = [event_1_1]
        assert actual == expected
        subject.notify.assert_called_with(EventRepositoryEvent([event_1_1], []))

    def test_add_without_section_id(self) -> None:
        event = Mock()
        event.section_id = None
        subject = Mock()
        repository = EventRepository(subject)

        repository.add(event)

        assert event in repository.get_all()
        subject.notify.assert_called_with(EventRepositoryEvent([event], []))

    def test_add_same_event_twice_without_section_id(self) -> None:
        event_1_1 = enter_scene_event_1()
        event_1_2 = enter_scene_event_1()
        subject = Mock()
        repository = EventRepository(subject)

        repository.add(event_1_1)
        repository.add(event_1_2)

        actual = repository.get_all()
        expected = [event_1_1]
        assert actual == expected
        subject.notify.assert_called_with(EventRepositoryEvent([event_1_1], []))

    def test_add_all(self) -> None:
        first_event = event_1_section_1()
        second_event = event_1_section_2()
        subject = Mock()
        repository = EventRepository(subject)

        repository.add_all([first_event, second_event])
        actual = list(repository.get_all())
        assert actual == [first_event, second_event]

        subject.notify.assert_called_with(
            EventRepositoryEvent([first_event, second_event], [])
        )

    def test_sort_after_add_all(self) -> None:
        repository = EventRepository()

        repository.add_all(
            [
                event_2_section_1(),
                event_1_section_2(),
                event_2_section_2(),
                event_1_section_1(),
            ]
        )

        actual = repository.get_all()
        expected = [
            event_1_section_1(),
            event_2_section_1(),
            event_1_section_2(),
            event_2_section_2(),
        ]
        assert actual == expected

    def test_sort_after_add(self) -> None:
        repository = EventRepository()
        repository.add(event_2_section_1())
        repository.add(event_1_section_2())
        repository.add(event_2_section_2())
        repository.add(event_1_section_1())

        actual = repository.get_all()
        expected = [
            event_1_section_1(),
            event_2_section_1(),
            event_1_section_2(),
            event_2_section_2(),
        ]
        assert actual == expected

    def test_no_event_for_intersected_section(self) -> None:
        section_id_1 = SectionId("1")
        section_id_2 = SectionId("2")
        section_1 = Mock(spec=Section)
        section_1.id = section_id_1
        section_2 = Mock(spec=Section)
        section_2.id = section_id_2
        first_event = Mock()
        first_event.section_id = section_id_1
        repository = EventRepository()

        repository.add_all([first_event], [section_id_1, section_id_2])
        missing_sections = repository.retain_missing([section_1, section_2])

        assert [first_event] == list(repository.get_all())
        assert not missing_sections

    def test_clear(self) -> None:
        subject = Mock()
        repository = EventRepository(subject)

        repository.add_all(
            [
                event_1_section_1(),
                event_1_section_2(),
                event_2_section_1(),
                enter_scene_event_1(),
            ]
        )
        repository.clear()

        assert not list(repository.get_all())
        subject.notify.assert_called_with(
            EventRepositoryEvent(
                [],
                [
                    enter_scene_event_1(),
                    event_1_section_1(),
                    event_2_section_1(),
                    event_1_section_2(),
                ],
            )
        )

    def test_remove(self) -> None:
        subject = Mock()
        repository = EventRepository(subject)

        repository.add_all([event_1_section_1(), event_1_section_2()])
        repository.remove([SECTION_ID_1])

        assert [event_1_section_2()] == list(repository.get_all())
        subject.notify.assert_called_with(
            EventRepositoryEvent([], [event_1_section_1()])
        )

    def test_remove_section_without_events(self) -> None:
        section_1 = SectionId("1")
        section_2 = SectionId("2")
        first_event = Mock()
        first_event.section_id = section_1
        subject = Mock()
        repository = EventRepository(subject)

        repository.add_all([first_event])
        repository.remove([section_2])

        assert [first_event] == list(repository.get_all())
        subject.notify.assert_called_with(EventRepositoryEvent([], []))

    def test_is_empty(self) -> None:
        repository = EventRepository()
        assert repository.is_empty()
        repository.add(Mock())
        assert not repository.is_empty()

    def test_get_all(self) -> None:
        repository = EventRepository()
        first_event = event_1_section_1()
        second_event = event_2_section_2()
        repository.add_all([first_event, second_event])
        actual = repository.get_all()
        assert actual == [first_event, second_event]
        assert actual  # ensure all events can not be exhausted

    @pytest.mark.parametrize(
        "input_event,expected_event,sections",
        [
            (event_1_section_1(), event_1_section_2(), []),
            (event_1_section_1(), event_2_section_1(), [SECTION_ID_1]),
            (event_1_section_2(), event_2_section_2(), [SECTION_ID_2]),
            (event_1_section_1(), event_1_section_2(), [SECTION_ID_1, SECTION_ID_2]),
        ],
    )
    def test_get_next_after(
        self,
        input_event: Event,
        expected_event: Event,
        sections: list[SectionId],
    ) -> None:
        repository = EventRepository()
        repository.add_all(all_events())

        actual_event = repository.get_next_after(input_event.occurrence, sections)

        assert actual_event == expected_event

    @pytest.mark.parametrize(
        "input_event,expected_event,sections",
        [
            (event_2_section_1(), event_1_section_2(), []),
            (event_2_section_1(), event_1_section_1(), [SECTION_ID_1]),
            (event_2_section_2(), event_1_section_2(), [SECTION_ID_2]),
            (event_2_section_1(), event_1_section_2(), [SECTION_ID_1, SECTION_ID_2]),
        ],
    )
    def test_get_previous_before(
        self,
        input_event: Event,
        expected_event: Event,
        sections: list[SectionId],
    ) -> None:
        repository = EventRepository()
        repository.add_all(all_events())

        actual_event = repository.get_previous_before(input_event.occurrence, sections)

        assert actual_event == expected_event

    @pytest.mark.parametrize(
        "start_date,end_date,sections,event_type,expected_events",
        [
            (
                None,
                None,
                [],
                [],
                all_events(),
            ),
            (
                event_2_section_2().occurrence,
                None,
                [],
                [],
                [event_2_section_2()],
            ),
            (
                event_2_section_1().occurrence,
                None,
                [],
                [],
                [event_2_section_1(), event_2_section_2()],
            ),
            (
                None,
                event_1_section_1().occurrence,
                [],
                [],
                [event_1_section_1()],
            ),
            (
                None,
                event_1_section_2().occurrence,
                [],
                [],
                [event_1_section_1(), event_1_section_2()],
            ),
            (
                None,
                event_2_section_1().occurrence,
                [],
                [],
                [event_1_section_1(), event_2_section_1(), event_1_section_2()],
            ),
            (
                event_1_section_2().occurrence,
                event_2_section_1().occurrence,
                [],
                [],
                [event_2_section_1(), event_1_section_2()],
            ),
            (
                None,
                None,
                [SECTION_ID_1],
                [],
                [event_1_section_1(), event_2_section_1()],
            ),
            (
                None,
                None,
                [SECTION_ID_2],
                [],
                [event_1_section_2(), event_2_section_2()],
            ),
            (None, None, [SECTION_ID_1, SECTION_ID_2], [], all_events()),
            (
                None,
                None,
                [SECTION_ID_1, SECTION_ID_2],
                DEFAULT_EVENT_TYPES,
                all_events(),
            ),
            (
                None,
                None,
                [SECTION_ID_1],
                [EventType.SECTION_ENTER],
                [event_1_section_1()],
            ),
            (
                None,
                None,
                [SECTION_ID_1],
                [EventType.SECTION_LEAVE],
                [event_2_section_1()],
            ),
        ],
    )
    def test_get(
        self,
        start_date: datetime,
        end_date: datetime,
        sections: list[SectionId],
        event_type: list[EventType],
        expected_events: list[Event],
    ) -> None:
        repository = EventRepository()
        repository.add_all(all_events())

        actual_events = repository.get(
            start_date=start_date,
            end_date=end_date,
            sections=sections,
            event_types=event_type,
        )

        assert actual_events == expected_events

    def test_remove_events_by_road_user_ids(self) -> None:
        target = EventRepository()
        target.add_all(
            [
                event_1_section_1(),
                event_2_section_2(),
                event_3_section_1_road_user_2(),
                event_3_section_2_road_user_2(),
                enter_scene_event_1(),
            ]
        )

        target.remove_events_by_road_user_ids([ROAD_USER_ID_1])
        actual = list(target.get_all())

        assert actual == [
            event_3_section_1_road_user_2(),
            event_3_section_2_road_user_2(),
        ]
