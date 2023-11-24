from unittest.mock import Mock

import pytest

from OTAnalytics.application.use_cases.event_repository import AddEvents, ClearAllEvents
from OTAnalytics.domain.event import Event, EventRepository
from OTAnalytics.domain.section import SectionId, SectionRepositoryEvent


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
