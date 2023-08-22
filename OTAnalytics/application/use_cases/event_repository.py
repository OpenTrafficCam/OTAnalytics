from typing import Iterable

from OTAnalytics.domain.event import Event, EventRepository
from OTAnalytics.domain.section import SectionId, SectionListObserver
from OTAnalytics.domain.track import TrackId, TrackListObserver


class AddEvents:
    """Add events to the repository."""

    def __init__(self, event_repository: EventRepository) -> None:
        self._event_repository = event_repository

    def __call__(self, events: Iterable[Event]) -> None:
        if events:
            self._event_repository.add_all(events)


class ClearEventRepository(SectionListObserver, TrackListObserver):
    """Clears the event repository also on section state changes.

    Args:
        event_repository (EventRepository): the event repository
    """

    def __init__(self, event_repository: EventRepository) -> None:
        self._event_repository = event_repository

    def __call__(self) -> None:
        self.clear()

    def clear(self) -> None:
        self._event_repository.clear()

    def notify_sections(self, sections: list[SectionId]) -> None:
        self.clear()

    def notify_tracks(self, tracks: list[TrackId]) -> None:
        self.clear()

    def on_section_changed(self, section_id: SectionId) -> None:
        self.clear()