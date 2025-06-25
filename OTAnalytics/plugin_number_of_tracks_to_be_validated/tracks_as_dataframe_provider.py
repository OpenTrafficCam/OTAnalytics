from pandas import DataFrame

from OTAnalytics.application.use_cases.track_repository import GetAllTracks
from OTAnalytics.domain.track_dataset.track_dataset import TRACK_GEOMETRY_FACTORY
from OTAnalytics.plugin_datastore.track_store import (
    DEFAULT_CLASSIFICATOR,
    PandasDataFrameProvider,
    PandasTrackClassificationCalculator,
    PandasTrackDataset,
)


class TracksAsDataFrameProvider:
    def __init__(
        self,
        get_all_tracks: GetAllTracks,
        track_geometry_factory: TRACK_GEOMETRY_FACTORY,
        calculator: PandasTrackClassificationCalculator = DEFAULT_CLASSIFICATOR,
    ) -> None:
        self._get_all_tracks = get_all_tracks
        self._geometry_factory = track_geometry_factory
        self._calculator = calculator

    def provide(self) -> DataFrame | None:
        track_dataset = self._get_all_tracks.as_dataset()
        if track_dataset.empty:
            return None

        if isinstance(track_dataset, PandasDataFrameProvider):
            return track_dataset.get_data()
        return self._convert_tracks_to_data_frame()

    def _convert_tracks_to_data_frame(self) -> DataFrame:
        return PandasTrackDataset.from_list(
            tracks=self._get_all_tracks.as_list(),
            track_geometry_factory=self._geometry_factory,
            calculator=self._calculator,
        ).get_data()
