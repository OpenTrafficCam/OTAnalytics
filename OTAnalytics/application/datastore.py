from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional, Tuple

from numpy import ndarray

from OTAnalytics.domain.section import Section, SectionRepository
from OTAnalytics.domain.track import Track, TrackId, TrackRepository


class TrackParser(ABC):
    @abstractmethod
    def parse(self, file: Path) -> list[Track]:
        pass


class SectionParser(ABC):
    @abstractmethod
    def parse(self, file: Path) -> list[Section]:
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


@dataclass(frozen=True)
class Video:
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
            raise ValueError("must be an existing path")

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
        self._videos: dict[TrackId, Video] = {}

    def add(self, track_id: TrackId, video: Video) -> None:
        self._videos[track_id] = video

    def add_all(self, track_ids: Iterable[TrackId], videos: Iterable[Video]) -> None:
        for track_id, video in zip(track_ids, videos):
            self.add(track_id, video)

    def get_video_for(self, track_id: TrackId) -> Optional[Video]:
        return self._videos.get(track_id)


class VideoParser(ABC):
    @abstractmethod
    def parse(self, file: Path) -> Tuple[list[TrackId], list[Video]]:
        pass


class Datastore:
    def __init__(
        self,
        track_parser: TrackParser,
        section_parser: SectionParser,
        video_parser: VideoParser,
    ) -> None:
        self._track_parser = track_parser
        self._section_parser = section_parser
        self._video_parser = video_parser
        self._track_repository = TrackRepository()
        self._section_repository = SectionRepository()
        self._video_repository = VideoRepository()

    def load_track_file(self, file: Path) -> None:
        tracks = self._track_parser.parse(file)
        self._track_repository.add_all(tracks)
        track_ids, videos = self._video_parser.parse(file)
        self._video_repository.add_all(track_ids, videos)

    def load_section_file(self, file: Path) -> None:
        sections = self._section_parser.parse(file)
        self._section_repository.add_all(sections)

    def add_section(self, section: Section) -> None:
        self._section_repository.add(section)
