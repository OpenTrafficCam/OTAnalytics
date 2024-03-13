from abc import ABC, abstractmethod
from datetime import timedelta

from OTAnalytics.application.state import TrackViewState, VideosMetadata
from OTAnalytics.domain.date import DateRange
from OTAnalytics.domain.event import Event, EventRepository
from OTAnalytics.domain.filter import FilterElement


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


class SwitchToEvent:

    def __init__(
        self, event_repository: EventRepository, track_view_state: TrackViewState
    ) -> None:
        self._event_repository = event_repository
        self._track_view_state = track_view_state

    def switch_to_previous(self) -> None:
        if end_date := self.__current_filter_element.date_range.end_date:
            if event := self._event_repository.get_previous_before(end_date):
                self.__switch_to(event)

    def switch_to_next(self) -> None:
        if end_date := self.__current_filter_element.date_range.end_date:
            if event := self._event_repository.get_next_after(end_date):
                self.__switch_to(event)

    def __switch_to(self, event: Event) -> None:
        new_end_date = event.occurrence
        if duration := self.__current_filter_element.date_range.duration():
            new_start_date = event.occurrence - duration
            new_range = DateRange(start_date=new_start_date, end_date=new_end_date)
            new_filter_element = self.__current_filter_element.derive_date(new_range)
            self._track_view_state.filter_element.set(new_filter_element)

    @property
    def __current_filter_element(self) -> FilterElement:
        return self._track_view_state.filter_element.get()
