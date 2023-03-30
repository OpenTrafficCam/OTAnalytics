from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Optional

from OTAnalytics.domain.common import DataclassValidation


@dataclass(frozen=True)
class TrackId(DataclassValidation):
    id: int

    def _validate(self) -> None:
        if self.id < 1:
            raise ValueError("track id must be greater equal 1")


class TrackListObserver(ABC):
    @abstractmethod
    def notify_tracks(self, tracks: list[TrackId]) -> None:
        pass


class TrackObserver(ABC):
    @abstractmethod
    def notify_track(self, track_id: Optional[TrackId]) -> None:
        pass


class TrackSubject:
    def __init__(self) -> None:
        self.observers: set[TrackObserver] = set()

    def register(self, observer: TrackObserver) -> None:
        self.observers.add(observer)

    def notify(self, track_id: Optional[TrackId]) -> None:
        [observer.notify_track(track_id) for observer in self.observers]


class TrackListSubject:
    def __init__(self) -> None:
        self.observers: set[TrackListObserver] = set()

    def register(self, observer: TrackListObserver) -> None:
        self.observers.add(observer)

    def notify(self, tracks: list[TrackId]) -> None:
        [observer.notify_tracks(tracks) for observer in self.observers]


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
        track_id (TrackId): the track id this detection belongs to.
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
class Track(DataclassValidation):
    """Represents the the track of an object as seen in the task of object tracking
    (computer vision).


    Args:
        id (TrackId): the track id.
        detections (list[Detection]): the detections belonging to this track.

    Raises:
        ValueError: if detections are not sorted by `occurrence`.
        ValueError: if an empty detections list has been passed.
    """

    id: TrackId
    classification: str
    detections: list[Detection]

    def _validate(self) -> None:
        self._validate_track_has_at_least_two_detections()
        self._validate_detections_sorted_by_occurrence()

    def _validate_track_has_at_least_two_detections(self) -> None:
        if len(self.detections) < 2:
            raise BuildTrackWithSingleDetectionError(self.id)

    def _validate_detections_sorted_by_occurrence(self) -> None:
        if self.detections != sorted(self.detections, key=lambda det: det.occurrence):
            raise ValueError("detections must be sorted by occurence")


@dataclass(frozen=True)
class TrackImage:
    @abstractmethod
    def as_array(self) -> Any:
        pass


class TrackClassificationCalculator(ABC):
    """
    Defines interface for calculation strategy to determine a track's classification.
    """

    @abstractmethod
    def calculate(self, detections: list[Detection]) -> str:
        """Determine a track's classification.

        Args:
            detections (Detection): the track's detections needed to determine the
                classification

        Returns:
            str: the track's class
        """
        pass


class CalculateTrackClassificationByMaxConfidence(TrackClassificationCalculator):
    """Determine a track's classification by its detections max confidence."""

    def calculate(self, detections: list[Detection]) -> str:
        classifications: dict[str, float] = {}
        for detection in detections:
            if classifications.get(detection.classification):
                classifications[detection.classification] += detection.confidence
            classifications[detection.classification] = detection.confidence

        return max(classifications, key=lambda x: classifications[x])


class TrackRepository:
    def __init__(self, tracks: dict[TrackId, Track] = {}) -> None:
        self.tracks: dict[TrackId, Track] = tracks
        self.observers = TrackListSubject()

    def register_tracks_observer(self, observer: TrackListObserver) -> None:
        """
        Listen to changes of the repository.

        Args:
            observer (TrackListObserver): listener to be notifed about changes
        """
        self.observers.register(observer)

    def add(self, track: Track) -> None:
        """
        Add a single track to the repository and notify the observers.

        Args:
            track (Track): track to be added
        """
        self.__add(track)
        self.observers.notify([track.id])

    def __add(self, track: Track) -> None:
        self.tracks[track.id] = track

    def add_all(self, tracks: Iterable[Track]) -> None:
        """
        Add multiple tracks to the repository and notify only once about it.

        Args:
            tracks (Iterable[Track]): tracks to be added
        """
        for track in tracks:
            self.__add(track)
        self.observers.notify([track.id for track in tracks])

    def get_for(self, id: TrackId) -> Optional[Track]:
        """
        Retrieve a track for the given id.

        Args:
            id (TrackId): id to search for

        Returns:
            Optional[Track]: track if it exists
        """
        return self.tracks[id]

    def get_all(self) -> Iterable[Track]:
        """
        Retrieve all tracks.

        Returns:
            Iterable[Track]: all tracks within the repository
        """
        return self.tracks.values()
