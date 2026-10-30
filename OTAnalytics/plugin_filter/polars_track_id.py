import polars as pl

from OTAnalytics.domain.track import TRACK_ID
from OTAnalytics.domain.track_dataset.track_dataset import EmptyTrackIdSet, TrackIdSet
from OTAnalytics.domain.track_id_provider import TrackIdProvider
from OTAnalytics.plugin_datastore.polars_track_id_set import PolarsTrackIdSet
from OTAnalytics.plugin_datastore.polars_track_store import PolarsDataFrameProvider


class PolarsTrackIdProvider(TrackIdProvider):
    def __init__(self, polars_data_frame_provider: PolarsDataFrameProvider) -> None:
        self._polars_data_frame_provider = polars_data_frame_provider

    def get_ids(self) -> TrackIdSet:
        data = self._polars_data_frame_provider.get_data()

        if data.is_empty():
            return EmptyTrackIdSet()

        if TRACK_ID not in data.columns:
            raise ValueError(
                f"{TRACK_ID} must be a column of DataFrame "
                "for retrieving all track ids."
            )
        series = data.get_column(TRACK_ID).unique(maintain_order=True)
        return PolarsTrackIdSet(series.cast(pl.Utf8))
