from dataclasses import dataclass
from datetime import datetime
from math import ceil
from typing import Iterable, Optional, Sequence

from more_itertools import batched

from OTAnalytics.application.logger import logger
from OTAnalytics.domain.common import DataclassValidation
from OTAnalytics.domain.track import (
    Detection,
    Track,
    TrackClassificationCalculator,
    TrackDataset,
    TrackHasNoDetectionError,
    TrackId,
)


@dataclass(frozen=True)
class PythonDetection(Detection, DataclassValidation):
    """Represents a detection belonging to a `Track`.

    The detection uses the xywh bounding box format.


    Raises:
        ValueError: confidence not in [0,1]
        ValueError: x < 0
        ValueError: y < 0
        ValueError: w < 0
        ValueError: h < 0
        ValueError: frame < 0
        ValueError: track_id < 0


    Args:
        _classification (str): class of detection.
        _confidence (float): the confidence.
        _x (float): the x coordinate component of the bounding box.
        _y (float): the y coordinate component of the bounding box.
        _w (float): the width component of the bounding box.
        _h (float): the height component of the bounding box.
        _frame (int): the frame that the detection belongs to.
        _occurrence (datetime): the time of the detection's occurrence.
        _interpolated_detection (bool): whether this detection is interpolated.
        _track_id (TrackId): the track id this detection belongs to.
        _video_name (str): name of video that this detection belongs.
    """

    _classification: str
    _confidence: float
    _x: float
    _y: float
    _w: float
    _h: float
    _frame: int
    _occurrence: datetime
    _interpolated_detection: bool
    _track_id: TrackId
    _video_name: str

    @property
    def classification(self) -> str:
        return self._classification

    @property
    def confidence(self) -> float:
        return self._confidence

    @property
    def x(self) -> float:
        return self._x

    @property
    def y(self) -> float:
        return self._y

    @property
    def w(self) -> float:
        return self._w

    @property
    def h(self) -> float:
        return self._h

    @property
    def frame(self) -> int:
        return self._frame

    @property
    def occurrence(self) -> datetime:
        return self._occurrence

    @property
    def interpolated_detection(self) -> bool:
        return self._interpolated_detection

    @property
    def track_id(self) -> TrackId:
        return self._track_id

    @property
    def video_name(self) -> str:
        return self._video_name

    def _validate(self) -> None:
        self._validate_confidence_greater_equal_zero()
        self._validate_bbox_values()
        self._validate_frame_id_greater_equal_one()

    def _validate_confidence_greater_equal_zero(self) -> None:
        if self.confidence < 0 or self.confidence > 1:
            raise ValueError("confidence must be in range [0,1]")

    def _validate_bbox_values(self) -> None:
        if self.x < 0:
            raise ValueError("x must be greater equal 0")
        if self.y < 0:
            raise ValueError("y must be greater equal 0")
        if self.w < 0:
            raise ValueError("w must be greater equal 0")
        if self.h < 0:
            raise ValueError("h must be greater equal 0")

    def _validate_frame_id_greater_equal_one(self) -> None:
        if self.frame < 1:
            raise ValueError("frame number must be greater equal 1")


@dataclass(frozen=True)
class PythonTrack(Track, DataclassValidation):
    """Represents the track of an object as seen in the task of object tracking
    (computer vision).

    Args:
        _id (TrackId): the track id.
        _classification: the max classification of this track.
        _detections (list[Detection]): the detections belonging to this track.

    Raises:
        ValueError: if detections are not sorted by `occurrence`.
        ValueError: if an empty detections list has been passed.
    """

    _id: TrackId
    _classification: str
    _detections: list[Detection]

    @property
    def id(self) -> TrackId:
        return self._id

    @property
    def classification(self) -> str:
        return self._classification

    @property
    def detections(self) -> list[Detection]:
        return self._detections

    def _validate(self) -> None:
        self._validate_track_has_detections()
        self._validate_detections_sorted_by_occurrence()

    def _validate_track_has_detections(self) -> None:
        if not self._detections:
            raise TrackHasNoDetectionError(
                self.id,
                (
                    f"Trying to construct track (track_id={self.id.id})"
                    " with no detections."
                ),
            )

    def _validate_detections_sorted_by_occurrence(self) -> None:
        if self._detections != sorted(self._detections, key=lambda det: det.occurrence):
            raise ValueError("detections must be sorted by occurrence")

    @property
    def first_detection(self) -> Detection:
        """Get first detection of track.

        Returns:
            Detection: the first detection.
        """
        return self._detections[0]

    @property
    def last_detection(self) -> Detection:
        """Get last detection of track.

        Returns:
            Detection: the last detection.
        """
        return self._detections[-1]


class ByMaxConfidence(TrackClassificationCalculator):
    """Determine a track's classification by its detections max confidence."""

    def calculate(self, detections: list[Detection]) -> str:
        classifications: dict[str, float] = {}
        for detection in detections:
            if classifications.get(detection.classification):
                classifications[detection.classification] += detection.confidence
            else:
                classifications[detection.classification] = detection.confidence

        return max(classifications, key=lambda x: classifications[x])


@dataclass
class PythonTrackDataset(TrackDataset):
    """Pure Python implementation of a TrackDataset."""

    def __init__(
        self,
        values: Optional[dict[TrackId, Track]] = None,
        calculator: TrackClassificationCalculator = ByMaxConfidence(),
    ) -> None:
        if values is None:
            values = {}
        self._tracks = values
        self._calculator = calculator

    @staticmethod
    def from_list(
        tracks: list[Track],
        calculator: TrackClassificationCalculator = ByMaxConfidence(),
    ) -> TrackDataset:
        return PythonTrackDataset({track.id: track for track in tracks}, calculator)

    def add_all(self, other: Iterable[Track]) -> "TrackDataset":
        if isinstance(other, PythonTrackDataset):
            return self.__merge(other._tracks)
        new_tracks = {track.id: track for track in other}
        return self.__merge(new_tracks)

    def __merge(self, other: dict[TrackId, Track]) -> TrackDataset:
        merged_tracks: dict[TrackId, Track] = {}
        for track_id, other_track in other.items():
            existing_detections = self._get_existing_detections(track_id)
            all_detections = existing_detections + other_track.detections
            sort_dets_by_occurrence = sorted(
                all_detections, key=lambda det: det.occurrence
            )
            classification = self._calculator.calculate(all_detections)
            try:
                current_track = PythonTrack(
                    _id=track_id,
                    _classification=classification,
                    _detections=sort_dets_by_occurrence,
                )
                merged_tracks[current_track.id] = current_track
            except TrackHasNoDetectionError as build_error:
                logger().exception(build_error, exc_info=True)
        merged = self._tracks | merged_tracks
        return PythonTrackDataset(merged)

    def _get_existing_detections(self, track_id: TrackId) -> list[Detection]:
        """
        Returns the detections of an already existing track with the same id or
        an empty list

        Args:
            track_id (TrackId): track id to search for

        Returns:
            list[Detection]: detections of the already existing track or an empty list
        """
        if existing_track := self._tracks.get(track_id):
            return existing_track.detections
        return []

    def get_all_ids(self) -> Iterable[TrackId]:
        return self._tracks.keys()

    def get_for(self, id: TrackId) -> Optional[Track]:
        return self._tracks.get(id)

    def remove(self, track_id: TrackId) -> TrackDataset:
        new_tracks = self._tracks.copy()
        del new_tracks[track_id]
        return PythonTrackDataset(new_tracks)

    def clear(self) -> TrackDataset:
        return PythonTrackDataset()

    def as_list(self) -> list[Track]:
        return list(self._tracks.values())

    def split(self, batches: int) -> Sequence["TrackDataset"]:
        dataset_size = len(self._tracks)
        batch_size = ceil(dataset_size / batches)

        return [
            PythonTrackDataset(dict(batch), self._calculator)
            for batch in batched(self._tracks.items(), batch_size)
        ]

    def __len__(self) -> int:
        return len(self._tracks)

    def filter_by_min_detection_length(self, length: int) -> "TrackDataset":
        filtered_tracks = {
            _id: track
            for _id, track in self._tracks.items()
            if len(track.detections) >= length
        }
        return PythonTrackDataset(filtered_tracks, self._calculator)
