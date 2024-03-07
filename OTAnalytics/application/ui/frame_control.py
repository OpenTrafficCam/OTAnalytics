from abc import ABC, abstractmethod
from datetime import timedelta

from OTAnalytics.application.state import TrackViewState, VideosMetadata
from OTAnalytics.domain.date import DateRange


class SwitchTo(ABC):
    def __init__(self, state: TrackViewState, videos_metadata: VideosMetadata) -> None:
        self._state = state
        self._videos_metadata = videos_metadata

    def switch_second(self) -> None:
        skip_time = self._state.skip_time.get()
        current_skip = timedelta(seconds=skip_time.seconds)
        self._switch_time(current_skip)

    def switch_frame(self) -> None:
        if current_skip := self._get_current_skip_frames():
            self._switch_time(current_skip)

    def _get_current_skip_frames(self) -> timedelta | None:
        if filter_element := self._state.filter_element.get():
            current_date_range = filter_element.date_range
            if current_date_range.start_date and current_date_range.end_date:
                if metadata := self._videos_metadata.get_metadata_for(
                    current_date_range.end_date
                ):
                    fps = metadata.fps
                    skip_time = self._state.skip_time.get()
                    subseconds = min(skip_time.frames, fps) / fps
                    milliseconds = subseconds * 1000
                    current_skip = timedelta(milliseconds=milliseconds)
                    return current_skip
        return None

    @abstractmethod
    def _switch_time(self, current_skip: timedelta) -> None:
        raise NotImplementedError


class SwitchToNext(SwitchTo):

    def __init__(self, state: TrackViewState, videos_metadata: VideosMetadata) -> None:
        super().__init__(state, videos_metadata)

    def _switch_time(self, current_skip: timedelta) -> None:
        if filter_element := self._state.filter_element.get():
            current_date_range = filter_element.date_range
            if current_date_range.start_date and current_date_range.end_date:
                next_start = current_date_range.start_date + current_skip
                next_end = current_date_range.end_date + current_skip
                next_date_range = DateRange(next_start, next_end)
                self._state.filter_element.set(
                    filter_element.derive_date(next_date_range)
                )


class SwitchToPrevious(SwitchTo):
    def __init__(self, state: TrackViewState, videos_metadata: VideosMetadata) -> None:
        super().__init__(state, videos_metadata)

    def _switch_time(self, current_skip: timedelta) -> None:
        if filter_element := self._state.filter_element.get():
            current_date_range = filter_element.date_range
            if current_date_range.start_date and current_date_range.end_date:
                next_start = current_date_range.start_date - current_skip
                next_end = current_date_range.end_date - current_skip
                next_date_range = DateRange(next_start, next_end)
                self._state.filter_element.set(
                    filter_element.derive_date(next_date_range)
                )
