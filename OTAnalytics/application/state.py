from typing import Optional

from OTAnalytics.domain.section import (
    SectionId,
    SectionListObserver,
    SectionObserver,
    SectionSubject,
)
from OTAnalytics.domain.track import (
    TrackId,
    TrackListObserver,
    TrackObserver,
    TrackSubject,
)


class TrackState(TrackListObserver):
    def __init__(self) -> None:
        self.selected_track: Optional[TrackId] = None
        self.observers: TrackSubject = TrackSubject()

    def register(self, observer: TrackObserver) -> None:
        self.observers.register(observer)

    def update(self, track_id: TrackId) -> None:
        if self.selected_track != track_id:
            self.selected_track = track_id
            self._notify_observers()

    def _notify_observers(self) -> None:
        self.observers.notify(self.selected_track)

    def notify_tracks(self, tracks: list[TrackId]) -> None:
        if not tracks:
            raise IndexError("No tracks to select")
        self.update(tracks[0])


class SectionState(SectionListObserver):
    def __init__(self) -> None:
        self.selected_section: Optional[SectionId] = None
        self.observers: SectionSubject = SectionSubject()

    def register(self, observer: SectionObserver) -> None:
        self.observers.register(observer)

    def update(self, section_id: SectionId) -> None:
        if self.selected_section != section_id:
            self.selected_section = section_id
            self._notify_observers()

    def _notify_observers(self) -> None:
        self.observers.notify(self.selected_section)

    def notify_sections(self, sections: list[SectionId]) -> None:
        if not sections:
            raise IndexError("No tracks to select")
        self.update(sections[0])
