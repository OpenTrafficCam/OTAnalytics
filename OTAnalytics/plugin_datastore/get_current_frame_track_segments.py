from OTAnalytics.application.use_cases.create_intersection_events import GetTracks
from OTAnalytics.domain.track_dataset.track_dataset import TrackDataset
from OTAnalytics.plugin_datastore.pandas_track_dataset_factory import (
    PandasTrackDatasetFactory,
)
from OTAnalytics.plugin_datastore.track_store import (
    FilterByIdPandasTrackDataset,
    FilterLastNDetectionsPandasTrackDataset,
)

NUMBER_OF_DETECTIONS_TO_FORM_SEGMENT = 2


class GetCurrentFrameTrackSegments:
    def __init__(
        self,
        get_all_tracks: GetTracks,
        track_ids: list[str],
        track_dataset_factory: PandasTrackDatasetFactory,
    ) -> None:
        self._get_all_tracks = get_all_tracks
        self._track_ids = track_ids
        self._track_dataset_factory = track_dataset_factory

    def as_dataset(self) -> TrackDataset:
        all_tracks = self._track_dataset_factory.from_dataset(
            self._get_all_tracks.as_dataset()
        )
        other = FilterByIdPandasTrackDataset(all_tracks, track_ids=self._track_ids)
        return FilterLastNDetectionsPandasTrackDataset(
            other, NUMBER_OF_DETECTIONS_TO_FORM_SEGMENT
        )
