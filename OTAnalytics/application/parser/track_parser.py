from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from OTAnalytics.domain.georeference import GeoreferenceMetadata
from OTAnalytics.domain.track_dataset.track_dataset import TrackDataset
from OTAnalytics.domain.video import VideoMetadata


@dataclass(frozen=True)
class DetectionMetadata:
    detection_classes: frozenset[str]


@dataclass(frozen=True)
class TrackParseResult:
    tracks: TrackDataset
    detection_metadata: DetectionMetadata
    video_metadata: VideoMetadata
    georeference_metadata: GeoreferenceMetadata | None = None


@dataclass(frozen=True)
class TracksParseResult:
    tracks: TrackDataset
    detections_metadata: list[DetectionMetadata]
    videos_metadata: list[VideoMetadata]
    georeference_metadata: GeoreferenceMetadata | None = None


def combine_track_datasets(results: list[TrackParseResult]) -> TrackDataset:
    if not results:
        raise ValueError("No results to combine")
    tracks = results[0].tracks
    for result in results[1:]:
        tracks.add_all(result.tracks)
    return tracks


class TrackParser(ABC):
    def parse_files(self, files: list[Path]) -> TracksParseResult:
        if not files:
            raise ValueError("No files to parse")
        results = [self.parse(file) for file in files]
        tracks = combine_track_datasets(results)
        detections_metadata = [result.detection_metadata for result in results]
        videos_metadata = [result.video_metadata for result in results]
        georeference_metadata = next(
            (
                r.georeference_metadata
                for r in results
                if r.georeference_metadata is not None
            ),
            None,
        )
        return TracksParseResult(
            tracks, detections_metadata, videos_metadata, georeference_metadata
        )

    @abstractmethod
    def parse(self, file: Path) -> TrackParseResult:
        raise NotImplementedError
