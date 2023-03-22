from datetime import datetime
from pathlib import Path

import pytest

from OTAnalytics.domain.event import (
    Event,
    EventType,
    IncompleteEventBuilderSetup,
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


class TestEvent:
    @pytest.mark.parametrize("frame", [-1, 0])
    def test_instantiate_event_with_invalid_frame_number(self, frame: int) -> None:
        with pytest.raises(ValueError):
            Event(
                road_user_id=0,
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
