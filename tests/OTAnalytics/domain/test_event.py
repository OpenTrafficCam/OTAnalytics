from datetime import datetime
from pathlib import Path
from unittest.mock import Mock

import pytest

from OTAnalytics.domain.event import (
    DATE_FORMAT,
    DIRECTION_VECTOR,
    EVENT_COORDINATE,
    EVENT_TYPE,
    FRAME_NUMBER,
    HOSTNAME,
    OCCURRENCE,
    ROAD_USER_ID,
    ROAD_USER_TYPE,
    SECTION_ID,
    VIDEO_NAME,
    Event,
    EventRepository,
    EventType,
    EventTypeParseError,
    IncompleteEventBuilderSetup,
    SceneEventBuilder,
    SectionEventBuilder,
)
from OTAnalytics.domain.geometry import DirectionVector2D, ImageCoordinate
from OTAnalytics.domain.track import Detection, TrackId


@pytest.fixture
def valid_detection() -> Detection:
    return Detection(
        classification="car",
        confidence=0.5,
        x=0.0,
        y=0.0,
        w=15.3,
        h=30.5,
        frame=1,
        occurrence=datetime(2022, 1, 1, 0, 0, 0, 0),
        input_file_path=Path("path/to/myhostname_something.otdet"),
        interpolated_detection=False,
        track_id=TrackId(1),
    )


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
        with pytest.raises(ValueError):
            Event(
                road_user_id=1,
                road_user_type="car",
                hostname="my_hostname",
                occurrence=datetime(2022, 1, 1, 0, 0, 0, 0),
                frame_number=frame,
                section_id="N",
                event_coordinate=ImageCoordinate(0, 0),
                event_type=EventType.SECTION_ENTER,
                direction_vector=DirectionVector2D(1, 0),
                video_name="my_video_name.mp4",
            )

    @pytest.mark.parametrize("road_user_id", [-1, 0])
    def test_instantiate_event_with_invalid_road_user_id(
        self, road_user_id: int
    ) -> None:
        with pytest.raises(ValueError):
            Event(
                road_user_id=road_user_id,
                road_user_type="car",
                hostname="myhostname",
                occurrence=datetime(2022, 1, 1, 0, 0, 0, 0),
                frame_number=1,
                section_id="N",
                event_coordinate=ImageCoordinate(0, 0),
                event_type=EventType.SECTION_ENTER,
                direction_vector=DirectionVector2D(1, 0),
                video_name="my_video_name.mp4",
            )

    def test_instantiate_with_valid_args(self) -> None:
        occurrence = datetime(2022, 1, 1, 0, 0, 0, 0)
        event_coordinate = ImageCoordinate(0, 0)
        direction = DirectionVector2D(1, 0)
        event = Event(
            road_user_id=1,
            road_user_type="car",
            hostname="my_hostname",
            occurrence=occurrence,
            frame_number=1,
            section_id="N",
            event_coordinate=event_coordinate,
            event_type=EventType.SECTION_ENTER,
            direction_vector=direction,
            video_name="my_video_name.mp4",
        )
        assert event.road_user_id == 1
        assert event.road_user_type == "car"
        assert event.hostname == "my_hostname"
        assert event.occurrence == occurrence
        assert event.frame_number == 1
        assert event.section_id == "N"
        assert event.event_coordinate == event_coordinate
        assert event.event_type == EventType.SECTION_ENTER
        assert event.direction_vector == direction
        assert event.video_name == "my_video_name.mp4"

    def test_to_dict(self) -> None:
        road_user_id = 1
        road_user_type = "car"
        hostname = "myhostname"
        occurrence = datetime(2022, 1, 1, 0, 0, 0, 0)
        frame_number = 1
        section_id = "N"
        event_coordinate = ImageCoordinate(0, 0)
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
        )
        event_dict = event.to_dict()
        expected = {
            ROAD_USER_ID: road_user_id,
            ROAD_USER_TYPE: road_user_type,
            HOSTNAME: hostname,
            OCCURRENCE: occurrence.strftime(DATE_FORMAT),
            FRAME_NUMBER: frame_number,
            SECTION_ID: section_id,
            EVENT_COORDINATE: [event_coordinate.x, event_coordinate.y],
            EVENT_TYPE: EventType.SECTION_ENTER.value,
            DIRECTION_VECTOR: [direction_vector.x1, direction_vector.x2],
            VIDEO_NAME: video_name,
        }

        assert event_dict == expected


class TestSectionEventBuilder:
    def test_create_event_without_adds(self, valid_detection: Detection) -> None:
        event_builder = SectionEventBuilder()
        with pytest.raises(IncompleteEventBuilderSetup):
            event_builder.create_event(valid_detection)

    def test_create_event_without_event_type_added(
        self, valid_detection: Detection
    ) -> None:
        event_builder = SectionEventBuilder()
        event_builder.add_section_id("N")
        event_builder.add_direction_vector(valid_detection, valid_detection)
        with pytest.raises(IncompleteEventBuilderSetup):
            event_builder.create_event(valid_detection)

    def test_create_event_without_direction_vector_added(
        self, valid_detection: Detection
    ) -> None:
        event_builder = SectionEventBuilder()
        event_builder.add_section_id("N")
        event_builder.add_event_type(EventType.SECTION_ENTER)
        with pytest.raises(IncompleteEventBuilderSetup):
            event_builder.create_event(valid_detection)

    def test_create_event_without_section_id_added(
        self, valid_detection: Detection
    ) -> None:
        event_builder = SectionEventBuilder()
        event_builder.add_direction_vector(valid_detection, valid_detection)
        event_builder.add_event_type(EventType.SECTION_ENTER)
        with pytest.raises(IncompleteEventBuilderSetup):
            event_builder.create_event(valid_detection)

    def test_create_event_with_correctly_initialised_builder(
        self, valid_detection: Detection
    ) -> None:
        event_builder = SectionEventBuilder()
        event_builder.add_section_id("N")
        event_builder.add_direction_vector(valid_detection, valid_detection)
        event_builder.add_event_type(EventType.SECTION_ENTER)
        event_builder.add_road_user_type("car")
        event = event_builder.create_event(valid_detection)

        assert event.road_user_id == valid_detection.track_id.id
        assert event.road_user_type == valid_detection.classification
        assert event.hostname == "myhostname"
        assert event.occurrence == valid_detection.occurrence
        assert event.frame_number == valid_detection.frame
        assert event.section_id == "N"
        assert event.event_coordinate == ImageCoordinate(
            valid_detection.x, valid_detection.y
        )
        assert event.event_type == EventType.SECTION_ENTER
        assert event.direction_vector == DirectionVector2D(0, 0)
        assert event.video_name == valid_detection.input_file_path.name


class TestSceneEventBuilder:
    def test_create_event_without_adds(self, valid_detection: Detection) -> None:
        event_builder = SceneEventBuilder()
        with pytest.raises(IncompleteEventBuilderSetup):
            event_builder.create_event(valid_detection)

    def test_create_event_without_event_type_added(
        self, valid_detection: Detection
    ) -> None:
        event_builder = SceneEventBuilder()
        event_builder.add_direction_vector(valid_detection, valid_detection)
        with pytest.raises(IncompleteEventBuilderSetup):
            event_builder.create_event(valid_detection)

    def test_create_event_without_direction_vector_added(
        self, valid_detection: Detection
    ) -> None:
        event_builder = SceneEventBuilder()
        event_builder.add_event_type(EventType.SECTION_ENTER)
        with pytest.raises(IncompleteEventBuilderSetup):
            event_builder.create_event(valid_detection)

    def test_create_event_with_correctly_initialised_builder(
        self, valid_detection: Detection
    ) -> None:
        event_builder = SceneEventBuilder()
        event_builder.add_direction_vector(valid_detection, valid_detection)
        event_builder.add_event_type(EventType.ENTER_SCENE)
        event = event_builder.create_event(valid_detection)

        assert event.road_user_id == valid_detection.track_id.id
        assert event.road_user_type == valid_detection.classification
        assert event.hostname == "myhostname"
        assert event.occurrence == valid_detection.occurrence
        assert event.frame_number == valid_detection.frame
        assert event.section_id is None
        assert event.event_coordinate == ImageCoordinate(
            valid_detection.x, valid_detection.y
        )
        assert event.event_type == EventType.ENTER_SCENE
        assert event.direction_vector == DirectionVector2D(0, 0)
        assert event.video_name == valid_detection.input_file_path.name


class TestEventRepository:
    def test_add(self) -> None:
        event = Mock()
        repository = EventRepository()

        repository.add(event)

        assert event in repository.get_all()

    def test_add_all(self) -> None:
        first_event = Mock()
        second_event = Mock()
        repository = EventRepository()

        repository.add_all([first_event, second_event])

        assert first_event in repository.get_all()
        assert second_event in repository.get_all()
