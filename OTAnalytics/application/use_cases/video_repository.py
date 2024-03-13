from typing import Iterable

from OTAnalytics.domain.video import Video, VideoRepository


class ClearAllVideos:
    """Clear video repository.

    Args:
        video_repository (VideoRepository): the repository to clear.
    """

    def __init__(self, video_repository: VideoRepository) -> None:
        self._video_repository = video_repository

    def __call__(self) -> None:
        """Clear the video repository."""
        self._video_repository.clear()


class AddAllVideos:

    def __init__(self, video_repository: VideoRepository) -> None:
        self._video_repository = video_repository

    def add(self, videos: Iterable[Video]) -> None:
        self._video_repository.add_all(videos)
