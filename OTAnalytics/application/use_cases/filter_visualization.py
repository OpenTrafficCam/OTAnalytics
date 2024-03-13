from datetime import datetime, timedelta

from OTAnalytics.application.state import TrackViewState, VideosMetadata
from OTAnalytics.domain.date import DateRange
from OTAnalytics.domain.filter import FilterElement

DEFAULT_DURATION = timedelta(seconds=10)


class CreateDefaultFilterRange:
    def __init__(
        self,
        state: TrackViewState,
        videos_metadata: VideosMetadata,
        duration: timedelta = DEFAULT_DURATION,
    ) -> None:
        self._state = state
        self._videos_metadata = videos_metadata
        self._duration = duration

    def create(self) -> None:
        if video_start := self._videos_metadata.first_video_start:
            new_filter = self.__create_new_filter_element(video_start)
            self._state.filter_element.set(new_filter)

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
