from pathlib import Path
from typing import Iterable, Optional

from OTAnalytics.application.analysis import RunIntersect
from OTAnalytics.application.datastore import Datastore
from OTAnalytics.application.state import SectionState, TrackState, TrackViewState
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate
from OTAnalytics.domain.section import Section, SectionId, SectionListObserver
from OTAnalytics.domain.track import TrackId, TrackImage
from OTAnalytics.domain.types import EventType


class OTAnalyticsApplication:
    """
    Entrypoint for calls from the UI.
    """

    def __init__(
        self,
        datastore: Datastore,
        track_state: TrackState,
        track_view_state: TrackViewState,
        section_state: SectionState,
        intersect: RunIntersect,
    ) -> None:
        self._datastore: Datastore = datastore
        self.track_state: TrackState = track_state
        self.track_view_state: TrackViewState = track_view_state
        self.section_state: SectionState = section_state
        self._intersect = intersect

    def connect_observers(self) -> None:
        """
        Connect the observers with the repositories to listen to domain object changes.
        """
        self._datastore.register_tracks_observer(self.track_state)
        self._datastore.register_sections_observer(self.section_state)

    def register_sections_observer(self, observer: SectionListObserver) -> None:
        self._datastore.register_sections_observer(observer)

    def get_all_sections(self) -> Iterable[Section]:
        return self._datastore.get_all_sections()

    def get_section_for(self, section_id: SectionId) -> Optional[Section]:
        return self._datastore.get_section_for(section_id)

    def add_tracks_of_file(self, track_file: Path) -> None:
        """
        Load a single track file.

        Args:
            track_file (Path): file in ottrk format
        """
        self._datastore.load_track_file(file=track_file)

    def add_tracks_of_files(self, track_files: list[Path]) -> None:
        """
        Load a multiple track files.

        Args:
            track_files (list[Path]): files in ottrk format
        """
        self._datastore.load_track_files(files=track_files)

    def delete_all_tracks(self) -> None:
        """Delete all tracks."""
        self._datastore.delete_all_tracks()

    def add_sections_of_file(self, sections_file: Path) -> None:
        """
        Load sections from a sections file.

        Args:
            sections_file (Path): file in sections format
        """
        self._datastore.load_section_file(file=sections_file)

    def add_section(self, section: Section) -> None:
        """
        Add a new section

        Args:
            section (Section): section to add
        """
        self._datastore.add_section(section)

    def remove_section(self, section: SectionId) -> None:
        """
        Remove the section

        Args:
            section (SectionId): section to remove
        """
        self._datastore.remove_section(section)

    def update_section(self, section: Section) -> None:
        """
        Update the section.

        Args:
            section (Section): updated section
        """
        self._datastore.update_section(section)

    def save_sections(self, file: Path) -> None:
        """
        Save the section repository into a file.

        Args:
            file (Path): file to save the sections to
        """
        self._datastore.save_section_file(file)

    def get_image_of_track(self, track_id: TrackId) -> Optional[TrackImage]:
        """
        Retrieve an image for the given track.

        Args:
            track_id (TrackId): identifier for the track

        Returns:
            Optional[TrackImage]: an image of the track if the track is available and
            the image can be loaded
        """
        return self._datastore.get_image_of_track(track_id)

    def start_analysis(self) -> None:
        """
        Intersect all tracks with all sections and write the events into the event
        repository
        """
        self._intersect.run()

    def save_events(self, file: Path) -> None:
        """
        Save the event repository into a file.

        Args:
            file (Path): file to save the events to
        """
        self._datastore.save_event_list_file(file)

    def change_to_section_offset(
        self, event_type: EventType = EventType.SECTION_ENTER
    ) -> None:
        """
        Change the offset to visualize tracks to the offset of the currently selected
        section.

        Args:
            event_type (EventType, optional): event type of the offset at the section.
            Defaults to EventType.SECTION_ENTER.
        """
        # TODO update after line section PR has been merged
        if section_id := self.section_state.selected_section.get():
            if section := self._datastore.get_section_for(section_id):
                if offset := section.relative_offset_coordinates.get(event_type):
                    self.track_view_state.track_offset.set(offset)

    def set_selected_section(self, id: Optional[str]) -> None:
        """Set the current selected section in the UI.

        Args:
            id (SectionId): the id of the currently selected section
        """
        if id:
            section_id = SectionId(id)
        else:
            section_id = None

        self.section_state.selected_section.set(section_id)

    def get_current_track_offset(self) -> Optional[RelativeOffsetCoordinate]:
        """Get the current track offset.

        Returns:
            Optional[RelativeOffsetCoordinate]: the current track offset.
        """
        return self.track_view_state.track_offset.get()
