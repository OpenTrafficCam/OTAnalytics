from typing import Iterable

from OTAnalytics.application.use_cases.cut_tracks_with_sections import CutTracksDto
from OTAnalytics.domain.event import Event, EventRepository
from OTAnalytics.domain.section import (
    SectionId,
    SectionListObserver,
    SectionRepositoryEvent,
)
from OTAnalytics.domain.track_repository import TrackListObserver, TrackRepositoryEvent
from OTAnalytics.domain.types import EventType


class AddEvents:
    """Add events to the repository."""

    def __init__(self, event_repository: EventRepository) -> None:
        self._event_repository = event_repository

    def __call__(
        self, events: Iterable[Event], sections: list[SectionId] | None = None
    ) -> None:
        if sections is None:
            sections = []
        if events:
            self._event_repository.add_all(events, sections)


class ClearAllEvents(SectionListObserver, TrackListObserver):
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

    def notify_sections(self, section_event: SectionRepositoryEvent) -> None:
        self._event_repository.remove(list(section_event.removed))

    def notify_tracks(self, track_event: TrackRepositoryEvent) -> None:
        self.clear()

    def on_section_changed(self, section_id: SectionId) -> None:
        self._event_repository.remove([section_id])

    def on_tracks_cut(self, _: CutTracksDto) -> None:
        self.clear()


class GetAllEnterSectionEvents:
    """Get all enter section events from the event repository"""

    def __init__(self, event_repository: EventRepository) -> None:
        self._event_repository = event_repository

    def get(self) -> Iterable[Event]:
        return self._event_repository.get(event_types=[EventType.SECTION_ENTER])
