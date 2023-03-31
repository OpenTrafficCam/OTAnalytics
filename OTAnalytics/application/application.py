from pathlib import Path
from typing import Optional

from domain.event import Event

from OTAnalytics.application.analysis import RunIntersect
from OTAnalytics.application.datastore import Datastore
from OTAnalytics.application.state import SectionState, TrackState
from OTAnalytics.domain.track import TrackId, TrackImage


class OTAnalyticsApplication:
    """
    Entrypoint for calls from the UI.
    """

    def __init__(
        self,
        datastore: Datastore,
        track_state: TrackState,
        section_state: SectionState,
        intersect: RunIntersect,
    ) -> None:
        self._datastore: Datastore = datastore
        self.track_state: TrackState = track_state
        self.section_state: SectionState = section_state
        self._intersect = intersect
        self._connect_observers()

    def _connect_observers(self) -> None:
        """
        Connect the observers with the repositories to listen to domain object changes.
        """
        self._datastore.register_tracks_observer(self.track_state)
        self._datastore.register_sections_observer(self.section_state)

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
        events: list[Event] = self._intersect.run(
            tracks=self._datastore._track_repository.get_all(),
            sections=self._datastore._section_repository.get_all(),
        )
        self._datastore._event_repository.add_all(events)

    def save_events(self, file: Path) -> None:
        self._datastore.save_event_list_file(file)
