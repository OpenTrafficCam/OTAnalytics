from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

import pytest
from pytest_lazy_fixtures import lf

from OTAnalytics.application.use_cases.video_repository import (
    AddAllVideos,
    ClearAllVideos,
    GetAllVideos,
    GetVideos,
)
from OTAnalytics.domain.video import Video, VideoRepository


class TestClearAllTrackToVideos:
    def test_clear(self) -> None:
        repository = Mock(spec=VideoRepository)
        clear_all_videos = ClearAllVideos(repository)
        clear_all_videos()
        repository.clear.assert_called_once()


class TestAddAllVideos:
    def test_add(self) -> None:
        repository = Mock(spec=VideoRepository)
        video = Mock()

        add_all = AddAllVideos(repository)
        add_all.add([video])
        repository.add_all.assert_called_once_with([video])


class TestGetAllVideos:
    def test_get(self) -> None:
        expected_videos = Mock()
        repository = Mock(spec=VideoRepository)
        repository.get_all.return_value = expected_videos

        get_all = GetAllVideos(repository)
        actual_videos = get_all.get()

        assert actual_videos == expected_videos
        repository.get_all.assert_called_once()


def first_video_date() -> datetime:
    return datetime(2020, 1, 1).replace(tzinfo=timezone.utc)


def video_duration() -> timedelta:
    return timedelta(seconds=1)


def second_video_date() -> datetime:
    return datetime(2020, 1, 2).replace(tzinfo=timezone.utc)


@pytest.fixture
def first_video() -> Video:
    video = Mock(spec=Video)
    video.start_date = first_video_date()
    video.end_date = video.start_date + video_duration()
    return video


@pytest.fixture
def second_video() -> Video:
    video = Mock(spec=Video)
    video.start_date = second_video_date()
    video.end_date = video.start_date + video_duration()
    return video


@pytest.fixture
def video_without_start_date() -> Video:
    """
    https://openproject.platomo.de/wp/7277
    """
    video = Mock(spec=Video)
    video.start_date = None
    video.end_date = None
    return video


class TestGetVideos:

    def test_get(self, first_video: Mock) -> None:
        current = first_video_date()
        repository = Mock(spec=VideoRepository)
        repository.get_by_date.return_value = [first_video]

        get = GetVideos(repository)
        actual_video = get.get(current)

        assert actual_video == first_video
        repository.get_by_date.assert_called_once_with(current)

    def test_get_not_found(self) -> None:
        current = first_video_date()
        repository = Mock(spec=VideoRepository)
        repository.get_by_date.return_value = []

        get = GetVideos(repository)
        actual_video = get.get(current)

        assert actual_video is None
        repository.get_by_date.assert_called_once_with(current)

    @pytest.mark.parametrize(
        "query_date, get_by_date, expected_videos",
        [
            (second_video_date(), [], []),
            (first_video_date(), [lf("first_video")], [lf("second_video")]),
            (
                first_video_date() - video_duration(),
                [],
                [lf("first_video"), lf("second_video")],
            ),
        ],
    )
    def test_get_after(
        self,
        first_video: Mock,
        second_video: Mock,
        video_without_start_date: Mock,
        query_date: datetime,
        get_by_date: list[Video],
        expected_videos: list[Video],
    ) -> None:
        repository = Mock(spec=VideoRepository)
        repository.get_by_date.return_value = get_by_date
        repository.get_all.return_value = [
            first_video,
            second_video,
            video_without_start_date,
        ]

        get = GetVideos(repository)
        actual_videos = get.get_after(query_date)

        assert actual_videos == expected_videos
        repository.get_by_date.assert_called_once_with(query_date)
        repository.get_all.assert_called_once()

    @pytest.mark.parametrize(
        "query_date, get_by_date, expected_videos",
        [
            (first_video_date(), [], []),
            (second_video_date(), [lf("second_video")], [lf("first_video")]),
            (
                second_video_date() + 2 * video_duration(),
                [],
                [lf("first_video"), lf("second_video")],
            ),
        ],
    )
    def test_get_before(
        self,
        first_video: Mock,
        second_video: Mock,
        query_date: datetime,
        get_by_date: list[Video],
        expected_videos: list[Video],
    ) -> None:
        repository = Mock(spec=VideoRepository)
        repository.get_by_date.return_value = get_by_date
        repository.get_all.return_value = [first_video, second_video]

        get = GetVideos(repository)
        actual_videos = get.get_before(query_date)

        assert actual_videos == expected_videos
        repository.get_by_date.assert_called_once_with(query_date)
        repository.get_all.assert_called_once()
