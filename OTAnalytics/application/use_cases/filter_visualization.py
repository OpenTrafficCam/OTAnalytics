from abc import ABC, abstractmethod
from datetime import datetime, timedelta

from OTAnalytics.application.state import TrackViewState, VideosMetadata
from OTAnalytics.domain.date import DateRange
from OTAnalytics.domain.filter import FilterElement, FilterElementSettingRestorer

DEFAULT_DURATION = timedelta(seconds=10)


class EnableFilterTrackByDate:
    def __init__(
        self,
        track_view_state: TrackViewState,
        filter_element_setting_restorer: FilterElementSettingRestorer,
    ):
        self._track_view_state = track_view_state
        self._filter_element_setting_restorer = filter_element_setting_restorer

    def enable(self) -> None:
        current_filter_element = self._track_view_state.filter_element.get()
        restored_filter_element = (
            self._filter_element_setting_restorer.restore_by_date_filter_setting(
                current_filter_element
            )
        )
        self._track_view_state.filter_element.set(restored_filter_element)


class CreateDefaultFilter(ABC):
    @abstractmethod
    def create(self) -> None:
        raise NotImplementedError


class CreateDefaultFilterRange(CreateDefaultFilter):
    def __init__(
        self,
        state: TrackViewState,
        videos_metadata: VideosMetadata,
        enable_filter_track_by_date: EnableFilterTrackByDate,
        duration: timedelta = DEFAULT_DURATION,
    ) -> None:
        self._state = state
        self._videos_metadata = videos_metadata
        self._enable_filter_track_by_date = enable_filter_track_by_date
        self._duration = duration

    def create(self) -> None:
        if video_start := self._videos_metadata.first_video_start:
            new_filter = self.__create_new_filter_element(video_start)
            self._enable_filter_track_by_date.enable()
            self._state.filter_element.set(new_filter)
            self._state.filter_date_active.set(True)

    def __create_new_filter_element(self, video_start: datetime) -> FilterElement:
        filter_element = self._state.filter_element.get()
        date_range = filter_element.date_range
        if date_range.start_date and date_range.end_date:
            return filter_element
        if not date_range.start_date and date_range.end_date is not None:
            new_range = DateRange(
                start_date=date_range.end_date - self._duration,
                end_date=date_range.end_date,
            )
            return filter_element.derive_date(new_range)
        if not date_range.end_date and date_range.start_date is not None:
            new_range = DateRange(
                start_date=date_range.start_date,
                end_date=date_range.start_date + self._duration,
            )
            return filter_element.derive_date(new_range)

        start_date = video_start - self._duration
        new_range = DateRange(start_date=start_date, end_date=video_start)
        return filter_element.derive_date(new_range)
