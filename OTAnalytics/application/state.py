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
    """
    This state represents the currently selected track.
    """

    def __init__(self) -> None:
        self.selected_track: Optional[TrackId] = None
        self.observers: TrackSubject = TrackSubject()

    def register(self, observer: TrackObserver) -> None:
        """
        Listen to changes of the currently selected track.

        Args:
            observer (TrackObserver): listener to be notified about changes
        """
        self.observers.register(observer)

    def select(self, track_id: TrackId) -> None:
        """
        Select the given track.

        Args:
            track_id (TrackId): track to be selected
        """
        if self.selected_track != track_id:
            self.selected_track = track_id
            self._notify_observers()

    def _notify_observers(self) -> None:
        """
        Notify observers about the currently selected track.
        """
        self.observers.notify(self.selected_track)

    def notify_tracks(self, tracks: list[TrackId]) -> None:
        """
        Notify the state about changes in the track list.

        Args:
            tracks (list[TrackId]): newly added tracks

        Raises:
            IndexError: if the list of tracks is empty
        """
        if not tracks:
            raise IndexError("No tracks to select")
        self.select(tracks[0])


class SectionState(SectionListObserver):
    """
    This state represents the currently selected section.
    """

    def __init__(self) -> None:
        self.selected_section: Optional[SectionId] = None
        self.observers: SectionSubject = SectionSubject()

    def register(self, observer: SectionObserver) -> None:
        """
        Listen to changes of the currently selected section.

        Args:
            observer (SectionObserver): listener to be notified about changes
        """
        self.observers.register(observer)

    def select(self, section_id: SectionId) -> None:
        """
        Select the given section.

        Args:
            section_id (SectionId): section to be selected
        """
        if self.selected_section != section_id:
            self.selected_section = section_id
            self._notify_observers()

    def _notify_observers(self) -> None:
        """
        Notify observers about the currently selected section.
        """
        self.observers.notify(self.selected_section)

    def notify_sections(self, sections: list[SectionId]) -> None:
        """
        Notify the state about changes in the section list.

        Args:
            sections (list[SectionId]): newly added sections

        Raises:
            IndexError: if the list of sections is empty
        """
        if not sections:
            raise IndexError("No section to select")
        self.select(sections[0])
