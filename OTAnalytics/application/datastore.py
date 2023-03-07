from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from numpy import ndarray
from pydantic import BaseModel, validator

from OTAnalytics.domain.track import Track, TrackRepository


class TrackParser(ABC):
    @abstractmethod
    def parse(self, file: Path) -> list[Track]:
        pass


class VideoReader(ABC):
    @abstractmethod
    def get_frame(self, video: Path, index: int) -> ndarray:
        """Get frame of `video` at `index`.

        Args:
            video (Path): the path to the video file.
            index (int): the index of the frame to get.

        Returns:
            ndarray: the frame.
        """
        pass


class Video(BaseModel, frozen=True, arbitrary_types_allowed=True):
    """Represents a video file.

    Extends from pydantic.BaseModel
    IMPORTANT: Instantiation of this class is only possible by using named parameters.

    Args:
        video_reader (VideoReader): A video reader used to get frames.
        path (Path): the video file path.

    Raises:
        ValueError: if video file path does not exist.
    """

    video_reader: VideoReader
    path: Path

    @validator("path")
    def check_path_exists(cls, path: Path) -> Path:
        if not path.exists():
            raise ValueError("must be an existing path")
        return path

    def get_frame(self, index: int) -> ndarray:
        """Returns the frame of the video at `index`.

        Args:
            index (int): the index of the frame to get.

        Returns:
            ndarray: the frame.
        """
        return self.video_reader.get_frame(self.path, index)


class VideoRepository:
    def __init__(self) -> None:
        self.videos: dict[int, Video] = {}

    def get_video_for(self, track: Track) -> Optional[Video]:
        return None


class Datastore:
    def __init__(self, track_parser: TrackParser) -> None:
        self.track_parser = track_parser
        self.track_repository = TrackRepository()
        self.video_repository = VideoRepository()

    def load_track_file(self, file: Path) -> None:
        tracks = self.track_parser.parse(file)
        self.track_repository.add_all(tracks)
