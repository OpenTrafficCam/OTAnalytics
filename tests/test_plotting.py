from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest
from application.datastore import VideoMetadata
from domain.date import DateRange
from domain.filter import FilterElement

from OTAnalytics.application.plotting import GetCurrentFrame, GetCurrentVideo
from OTAnalytics.application.state import TrackViewState, VideosMetadata


class TestGetCurrentVideoPath:
    def test_get_video(self) -> None:
        filter_end_date = datetime(2023, 1, 1, 0, 1)
        mocked_filter_element = FilterElement(
            DateRange(start_date=None, end_date=filter_end_date), classifications={}
        )
        video_path = "some/path"
        state = TrackViewState()
        state.filter_element.set(mocked_filter_element)
        metadata = Mock(spec=VideoMetadata)
        metadata.path = video_path
        videos_metadata = Mock(spec=VideosMetadata)
        videos_metadata.get_metadata_for.return_value = metadata
        use_case = GetCurrentVideo(state, videos_metadata)

        actual = use_case.get_video()

        assert actual == video_path


class TestGetCurrentFrame:
    @pytest.mark.parametrize(
        "filter_end_date, expected_frame_number",
        [
            (datetime(2023, 1, 1, 0, 1), 0),
            (datetime(2023, 1, 1, 0, 1, 1), 20),
            (datetime(2023, 1, 1, 0, 1, 3), 60),
            (datetime(2023, 1, 1, 0, 1, 4), 60),
        ],
    )
    def test_get_frame_number(
        self,
        filter_end_date: datetime,
        expected_frame_number: int,
    ) -> None:
        video_start_date = datetime(2023, 1, 1, 0, 1)
        mocked_filter_element = FilterElement(
            DateRange(start_date=None, end_date=filter_end_date), classifications={}
        )
        state = TrackViewState()
        state.filter_element.set(mocked_filter_element)
        metadata = Mock(spec=VideoMetadata)
        metadata.start = video_start_date
        metadata.duration = timedelta(seconds=3)
        metadata.fps = 20
        metadata.number_of_frames = 60
        videos_metadata = Mock(spec=VideosMetadata)
        videos_metadata.get_metadata_for.return_value = metadata
        use_case = GetCurrentFrame(state, videos_metadata)

        frame_number = use_case.get_frame_number()

        assert frame_number == expected_frame_number

        videos_metadata.get_metadata_for.assert_called_with(filter_end_date)
