from datetime import datetime
from unittest.mock import Mock

import pytest

from OTAnalytics.application.state import VideosMetadata
from OTAnalytics.application.use_cases.filter_visualization import (
    CreateDefaultFilterRange,
    EnableFilterTrackByDate,
)
from OTAnalytics.domain.date import DateRange
from OTAnalytics.domain.filter import FilterElement
from tests.utils.state import create_filter_element, create_track_view_state

START_DATE = datetime(2023, 1, 1, 0, 0, 0)
END_DATE = datetime(2023, 1, 1, 0, 0, 1)
FILTER_DURATION = END_DATE - START_DATE


@pytest.fixture
def videos_metadata() -> VideosMetadata:
    videos_metadata = Mock(spec=VideosMetadata)
    videos_metadata.first_video_start = START_DATE
    return videos_metadata


class TestCreateDefaultFilterRange:

    @pytest.mark.parametrize(
        "start_date, end_date,expected_start_date,expected_end_date",
        [
            (None, None, START_DATE - FILTER_DURATION, START_DATE),
            (START_DATE, None, START_DATE, START_DATE + FILTER_DURATION),
            (None, END_DATE, END_DATE - FILTER_DURATION, END_DATE),
        ],
    )
    def test_create_default_filter_range(
        self,
        videos_metadata: Mock,
        start_date: datetime,
        end_date: datetime,
        expected_start_date: datetime,
        expected_end_date: datetime,
    ) -> None:
        enable_filter_track_by_date = Mock(spec=EnableFilterTrackByDate)
        filter_element = create_filter_element(start_date=start_date, end_date=end_date)
        track_view_state = create_track_view_state(filter_element, True)
        derived_filter_element = Mock(spec=FilterElement)
        filter_element.derive_date.return_value = derived_filter_element
        use_case = CreateDefaultFilterRange(
            track_view_state,
            videos_metadata=videos_metadata,
            duration=FILTER_DURATION,
            enable_filter_track_by_date=enable_filter_track_by_date,
        )

        use_case.create()

        filter_element.derive_date.assert_called_once_with(
            DateRange(expected_start_date, expected_end_date)
        )
        track_view_state.filter_element.set.assert_called_once_with(
            derived_filter_element
        )
        track_view_state.filter_date_active.set.assert_called_once_with(True)
        enable_filter_track_by_date.enable.assert_called_once()

    def test_do_nothing_if_filter_is_already_set(self, videos_metadata: Mock) -> None:
        enable_filter_track_by_date = Mock(spec=EnableFilterTrackByDate)
        filter_element = create_filter_element(start_date=START_DATE, end_date=END_DATE)
        track_view_state = create_track_view_state(filter_element, True)
        use_case = CreateDefaultFilterRange(
            track_view_state,
            videos_metadata=videos_metadata,
            duration=FILTER_DURATION,
            enable_filter_track_by_date=enable_filter_track_by_date,
        )

        use_case.create()

        filter_element.derive_date.assert_not_called()
        track_view_state.filter_element.set.assert_called_once_with(filter_element)
        track_view_state.filter_date_active.set.assert_called_once_with(True)
        enable_filter_track_by_date.enable.assert_called_once()
