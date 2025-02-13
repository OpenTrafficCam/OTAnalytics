from datetime import datetime, timezone
from typing import Iterable, Optional

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


class GetAllVideos:
    def __init__(self, video_repository: VideoRepository) -> None:
        self._video_repository = video_repository

    def get(self) -> list[Video]:
        return self._video_repository.get_all()


class GetVideos:
    """
    Class to retrieve videos from the video repository.
    """

    def __init__(self, video_repository: VideoRepository) -> None:
        self._video_repository = video_repository

    def get(self, date: datetime) -> Optional[Video]:
        """
        This method retrieves a Video object based on the specified date.

        Args:
            date (datetime): The date to get the Video objects at

        Returns:
            The Video that is present at the specified date.
            Returns None if no matching Video object is found.

        """
        videos = self._video_repository.get_by_date(date)
        if videos:
            return videos[0]
        return None

    def get_after(self, date: datetime) -> list[Video]:
        """
        Retrieves all videos after the video present at the specified date.

        Args:
            date (datetime): A date specifying the date for the current video

        Returns:
            Videos that start after the current video determined by date.

        Note:
            If the provided date matches a video, the returned list will include
            videos starting after that video. The returned list is sorted in ascending
            order by start date.
            If no video is present at the specified date, the returned list will be
            empty.
        """
        sorted_videos = self._get_all_videos_sorted()
        if current_video := self.get(date):
            index = sorted_videos.index(current_video)
            return sorted_videos[index + 1 :]
        for index, video in enumerate(sorted_videos):
            if video.start_date and video.start_date > date:
                return sorted_videos[index:]
        return []

    def _get_all_videos_sorted(self) -> list[Video]:
        """
        Sorts and returns a list of all videos in a sorted order based on their start
        dates.

        datetime.min will be assumed if a video has no start date.

        Returns:
            All videos sorted by their start dates.
        """
        all_videos = self._video_repository.get_all()
        return sorted(
            all_videos,
            key=lambda video: (
                video.start_date
                if video.start_date
                else datetime.min.replace(tzinfo=timezone.utc)
            ),
        )

    def get_before(self, date: datetime) -> list[Video]:
        """
        Retrieves all videos before the video present at the specified date.

        Args:
            date: A date specifying the date for the current video

        Returns:
            A videos that start before the current video determined by date.

        Note:
            If the provided date matches a video, the returned list will include
            videos starting before that video. The returned list is sorted in ascending
            order by start date.
            If no video is present at the specified date, the returned list will be
            empty.
        """
        sorted_videos = self._get_all_videos_sorted()
        if current_video := self.get(date):
            index = sorted_videos.index(current_video)
            return sorted_videos[:index]
        if (
            sorted_videos
            and sorted_videos[-1].end_date
            and sorted_videos[-1].end_date < date
        ):
            return sorted_videos
        return []
