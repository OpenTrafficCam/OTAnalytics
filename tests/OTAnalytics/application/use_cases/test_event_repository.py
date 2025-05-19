from unittest.mock import Mock, patch

import pytest

from OTAnalytics.application.use_cases.event_repository import (
    AddEvents,
    ClearAllEvents,
    RemoveEventsByRoadUserId,
)
from OTAnalytics.domain.event import Event, EventRepository
from OTAnalytics.domain.section import SectionId, SectionRepositoryEvent
from OTAnalytics.domain.track import TrackId
from OTAnalytics.domain.track_repository import TrackRepositoryEvent


@pytest.fixture
def events() -> list[Mock]:
    return [Mock(spec=Event), Mock(spec=Event)]


@pytest.fixture
def sections() -> list[SectionId]:
    return [SectionId("section")]


@pytest.fixture
def event_repository() -> Mock:
    return Mock(spec=EventRepository)


class TestAddEvents:
    def test_add(
        self, event_repository: Mock, events: list[Event], sections: list[SectionId]
    ) -> None:
        add_events = AddEvents(event_repository)
        add_events(events, sections)
        event_repository.add_all.assert_called_once_with(events, sections)


class TestClearAllEvents:
    def test_clear(self) -> None:
        repository = Mock(spec=EventRepository)
        clear_all_events = ClearAllEvents(repository)
        clear_all_events()
        repository.clear.assert_called_once()

    def test_remove_events_of_changed_sections(self) -> None:
        section_1 = SectionId("1")
        repository = Mock(spec=EventRepository)
        clear_all_events = ClearAllEvents(repository)

        clear_all_events.notify_sections(
            SectionRepositoryEvent.create_removed([section_1])
        )

        repository.remove.assert_called_once_with([section_1])


class TestRemoveEventsByRoadUserId:
    def test_remove_multiple(self) -> None:
        given_event_repository = Mock(spec=EventRepository)
        given_road_user_ids = [TrackId("1"), TrackId("2")]
        target = RemoveEventsByRoadUserId(given_event_repository)
        target.remove_multiple(given_road_user_ids)

        given_event_repository.remove_events_by_road_user_ids.assert_called_once_with(
            given_road_user_ids
        )

    @patch(
        (
            "OTAnalytics.application.use_cases.event_repository."
            "RemoveEventsByRoadUserId.remove_multiple"
        )
    )
    def test_notify_tracks(self, mock_remove_multiple: Mock) -> None:
        given_event = TrackRepositoryEvent(added=Mock(), removed=Mock())

        target = RemoveEventsByRoadUserId(Mock())
        target.notify_tracks(given_event)

        mock_remove_multiple.assert_called_once_with(given_event.removed)
