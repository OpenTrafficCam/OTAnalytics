from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional


@dataclass(frozen=True)
class Detection:
    classification: str
    confidence: float
    x: float
    y: float
    w: float
    h: float
    frame: int
    occurrence: datetime
    input_file_path: Path
    interpolated_detection: bool
    track_id: int


@dataclass(frozen=True)
class Track:
    id: int
    detections: list[Detection]


class TrackRepository:
    def __init__(self) -> None:
        self.tracks: dict[int, Track] = {}

    def add(self, track: Track) -> None:
        self.tracks[track.id] = track

    def add_all(self, tracks: Iterable[Track]) -> None:
        for track in tracks:
            self.add(track)

    def get_for(self, id: int) -> Optional[Track]:
        return None

    def get_all(self) -> Iterable[Track]:
        return self.tracks.values()
