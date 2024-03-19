from typing import Iterable

from pandas import DataFrame

from OTAnalytics.domain import event, track
from OTAnalytics.domain.event import Event, EventRepository
from OTAnalytics.domain.progress import ProgressbarBuilder
from OTAnalytics.domain.types import EventType
from OTAnalytics.plugin_filter.dataframe_filter import DataFrameFilterBuilder
from OTAnalytics.plugin_prototypes.track_visualization.track_viz import (
    PandasDataFrameProvider,
)


class PandasEventProvider(PandasDataFrameProvider):
    """Provides events as pandas DataFrame."""

    def __init__(
        self,
        event_repository: EventRepository,
        filter_builder: DataFrameFilterBuilder,
        progressbar: ProgressbarBuilder,
    ) -> None:
        self._event_repository = event_repository
        self._filter_builder = filter_builder
        self._progressbar = progressbar

    def get_data(self) -> DataFrame:
        events = self._event_repository.get_all()
        if not events:
            return DataFrame()

        return self._convert_tracks(events)

    def _convert_tracks(self, events: Iterable[Event]) -> DataFrame:
        """
        Convert events into a dataframe.

        Args:
            events (Iterable[Event]): events to convert.

        Returns:
            DataFrame: events as dataframe.
        """
        prepared: list[dict] = [current.to_typed_dict() for current in events]

        if not prepared:
            return DataFrame()
        for current in prepared:
            current[track.X] = current[event.EVENT_COORDINATE][0]
            current[track.Y] = current[event.EVENT_COORDINATE][1]
        data = DataFrame(prepared)
        data = data.rename(
            columns={
                event.ROAD_USER_ID: track.TRACK_ID,
                event.ROAD_USER_TYPE: track.TRACK_CLASSIFICATION,
                event.OCCURRENCE: track.OCCURRENCE,
                event.FRAME_NUMBER: track.FRAME,
                event.VIDEO_NAME: track.VIDEO_NAME,
            }
        )
        data = data.loc[data[event.EVENT_TYPE] == EventType.SECTION_ENTER.value, :]
        df = data.set_index([track.TRACK_ID, track.OCCURRENCE])
        df.index.names = [track.TRACK_ID, track.OCCURRENCE]

        return self._sort_tracks(df)

    def _sort_tracks(self, data: DataFrame) -> DataFrame:
        """Sort the given dataframe by track id and occurrence,

        Args:
            data (DataFrame): dataframe of events

        Returns:
            DataFrame: sorted dataframe by track id and frame
        """
        if data.empty:
            return data
        return data.sort_index()
