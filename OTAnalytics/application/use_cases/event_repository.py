from typing import Iterable

from OTAnalytics.application.use_cases.cut_tracks_with_sections import CutTracksDto
from OTAnalytics.domain.event import Event, EventRepository
from OTAnalytics.domain.section import SectionId, SectionListObserver
from OTAnalytics.domain.track import TrackListObserver, TrackRepositoryEvent


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

    def notify_sections(self, sections: list[SectionId]) -> None:
        self._event_repository.remove(sections)

    def notify_tracks(self, track_event: TrackRepositoryEvent) -> None:
        self.clear()

    def on_section_changed(self, section_id: SectionId) -> None:
        self._event_repository.remove([section_id])

    def on_tracks_cut(self, _: CutTracksDto) -> None:
        self.clear()
