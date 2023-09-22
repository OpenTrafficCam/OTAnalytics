from unittest.mock import Mock

from OTAnalytics.application.datastore import TrackToVideoRepository
from OTAnalytics.application.use_cases.track_to_video_repository import (
    ClearAllTrackToVideos,
)


class TestClearAllTrackToVideos:
    def test_clear(self) -> None:
        repository = Mock(spec=TrackToVideoRepository)
        clear_all_track_to_videos = ClearAllTrackToVideos(repository)
        clear_all_track_to_videos()
        repository.clear.assert_called_once()
