from abc import ABC, abstractmethod

from pandas import DataFrame

from OTAnalytics.domain.track import TRACK_CLASSIFICATION, TRACK_ID, Detection, Track
from OTAnalytics.domain.track_dataset.track_dataset import (
    END_FRAME,
    END_OCCURRENCE,
    END_VIDEO_NAME,
    END_X,
    END_Y,
    START_FRAME,
    START_OCCURRENCE,
    START_VIDEO_NAME,
    START_X,
    START_Y,
    TrackSegmentDataset,
)
from OTAnalytics.plugin_datastore.python_track_store import (
    PythonTrackPoint,
    PythonTrackSegment,
    PythonTrackSegmentDataset,
)
from OTAnalytics.plugin_datastore.track_store import PandasTrackSegmentDataset

PYTHON = "PYTHON"
PANDAS = "PANDAS"
IMPLEMENTATIONS = [PYTHON, PANDAS]


class TrackSegmentDatasetBuilder(ABC):
    @abstractmethod
    def _create_segment_for(
        self, track: Track, start: Detection, end: Detection
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def _build(self) -> TrackSegmentDataset:
        raise NotImplementedError

    @abstractmethod
    def reset(self) -> None:
        raise NotImplementedError

    def add_first_segments(self, tracks: list[Track]) -> None:
        for track in tracks:
            self.add_first_segment(track)

    def add_last_segments(self, tracks: list[Track]) -> None:
        for track in tracks:
            self.add_last_segment(track)

    def add_first_segment(self, track: Track) -> None:
        first_detection = track.first_detection
        second_detection = track.detections[1]
        self._create_segment_for(track, first_detection, second_detection)

    def add_last_segment(self, track: Track) -> None:
        last_detection = track.last_detection
        second_last_detection = track.detections[-2]
        self._create_segment_for(track, second_last_detection, last_detection)

    def build(self) -> TrackSegmentDataset:
        dataset = self._build()
        self.reset()
        return dataset


class PandasTrackSegmentDatasetBuilder(TrackSegmentDatasetBuilder):
    def __init__(self) -> None:
        self._segments: list[dict] = []

    def reset(self) -> None:
        self._segments = []

    def _create_segment_for(
        self, track: Track, start: Detection, end: Detection
    ) -> None:
        self._segments.append(
            {
                TRACK_ID: track.id.id,
                TRACK_CLASSIFICATION: track.classification,
                START_X: start.x,
                START_Y: start.y,
                START_OCCURRENCE: start.occurrence,
                START_FRAME: start.frame,
                START_VIDEO_NAME: start.video_name,
                END_X: end.x,
                END_Y: end.y,
                END_OCCURRENCE: end.occurrence,
                END_FRAME: end.frame,
                END_VIDEO_NAME: end.video_name,
            }
        )

    def _build(self) -> PandasTrackSegmentDataset:
        dataframe = DataFrame(self._segments)
        dataframe.set_index(TRACK_ID, inplace=True)
        return PandasTrackSegmentDataset(dataframe)


class PythonTrackSegmentDatasetBuilder(TrackSegmentDatasetBuilder):
    def __init__(self) -> None:
        self._segments: list[PythonTrackSegment] = []

    def reset(self) -> None:
        self._segments = []

    def _create_segment_for(
        self, track: Track, start: Detection, end: Detection
    ) -> None:
        self._segments.append(
            PythonTrackSegment(
                track_id=track.id.id,
                track_classification=track.classification,
                start=PythonTrackPoint.from_detection(start),
                end=PythonTrackPoint.from_detection(end),
            )
        )

    def _build(self) -> PythonTrackSegmentDataset:
        return PythonTrackSegmentDataset(self._segments)


class TrackSegmentDatasetBuilderProvider:
    def provide(self, implementation: str) -> TrackSegmentDatasetBuilder:
        if implementation == PYTHON:
            return PythonTrackSegmentDatasetBuilder()
        elif implementation == PANDAS:
            return PandasTrackSegmentDatasetBuilder()
        else:
            raise ValueError(f"Unsupported implementation: {implementation}")
