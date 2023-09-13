from unittest.mock import Mock

from OTAnalytics.application.use_cases.video_repository import ClearAllVideos
from OTAnalytics.domain.video import VideoRepository


class TestClearAllTrackToVideos:
    def test_clear(self) -> None:
        repository = Mock(spec=VideoRepository)
        clear_all_videos = ClearAllVideos(repository)
        clear_all_videos()
        repository.clear.assert_called_once()
