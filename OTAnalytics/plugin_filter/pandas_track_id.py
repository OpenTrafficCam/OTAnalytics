from typing import Iterable

from OTAnalytics.domain.track import TRACK_ID, TrackId, TrackIdProvider
from OTAnalytics.plugin_datastore.track_store import PandasDataFrameProvider


class PandasTrackIdProvider(TrackIdProvider):
    def __init__(self, pandas_data_frame_provider: PandasDataFrameProvider) -> None:
        self._pandas_data_frame_provider = pandas_data_frame_provider

    def get_ids(self) -> Iterable[TrackId]:
        data = self._pandas_data_frame_provider.get_data()

        if data.empty:
            return []

        if TRACK_ID not in list(data.index.names):
            raise ValueError(
                f"{TRACK_ID}"
                "must be in the index of DataFrame for retrieving all track ids."
            )

        return [TrackId(id) for id in data.index.get_level_values(TRACK_ID)]
