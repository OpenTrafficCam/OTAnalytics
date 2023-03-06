from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from OTAnalytics.domain.track import Track, TrackRepository


class TrackParser(ABC):
    @abstractmethod
    def parse(self, file: Path) -> list[Track]:
        pass


@dataclass(frozen=True)
class Video:
    path: Path

    def get_image(self) -> None:
        pass


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
