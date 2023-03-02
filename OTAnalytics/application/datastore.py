from abc import ABC, abstractmethod
from pathlib import Path

from domain.track import Track, TrackRepository


class TrackParser(ABC):
    @abstractmethod
    def parse(self, file: Path) -> list[Track]:
        pass


class Datastore:
    track_repository: TrackRepository
    track_parser: TrackParser

    def __init__(self, track_parser: TrackParser) -> None:
        self.track_parser = track_parser
        self.track_repository = TrackRepository()

    def load_track_file(self, file: Path) -> None:
        tracks = self.track_parser.parse(file)
        self.track_repository.add_all(tracks)
