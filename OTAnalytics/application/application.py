from pathlib import Path
from typing import Iterable, Optional

from domain.section import Section, SectionListObserver

from OTAnalytics.application.analysis import RunIntersect
from OTAnalytics.application.datastore import Datastore
from OTAnalytics.application.state import SectionState, TrackState, TrackViewState
from OTAnalytics.domain.track import TrackId, TrackImage


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
        self._connect_observers()

    def _connect_observers(self) -> None:
        """
        Connect the observers with the repositories to listen to domain object changes.
        """
        self._datastore.register_tracks_observer(self.track_state)
        self._datastore.register_sections_observer(self.section_state)

    def register_sections_observer(self, observer: SectionListObserver) -> None:
        self._datastore.register_sections_observer(observer)

    def get_all_sections(self) -> Iterable[Section]:
        return self._datastore.get_all_sections()

    def add_tracks_of_file(self, track_file: Path) -> None:
        """
        Load a single track file.

        Args:
            track_file (Path): file in ottrk format
        """
        self._datastore.load_track_file(file=track_file)

    def add_sections_of_file(self, sections_file: Path) -> None:
        """
        Load sections from a sections file.

        Args:
            sections_file (Path): file in sections format
        """
        self._datastore.load_section_file(file=sections_file)

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
