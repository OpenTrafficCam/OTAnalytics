from datetime import timedelta

from OTAnalytics.application.state import TrackViewState, VideosMetadata
from OTAnalytics.domain.date import DateRange


class GetNextFrame:
    def __init__(self, state: TrackViewState, videos_metadata: VideosMetadata) -> None:
        self._state = state
        self._videos_metadata = videos_metadata

    def set_next_frame(self) -> None:
        if filter_element := self._state.filter_element.get():
            current_date_range = filter_element.date_range
            if current_date_range.start_date and current_date_range.end_date:
                if metadata := self._videos_metadata.get_metadata_for(
                    current_date_range.end_date
                ):
                    fps = metadata.fps
                    skip_time = self._state.skip_time.get()
                    subseconds = min(skip_time.frames, fps) / fps
                    current_skip = timedelta(seconds=skip_time.seconds) + timedelta(
                        seconds=subseconds
                    )
                    next_start = current_date_range.start_date + current_skip
                    next_end = current_date_range.end_date + current_skip
                    next_date_range = DateRange(next_start, next_end)
                    self._state.filter_element.set(
                        filter_element.derive_date(next_date_range)
                    )


class GetPreviousFrame:
    def __init__(self, state: TrackViewState, videos_metadata: VideosMetadata) -> None:
        self._state = state
        self._videos_metadata = videos_metadata

    def set_previous_frame(self) -> None:
        if filter_element := self._state.filter_element.get():
            current_date_range = filter_element.date_range
            if current_date_range.start_date and current_date_range.end_date:
                if metadata := self._videos_metadata.get_metadata_for(
                    current_date_range.end_date
                ):
                    fps = metadata.fps
                    skip_time = self._state.skip_time.get()
                    subseconds = min(skip_time.frames, fps) / fps
                    current_skip = timedelta(seconds=skip_time.seconds) + timedelta(
                        seconds=subseconds
                    )
                    next_start = current_date_range.start_date - current_skip
                    next_end = current_date_range.end_date - current_skip
                    next_date_range = DateRange(next_start, next_end)
                    self._state.filter_element.set(
                        filter_element.derive_date(next_date_range)
                    )
