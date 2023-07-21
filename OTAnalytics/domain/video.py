from abc import ABC, abstractmethod
from dataclasses import dataclass
from os import path
from os.path import normcase, splitdrive
from pathlib import Path
from typing import Iterable, Optional

from OTAnalytics.domain.track import TrackImage

VIDEOS: str = "videos"
PATH: str = "path"


class VideoReader(ABC):
    @abstractmethod
    def get_frame(self, video: Path, index: int) -> TrackImage:
        """Get frame of `video` at `index`.
        Args:
            video (Path): the path to the video file.
            index (int): the index of the frame to get.
        Returns:
            TrackImage: the frame.
        """
        pass


class Video(ABC):
    @abstractmethod
    def get_path(self) -> Path:
        pass

    @abstractmethod
    def get_frame(self, index: int) -> TrackImage:
        pass

    @abstractmethod
    def to_dict(
        self,
        relative_to: Path,
    ) -> dict:
        """Convert the video object to a dictionary containing the path of the video
        relative to the given path.
        Args:
            relative_to (Path): target to build relative paths to
        Returns:
            dict: path of the dictionary relative to the given path
        Throws:
            DifferentDrivesException: if config and videos files are located on
            different drives
        """
        pass


class DifferentDrivesException(Exception):
    pass


@dataclass
class SimpleVideo(Video):
    """Represents a video file.
    Args:
        video_reader (VideoReader): A video reader used to get frames.
        path (Path): the video file path.
    Raises:
        ValueError: if video file path does not exist.
    """

    video_reader: VideoReader
    path: Path

    def __post_init__(self) -> None:
        self.check_path_exists()

    def check_path_exists(self) -> None:
        if not self.path.exists():
            raise ValueError(f"{self.path} must be an existing path")

    def get_path(self) -> Path:
        return self.path

    def get_frame(self, index: int) -> TrackImage:
        """Returns the frame of the video at `index`.
        Args:
            index (int): the index of the frame to get.
        Returns:
            TrackImage: the frame.
        """
        return self.video_reader.get_frame(self.path, index)

    def to_dict(
        self,
        relative_to: Path,
    ) -> dict:
        return {PATH: self.__build_relative_path(relative_to)}

    def __build_relative_path(self, relative_to: Path) -> str:
        self_drive, _ = splitdrive(self.path)
        other_drive, _ = splitdrive(relative_to)
        if normcase(self_drive) != normcase(other_drive):
            raise DifferentDrivesException(
                "Video and config files are stored on different drives. "
                f"Video file is stored on {self_drive}."
                f"Configuration is stored on {other_drive}"
            )
        return path.relpath(self.path, relative_to)


class VideoListObserver(ABC):
    """
    Interface to listen to changes to a list of tracks.
    """

    @abstractmethod
    def notify_videos(self, videos: list[Video]) -> None:
        """
        Notifies that the given videos have been added.
        Args:
            tracks (list[Video]): list of added videos
        """
        pass


class VideoListSubject:
    """
    Helper class to handle and notify observers
    """

    def __init__(self) -> None:
        self.observers: list[VideoListObserver] = []

    def register(self, observer: VideoListObserver) -> None:
        """
        Listen to events.
        Args:
            observer (VideoListObserver): listener to add
        """
        self.observers.append(observer)

    def notify(self, videos: list[Video]) -> None:
        """
        Notifies observers about the list of videos.
        Args:
            videos (list[Video]): list of added videos
        """
        [observer.notify_videos(videos) for observer in self.observers]


class VideoRepository:
    def __init__(self) -> None:
        self._videos: dict[Path, Video] = {}
        self._observers = VideoListSubject()

    def register_videos_observer(self, observer: VideoListObserver) -> None:
        """
        Listen to changes of the repository.
        Args:
            observer (VideoListObserver): listener to be notifed about changes
        """
        self._observers.register(observer)

    def add(self, video: Video) -> None:
        self.__do_add(video)
        self._observers.notify([video])

    def __do_add(self, video: Video) -> None:
        self._videos[video.get_path()] = video

    def add_all(self, videos: Iterable[Video]) -> None:
        for video in videos:
            self.__do_add(video)
        self._observers.notify(list(videos))

    def get_all(self) -> list[Video]:
        return list(self._videos.values())

    def get(self, file: Path) -> Optional[Video]:
        return self._videos.get(file)

    def remove(self, videos: list[Video]) -> None:
        for video in videos:
            del self._videos[video.get_path()]
        self._observers.notify([])

    def clear(self) -> None:
        """
        Clear the repository.
        """
        self._videos.clear()
