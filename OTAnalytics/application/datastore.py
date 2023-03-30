from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional, Tuple

from OTAnalytics.domain.event import Event, EventRepository
from OTAnalytics.domain.section import Section, SectionListObserver, SectionRepository
from OTAnalytics.domain.track import (
    Track,
    TrackClassificationCalculator,
    TrackId,
    TrackImage,
    TrackListObserver,
    TrackRepository,
)


class TrackParser(ABC):
    def __init__(
        self, track_classification_calculator: TrackClassificationCalculator
    ) -> None:
        self._track_classification_calculator = track_classification_calculator

    @abstractmethod
    def parse(self, file: Path) -> list[Track]:
        pass


class SectionParser(ABC):
    @abstractmethod
    def parse(self, file: Path) -> list[Section]:
        pass

    @abstractmethod
    def serialize(self, sections: Iterable[Section], file: Path) -> None:
        pass


class EventListParser(ABC):
    @abstractmethod
    def serialize(self, events: Iterable[Event], file: Path) -> None:
        pass


class VideoReader(ABC):
    @abstractmethod
    def get_frame(self, video: Path, index: int) -> TrackImage:
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

    def get_frame(self, index: int) -> TrackImage:
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
    def parse(
        self, file: Path, track_ids: list[TrackId]
    ) -> Tuple[list[TrackId], list[Video]]:
        pass


class Datastore:
    def __init__(
        self,
        track_parser: TrackParser,
        section_parser: SectionParser,
        event_list_parser: EventListParser,
        video_parser: VideoParser,
    ) -> None:
        self._track_parser = track_parser
        self._section_parser = section_parser
        self._event_list_parser = event_list_parser
        self._video_parser = video_parser
        self._track_repository = TrackRepository()
        self._section_repository = SectionRepository()
        self._event_repository = EventRepository()
        self._video_repository = VideoRepository()

    def register_tracks_observer(self, observer: TrackListObserver) -> None:
        self._track_repository.register_tracks_observer(observer)

    def register_sections_observer(self, observer: SectionListObserver) -> None:
        self._section_repository.register_sections_observer(observer)

    def load_track_file(self, file: Path) -> None:
        tracks = self._track_parser.parse(file)
        track_ids = [track.id for track in tracks]
        track_ids, videos = self._video_parser.parse(file, track_ids)
        self._video_repository.add_all(track_ids, videos)
        self._track_repository.add_all(tracks)

    def load_section_file(self, file: Path) -> None:
        sections = self._section_parser.parse(file)
        self._section_repository.add_all(sections)

    def save_section_file(self, file: Path) -> None:
        self._section_parser.serialize(
            self._section_repository.get_all(),
            file=file,
        )

    def save_event_list_file(self, file: Path) -> None:
        self._event_list_parser.serialize(
            self._event_repository.get_all(),
            file=file,
        )

    def add_section(self, section: Section) -> None:
        self._section_repository.add(section)

    def get_image_of_track(self, track_id: TrackId) -> Optional[TrackImage]:
        if video := self._video_repository.get_video_for(track_id):
            return video.get_frame(0)
        return None
