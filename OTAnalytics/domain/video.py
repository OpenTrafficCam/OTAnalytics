from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from math import floor
from pathlib import Path
from typing import Iterable, Optional

from OTAnalytics.domain.files import build_relative_path
from OTAnalytics.domain.track import TrackImage

VIDEOS: str = "videos"
PATH: str = "path"


class InvalidVideoError(Exception):
    pass


class FrameDoesNotExistError(Exception):
    pass


class VideoReader(ABC):
    @abstractmethod
    def get_fps(self, video: Path) -> float:
        raise NotImplementedError

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

    @abstractmethod
    def get_frame_number_for(self, video_path: Path, date: timedelta) -> int:
        raise NotImplementedError


class Video(ABC):
    @property
    @abstractmethod
    def start_date(self) -> Optional[datetime]:
        raise NotImplementedError

    @property
    @abstractmethod
    def end_date(self) -> Optional[datetime]:
        raise NotImplementedError

    @property
    @abstractmethod
    def fps(self) -> float:
        raise NotImplementedError

    @abstractmethod
    def get_path(self) -> Path:
        pass

    @property
    def name(self) -> str:
        return self.get_path().name

    @abstractmethod
    def get_frame(self, index: int) -> TrackImage:
        pass

    @abstractmethod
    def get_frame_number_for(self, date: datetime) -> int:
        raise NotImplementedError

    @abstractmethod
    def contains(self, date: datetime) -> bool:
        raise NotImplementedError

    @abstractmethod
    def to_dict(
        self,
        relative_to: Path,
    ) -> dict:
        """Convert the video object to a dictionary containing the path of the video
        relative to the given path.

        Args:
            relative_to (Path): target to build relative paths to

        Raises:
            DifferentDrivesException: if config and videos files are located on
            different drives

        Returns:
            dict: path of the dictionary relative to the given path

        """
        pass

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Video):
            return NotImplemented
        return self.get_path() == other.get_path()

    def __hash__(self) -> int:
        return hash(self.get_path())


@dataclass(frozen=True)
class VideoMetadata:
    path: str
    recorded_start_date: datetime
    expected_duration: Optional[timedelta]
    recorded_fps: float
    actual_fps: Optional[float]
    number_of_frames: int

    @property
    def start(self) -> datetime:
        return self.recorded_start_date

    @property
    def end(self) -> datetime:
        return self.start + self.duration

    @property
    def duration(self) -> timedelta:
        if self.expected_duration:
            return self.expected_duration
        return timedelta(seconds=self.number_of_frames / self.recorded_fps)

    @property
    def fps(self) -> float:
        if self.actual_fps:
            return self.actual_fps
        return self.recorded_fps

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "recorded_start_date": self.recorded_start_date.timestamp(),
            "expected_duration": (
                self.expected_duration.total_seconds()
                if self.expected_duration
                else None
            ),
            "recorded_fps": self.recorded_fps,
            "actual_fps": self.actual_fps,
            "number_of_frames": self.number_of_frames,
        }

    def contains(self, date: datetime) -> bool:
        return self.start <= date < self.end


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
    metadata: Optional[VideoMetadata]

    @property
    def start_date(self) -> Optional[datetime]:
        if self.metadata:
            return self.metadata.recorded_start_date
        return None

    @property
    def end_date(self) -> Optional[datetime]:
        if self.metadata:
            return self.metadata.end
        return None

    @property
    def fps(self) -> float:
        return (
            self.metadata.fps if self.metadata else self.video_reader.get_fps(self.path)
        )

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

    def get_frame_number_for(self, date: datetime) -> int:
        if not self.start_date:
            return 0
        time_in_video = date - self.start_date
        if time_in_video < timedelta(0):
            return 0

        return floor(self.fps * time_in_video.total_seconds())

    def to_dict(
        self,
        relative_to: Path,
    ) -> dict:
        return {
            PATH: build_relative_path(
                self.path,
                relative_to,
                lambda actual, other: (
                    "Video and config files are stored on different drives. "
                    f"Video file is stored on {actual}."
                    f"Configuration is stored on {other}"
                ),
            )
        }

    def contains(self, date: datetime) -> bool:
        if self.metadata:
            return self.metadata.contains(date)
        return False


class VideoListObserver(ABC):
    """
    Interface to listen to changes to a list of tracks.
    """

    @abstractmethod
    def notify_videos(self, videos: list[Video]) -> None:
        """
        Notifies that the given videos have been added.

        Args:
            videos (list[Video]): list of added videos
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
            observer (VideoListObserver): listener to be notified about changes.
        """
        self._observers.register(observer)

    def add(self, video: Video) -> None:
        self.__do_add(video)
        self.__sort()
        self._observers.notify([video])

    def __sort(self) -> None:
        """
        Sort the videos in the repository according to their path.
        """
        self._videos = dict(sorted(self._videos.items()))

    def __do_add(self, video: Video) -> None:
        self._videos[video.get_path()] = video

    def add_all(self, videos: Iterable[Video]) -> None:
        for video in videos:
            self.__do_add(video)
        self.__sort()
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
        self._observers.notify([])

    def get_by_date(self, date: datetime) -> list[Video]:
        return [video for video in self._videos.values() if video.contains(date)]
