from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional

from OTAnalytics.domain.common import DataclassValidation


@dataclass(frozen=True)
class TrackId:
    id: int


class TrackError(Exception):
    def __init__(self, track_id: TrackId, *args: object) -> None:
        super().__init__(*args)
        self.track_id = track_id


class BuildTrackWithSingleDetectionError(TrackError):
    def __str__(self) -> str:
        return (
            f"Trying to construct track (track_id={self.track_id}) with less than "
            "two detections."
        )


@dataclass(frozen=True)
class Detection(DataclassValidation):
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
        classification (str): class of detection.
        confidence (float): the confidence.
        x (float): the x coordinate component of the bounding box.
        y (float): the y coordinate component of the bounding box.
        w (float): the width component of the bounding box.
        h (float): the height component of the bounding box.
        frame (int): the frame that the detection belongs to.
        occurrence (datetime): the time of the detection's occurence.
        input_file_path (Path): absolute path to otdet that the detection belongs to
        at the time of its creation.
        interpolated_detection (bool): whether this detection is interpolated.
        track_id (int): the track id this detection belongs to.
    """

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
    track_id: TrackId

    def _validate(self) -> None:
        self._validate_confidence_greater_equal_zero()
        self._validate_bbox_values()
        self._validate_frame_id_greater_equal_one()
        self._validate_track_id_greater_equal_one()

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

    def _validate_track_id_greater_equal_one(self) -> None:
        if self.track_id.id < 1:
            raise ValueError("track id must be greater equal 1")


@dataclass(frozen=True)
class Track(DataclassValidation):
    """Represents the the track of an object as seen in the task of object tracking
    (computer vision).


    Args:
        id (int): the track id.
        detections (list[Detection]): the detections belonging to this track.

    Raises:
        ValueError: if detections are not sorted by `occurrence`.
        ValueError: if an empty detections list has been passed.
    """

    id: TrackId
    detections: list[Detection]

    def _validate(self) -> None:
        self._validate_id_greater_zero()
        self._validate_track_has_at_least_two_detections()
        self._validate_detections_sorted_by_occurrence()

    def _validate_id_greater_zero(self) -> None:
        if self.id.id < 1:
            raise ValueError("id must be a number greater than 0")

    def _validate_track_has_at_least_two_detections(self) -> None:
        if len(self.detections) < 2:
            raise BuildTrackWithSingleDetectionError(self.id)

    def _validate_detections_sorted_by_occurrence(self) -> None:
        if self.detections != sorted(self.detections, key=lambda det: det.occurrence):
            raise ValueError("detections must be sorted by occurence")


class TrackRepository:
    def __init__(self, tracks: dict[TrackId, Track] = {}) -> None:
        self.tracks: dict[TrackId, Track] = tracks

    def add(self, track: Track) -> None:
        self.tracks[track.id] = track

    def add_all(self, tracks: Iterable[Track]) -> None:
        for track in tracks:
            self.add(track)

    def get_for(self, id: TrackId) -> Optional[Track]:
        return self.tracks[id]

    def get_all(self) -> Iterable[Track]:
        return self.tracks.values()
