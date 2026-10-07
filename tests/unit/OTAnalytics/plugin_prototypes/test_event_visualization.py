from datetime import datetime, timezone
from unittest.mock import Mock

from OTAnalytics.domain import event, track
from OTAnalytics.domain.event import Event, EventRepository
from OTAnalytics.domain.progress import NoProgressbarBuilder
from OTAnalytics.domain.types import EventType
from OTAnalytics.plugin_prototypes.event_visualization import PolarsEventProvider


def create_event(road_user_id: str, event_type: EventType, frame: int) -> Mock:
    current = Mock(spec=Event)
    current.to_typed_dict.return_value = {
        event.ROAD_USER_ID: road_user_id,
        event.ROAD_USER_TYPE: "car",
        event.HOSTNAME: "hostname",
        event.OCCURRENCE: datetime(2020, 1, 1, 0, 0, frame, tzinfo=timezone.utc),
        event.FRAME_NUMBER: frame,
        event.SECTION_ID: "section",
        event.EVENT_COORDINATE: [float(frame), float(frame * 2)],
        event.EVENT_TYPE: event_type.value,
        event.DIRECTION_VECTOR: [1.0, 0.0],
        event.VIDEO_NAME: "video",
        event.INTERPOLATED_OCCURRENCE: None,
        event.INTERPOLATED_EVENT_COORDINATE: [0.0, 0.0],
        event.GEO_X: None,
        event.GEO_Y: None,
    }
    return current


class TestPolarsEventProvider:
    def test_get_data_contains_sorted_section_enter_events(self) -> None:
        event_repository = Mock(spec=EventRepository)
        event_repository.get_all.return_value = [
            create_event("2", EventType.SECTION_ENTER, 3),
            create_event("1", EventType.SECTION_LEAVE, 2),
            create_event("1", EventType.SECTION_ENTER, 1),
        ]
        provider = PolarsEventProvider(event_repository, Mock(), NoProgressbarBuilder())

        result = provider.get_data()

        assert result.get_column(track.TRACK_ID).to_list() == ["1", "2"]
        assert result.get_column(track.TRACK_CLASSIFICATION).to_list() == [
            "car",
            "car",
        ]
        assert result.get_column(track.FRAME).to_list() == [1, 3]
        assert result.get_column(track.X).to_list() == [1.0, 3.0]
        assert result.get_column(track.Y).to_list() == [2.0, 6.0]

    def test_get_data_without_events(self) -> None:
        event_repository = Mock(spec=EventRepository)
        event_repository.get_all.return_value = []
        provider = PolarsEventProvider(event_repository, Mock(), NoProgressbarBuilder())

        assert provider.get_data().is_empty()
