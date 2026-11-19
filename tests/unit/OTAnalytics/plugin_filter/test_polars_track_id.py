from unittest.mock import Mock

import pytest
from polars import DataFrame

from OTAnalytics.domain.track import TRACK_ID, TrackId
from OTAnalytics.domain.track_dataset.track_dataset import EmptyTrackIdSet
from OTAnalytics.plugin_datastore.polars_track_store import PolarsDataFrameProvider
from OTAnalytics.plugin_filter.polars_track_id import PolarsTrackIdProvider

FIRST_TRACK_ID = "1"
SECOND_TRACK_ID = "2"


def create_provider(data: DataFrame) -> Mock:
    provider = Mock(spec=PolarsDataFrameProvider)
    provider.get_data.return_value = data
    return provider


class TestPolarsTrackIdProvider:
    def test_get_ids(self) -> None:
        data = DataFrame({TRACK_ID: [FIRST_TRACK_ID, FIRST_TRACK_ID, SECOND_TRACK_ID]})

        ids = PolarsTrackIdProvider(create_provider(data)).get_ids()

        assert set(ids) == {TrackId(FIRST_TRACK_ID), TrackId(SECOND_TRACK_ID)}

    def test_get_ids_of_empty_dataframe(self) -> None:
        ids = PolarsTrackIdProvider(create_provider(DataFrame())).get_ids()

        assert isinstance(ids, EmptyTrackIdSet)

    def test_get_ids_without_track_id_column(self) -> None:
        provider = PolarsTrackIdProvider(
            create_provider(DataFrame({"other": [FIRST_TRACK_ID]}))
        )

        with pytest.raises(ValueError):
            provider.get_ids()
