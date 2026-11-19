from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

from OTAnalytics.domain import event, track
from OTAnalytics.domain.event import Event, EventRepository
from OTAnalytics.domain.progress import NoProgressbarBuilder
from OTAnalytics.domain.types import EventType
from OTAnalytics.plugin_prototypes.event_visualization import PolarsEventProvider

ROAD_USER_TYPE = "car"
HOSTNAME = "hostname"
SECTION_ID = "section"
VIDEO_NAME = "video"
START_TIME = datetime(2020, 1, 1, tzinfo=timezone.utc)
DIRECTION_VECTOR = [1.0, 0.0]
INTERPOLATED_EVENT_COORDINATE = [0.0, 0.0]
Y_SCALE = 2

FIRST_ROAD_USER = "1"
SECOND_ROAD_USER = "2"
FIRST_ENTER_FRAME = 1
FIRST_LEAVE_FRAME = 2
SECOND_ENTER_FRAME = 3


def event_coordinate(frame: int) -> tuple[float, float]:
    return float(frame), float(frame * Y_SCALE)


def create_event(road_user_id: str, event_type: EventType, frame: int) -> Mock:
    current = Mock(spec=Event)
    current.to_typed_dict.return_value = {
        event.ROAD_USER_ID: road_user_id,
        event.ROAD_USER_TYPE: ROAD_USER_TYPE,
        event.HOSTNAME: HOSTNAME,
        event.OCCURRENCE: START_TIME + timedelta(seconds=frame),
        event.FRAME_NUMBER: frame,
        event.SECTION_ID: SECTION_ID,
        event.EVENT_COORDINATE: list(event_coordinate(frame)),
        event.EVENT_TYPE: event_type.value,
        event.DIRECTION_VECTOR: DIRECTION_VECTOR,
        event.VIDEO_NAME: VIDEO_NAME,
        event.INTERPOLATED_OCCURRENCE: None,
        event.INTERPOLATED_EVENT_COORDINATE: INTERPOLATED_EVENT_COORDINATE,
        event.GEO_X: None,
        event.GEO_Y: None,
    }
    return current


class TestPolarsEventProvider:
    def test_get_data_contains_sorted_section_enter_events(self) -> None:
        event_repository = Mock(spec=EventRepository)
        event_repository.get_all.return_value = [
            create_event(SECOND_ROAD_USER, EventType.SECTION_ENTER, SECOND_ENTER_FRAME),
            create_event(FIRST_ROAD_USER, EventType.SECTION_LEAVE, FIRST_LEAVE_FRAME),
            create_event(FIRST_ROAD_USER, EventType.SECTION_ENTER, FIRST_ENTER_FRAME),
        ]
        provider = PolarsEventProvider(event_repository, Mock(), NoProgressbarBuilder())

        result = provider.get_data()

        enter_frames = [FIRST_ENTER_FRAME, SECOND_ENTER_FRAME]
        expected_x, expected_y = zip(*map(event_coordinate, enter_frames))
        assert result.get_column(track.TRACK_ID).to_list() == [
            FIRST_ROAD_USER,
            SECOND_ROAD_USER,
        ]
        assert result.get_column(track.TRACK_CLASSIFICATION).to_list() == [
            ROAD_USER_TYPE,
            ROAD_USER_TYPE,
        ]
        assert result.get_column(track.FRAME).to_list() == enter_frames
        assert result.get_column(track.X).to_list() == list(expected_x)
        assert result.get_column(track.Y).to_list() == list(expected_y)

    def test_get_data_without_events(self) -> None:
        event_repository = Mock(spec=EventRepository)
        event_repository.get_all.return_value = []
        provider = PolarsEventProvider(event_repository, Mock(), NoProgressbarBuilder())

        assert provider.get_data().is_empty()
