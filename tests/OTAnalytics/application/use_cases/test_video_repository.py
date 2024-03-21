from unittest.mock import Mock

from OTAnalytics.application.use_cases.video_repository import (
    AddAllVideos,
    ClearAllVideos,
    GetAllVideos,
)
from OTAnalytics.domain.video import VideoRepository


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
