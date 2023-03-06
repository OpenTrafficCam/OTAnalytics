from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional, Tuple

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


@dataclass(frozen=True)
class Video:
    path: Path

    def get_image(self) -> None:
        pass


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
