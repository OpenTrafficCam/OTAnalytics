from unittest.mock import Mock

import pytest

from OTAnalytics.application.use_cases.event_repository import (
    AddEvents,
    ClearEventRepository,
)
from OTAnalytics.domain.event import Event, EventRepository


@pytest.fixture
def events() -> list[Mock]:
    return [Mock(spec=Event), Mock(spec=Event)]


@pytest.fixture
def event_repository() -> Mock:
    return Mock(spec=EventRepository)


class TestAddEvents:
    def test_add(self, event_repository: Mock, events: list[Event]) -> None:
        add_events = AddEvents(event_repository)
        add_events(events)
        event_repository.add_all.assert_called_once_with(events)


class TestClearEventRepository:
    def test_clear(self) -> None:
        repository = Mock(spec=EventRepository)
        clear_event_repository = ClearEventRepository(repository)
        clear_event_repository.clear()
        repository.clear.assert_called_once()
