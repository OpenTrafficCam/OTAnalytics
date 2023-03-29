from pathlib import Path

from OTAnalytics.application.datastore import Datastore
from OTAnalytics.application.state import TrackState


class OTAnalyticsApplication:
    def __init__(self, datastore: Datastore, track_state: TrackState) -> None:
        self._datastore: Datastore = datastore
        self.track_state: TrackState = track_state
        self._connect_observers()

    def _connect_observers(self) -> None:
        self._datastore.register_tracks_observer(self.track_state)

    def add_tracks_of_file(self, track_file: Path) -> None:
        self._datastore.load_track_file(file=track_file)

    def add_sections_of_file(self, sections_file: Path) -> None:
        self._datastore.load_section_file(file=sections_file)
