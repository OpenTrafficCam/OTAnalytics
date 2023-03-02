from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from domain.track import Track, TrackRepository


class TrackParser(ABC):
    @abstractmethod
    def parse(self, file: Path) -> list[Track]:
        pass


class Video:
    path: Path

    def get_image(self) -> None:
        pass


class VideoRepository:
    videos: dict[int, Video]

    def get_video_for(self, track: Track) -> Optional[Video]:
        return None


class Datastore:
    track_repository: TrackRepository
    track_parser: TrackParser
    video_repository: VideoRepository

    def __init__(self, track_parser: TrackParser) -> None:
        self.track_parser = track_parser
        self.track_repository = TrackRepository()

    def load_track_file(self, file: Path) -> None:
        tracks = self.track_parser.parse(file)
        self.track_repository.add_all(tracks)
