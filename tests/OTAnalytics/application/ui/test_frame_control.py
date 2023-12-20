from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest

from OTAnalytics.application.datastore import VideoMetadata
from OTAnalytics.application.playback import SkipTime
from OTAnalytics.application.state import (
    ObservableProperty,
    TrackViewState,
    VideosMetadata,
)
from OTAnalytics.application.ui.frame_control import GetNextFrame, GetPreviousFrame
from OTAnalytics.domain.date import DateRange
from OTAnalytics.domain.filter import FilterElement

FPS = 1
TIME_OF_A_FRAME = timedelta(seconds=1) / FPS
START_DATE = datetime(2023, 1, 1, 0, 0, 0)
END_DATE = datetime(2023, 1, 1, 0, 0, 1)


def observable(value: Mock) -> Mock:
    observable_property = Mock(spec=ObservableProperty)
    observable_property.get.return_value = value
    return observable_property


@pytest.fixture
def filter_element() -> Mock:
    filter_element = Mock(spec=FilterElement)
    filter_element.date_range = DateRange(START_DATE, END_DATE)
    return filter_element


@pytest.fixture
def skip_time() -> Mock:
    skip_time = Mock(spec=SkipTime)
    skip_time.seconds = 0
    skip_time.frames = 1
    return skip_time


@pytest.fixture
def track_view_state(filter_element: Mock, skip_time: Mock) -> Mock:
    track_view_state = Mock(spec=TrackViewState)
    track_view_state.filter_element = observable(filter_element)
    track_view_state.skip_time = observable(skip_time)
    return track_view_state


@pytest.fixture
def videos_metadata() -> VideosMetadata:
    metadata = Mock(spec=VideoMetadata)
    metadata.fps = FPS
    videos_metadata = Mock(spec=VideosMetadata)
    videos_metadata.get_metadata_for.return_value = metadata
    return videos_metadata


class TestGetNextFrame:
    def test_set_next_frame(
        self,
        track_view_state: Mock,
        videos_metadata: Mock,
        filter_element: Mock,
    ) -> None:
        derived_filter_element = Mock(spec=FilterElement)
        filter_element.derive_date.return_value = derived_filter_element

        new_date_range = DateRange(
            START_DATE + TIME_OF_A_FRAME, END_DATE + TIME_OF_A_FRAME
        )
        use_case = GetNextFrame(track_view_state, videos_metadata)

        use_case.set_next_frame()

        filter_element.derive_date.assert_called_with(new_date_range)
        track_view_state.filter_element.set.assert_called_with(derived_filter_element)
        videos_metadata.get_metadata_for.assert_called_with(END_DATE)


class TestGetPreviousFrame:
    def test_set_next_frame(
        self,
        track_view_state: Mock,
        videos_metadata: Mock,
        filter_element: Mock,
    ) -> None:
        derived_filter_element = Mock(spec=FilterElement)
        filter_element.derive_date.return_value = derived_filter_element

        new_date_range = DateRange(
            START_DATE - TIME_OF_A_FRAME, END_DATE - TIME_OF_A_FRAME
        )
        use_case = GetPreviousFrame(track_view_state, videos_metadata)

        use_case.set_previous_frame()

        filter_element.derive_date.assert_called_with(new_date_range)
        track_view_state.filter_element.set.assert_called_with(derived_filter_element)
        videos_metadata.get_metadata_for.assert_called_with(END_DATE)
