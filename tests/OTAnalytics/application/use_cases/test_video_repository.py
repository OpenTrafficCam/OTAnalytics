from unittest.mock import Mock

from OTAnalytics.application.use_cases.video_repository import (
    AddAllVideos,
    ClearAllVideos,
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
