import polars as pl

from OTAnalytics.domain.track import TRACK_ID
from OTAnalytics.domain.track_dataset.track_dataset import EmptyTrackIdSet, TrackIdSet
from OTAnalytics.domain.track_id_provider import TrackIdProvider
from OTAnalytics.plugin_datastore.polars_track_id_set import PolarsTrackIdSet
from OTAnalytics.plugin_datastore.track_store import PandasDataFrameProvider


class PandasTrackIdProvider(TrackIdProvider):
    def __init__(self, pandas_data_frame_provider: PandasDataFrameProvider) -> None:
        self._pandas_data_frame_provider = pandas_data_frame_provider

    def get_ids(self) -> TrackIdSet:
        data = self._pandas_data_frame_provider.get_data()

        if data.empty:
            return EmptyTrackIdSet()

        if TRACK_ID not in list(data.index.names):
            raise ValueError(
                f"{TRACK_ID}"
                "must be in the index of DataFrame for retrieving all track ids."
            )
        series = data.index.get_level_values(TRACK_ID).unique()
        return PolarsTrackIdSet(pl.from_pandas(series).cast(pl.Utf8))
