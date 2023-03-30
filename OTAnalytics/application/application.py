from pathlib import Path
from typing import Optional

from OTAnalytics.application.datastore import Datastore
from OTAnalytics.application.state import SectionState, TrackState
from OTAnalytics.domain.track import TrackId, TrackImage


class OTAnalyticsApplication:
    def __init__(
        self, datastore: Datastore, track_state: TrackState, section_state: SectionState
    ) -> None:
        self._datastore: Datastore = datastore
        self.track_state: TrackState = track_state
        self.section_state: SectionState = section_state
        self._connect_observers()

    def _connect_observers(self) -> None:
        self._datastore.register_tracks_observer(self.track_state)
        self._datastore.register_sections_observer(self.section_state)

    def add_tracks_of_file(self, track_file: Path) -> None:
        self._datastore.load_track_file(file=track_file)

    def add_sections_of_file(self, sections_file: Path) -> None:
        self._datastore.load_section_file(file=sections_file)

    def get_image_of_track(self, track_id: TrackId) -> Optional[TrackImage]:
        return self._datastore.get_image_of_track(track_id)
