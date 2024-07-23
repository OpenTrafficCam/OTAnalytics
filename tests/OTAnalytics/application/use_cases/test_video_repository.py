from datetime import datetime
from unittest.mock import Mock

import pytest

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


class TestGetVideos:

    def first_video_date(self) -> datetime:
        return datetime(2020, 1, 1)

    @pytest.fixture
    def first_video(self) -> Video:
        video = Mock(spec=Video)
        video.start_date = self.first_video_date()
        return video

    def second_video_date(self) -> datetime:
        return datetime(2020, 1, 2)

    @pytest.fixture
    def second_video(self) -> Video:
        video = Mock(spec=Video)
        video.start_date = self.second_video_date()
        return video

    def test_get(self, first_video: Mock) -> None:
        current = self.first_video_date()
        repository = Mock(spec=VideoRepository)
        repository.get_by_date.return_value = [first_video]

        get = GetVideos(repository)
        actual_video = get.get(current)

        assert actual_video == first_video
        repository.get_by_date.assert_called_once_with(current)

    def test_get_not_found(self) -> None:
        current = self.first_video_date()
        repository = Mock(spec=VideoRepository)
        repository.get_by_date.return_value = []

        get = GetVideos(repository)
        actual_video = get.get(current)

        assert actual_video is None
        repository.get_by_date.assert_called_once_with(current)

    def test_get_after(self, first_video: Mock, second_video: Mock) -> None:
        current = self.first_video_date()
        repository = Mock(spec=VideoRepository)
        repository.get_by_date.return_value = [first_video]
        repository.get_all.return_value = [first_video, second_video]

        get = GetVideos(repository)
        actual_videos = get.get_after(current)

        assert actual_videos == [second_video]
        repository.get_by_date.assert_called_once_with(current)
        repository.get_all.assert_called_once()

    def test_get_before(self, first_video: Mock, second_video: Mock) -> None:
        current = self.second_video_date()
        repository = Mock(spec=VideoRepository)
        repository.get_by_date.return_value = [second_video]
        repository.get_all.return_value = [first_video, second_video]

        get = GetVideos(repository)
        actual_videos = get.get_before(current)

        assert actual_videos == [first_video]
        repository.get_by_date.assert_called_once_with(current)
        repository.get_all.assert_called_once()
