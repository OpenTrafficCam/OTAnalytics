from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional

from PIL import Image

from OTAnalytics.domain.common import DataclassValidation
from OTAnalytics.domain.observer import Subject

CLASSIFICATION: str = "classification"
CONFIDENCE: str = "confidence"
X: str = "x"
Y: str = "y"
W: str = "w"
H: str = "h"
FRAME: str = "frame"
OCCURRENCE: str = "occurrence"
INPUT_FILE_PATH: str = "input_file_path"
INTERPOLATED_DETECTION: str = "interpolated_detection"
TRACK_ID: str = "track_id"

VALID_TRACK_SIZE: int = 5


@dataclass(frozen=True)
class TrackId(DataclassValidation):
    id: int

    def _validate(self) -> None:
        if self.id < 1:
            raise ValueError("track id must be greater equal 1")


class TrackListObserver(ABC):
    """
    Interface to listen to changes to a list of tracks.
    """

    @abstractmethod
    def notify_tracks(self, tracks: list[TrackId]) -> None:
        """
        Notifies that the given tracks have been added.

        Args:
            tracks (list[TrackId]): list of added tracks
        """
        pass


class TrackObserver(ABC):
    """
    Interface to listen to changes of a single track.
    """

    @abstractmethod
    def notify_track(self, track_id: Optional[TrackId]) -> None:
        """
        Notifies that the track of the given id has changed.

        Args:
            track_id (Optional[TrackId]): id of the changed track
        """
        pass


class TrackSubject:
    """
    Helper class to handle and notify observers
    """

    def __init__(self) -> None:
        self.observers: set[TrackObserver] = set()

    def register(self, observer: TrackObserver) -> None:
        """
        Listen to events.

        Args:
            observer (TrackObserver): listener to add
        """
        self.observers.add(observer)

    def notify(self, track_id: Optional[TrackId]) -> None:
        """
        Notifies observers about the track id.

        Args:
            track_id (Optional[TrackId]): id of the changed track
        """
        [observer.notify_track(track_id) for observer in self.observers]


class TrackError(Exception):
    def __init__(self, track_id: TrackId, *args: object) -> None:
        super().__init__(*args)
        self.track_id = track_id


class BuildTrackWithLessThanNDetectionsError(TrackError):
    def __str__(self) -> str:
        return (
            f"Trying to construct track (track_id={self.track_id}) with less than "
            f"{VALID_TRACK_SIZE} detections."
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

    def to_dict(self) -> dict:
        return {
            CLASSIFICATION: self.classification,
            CONFIDENCE: self.confidence,
            X: self.x,
            Y: self.y,
            W: self.w,
            H: self.h,
            FRAME: self.frame,
            OCCURRENCE: self.occurrence,
            INPUT_FILE_PATH: self.input_file_path,
            INTERPOLATED_DETECTION: self.interpolated_detection,
            TRACK_ID: self.track_id.id,
        }


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
        self._validate_track_has_at_least_five_detections()
        self._validate_detections_sorted_by_occurrence()

    def _validate_track_has_at_least_five_detections(self) -> None:
        if len(self.detections) < 5:
            raise BuildTrackWithLessThanNDetectionsError(self.id)

    def _validate_detections_sorted_by_occurrence(self) -> None:
        if self.detections != sorted(self.detections, key=lambda det: det.occurrence):
            raise ValueError("detections must be sorted by occurence")


@dataclass(frozen=True)
class TrackImage:
    """
    Represents an image with tracks. This might be an empty image or one with different
    types of track visualisation.
    """

    def add(self, other: "TrackImage") -> "TrackImage":
        """
        Add the other image on top of this image. The composition of the two images
        takes transparency into account.

        Args:
            other (TrackImage): other image to stack on top of this image

        Returns:
            TrackImage: combined image of this and the other image
        """
        self_image = self.as_image().convert(mode="RGBA")
        other_image = other.as_image().convert(mode="RGBA")
        return PilImage(Image.alpha_composite(self_image, other_image))

    @abstractmethod
    def as_image(self) -> Image.Image:
        """
        Convert image into a base python image.

        Returns:
            Image.Image: image as pilow image
        """
        pass

    @abstractmethod
    def width(self) -> int:
        """
        Width of the image.

        Returns:
            int: width of the image
        """
        pass

    @abstractmethod
    def height(self) -> int:
        """
        Height of the image.

        Returns:
            int: height of the image
        """
        pass


@dataclass(frozen=True)
class PilImage(TrackImage):
    """
    Concrete implementation using pilow as image format.
    """

    _image: Image.Image

    def as_image(self) -> Image.Image:
        return self._image

    def width(self) -> int:
        return self._image.width

    def height(self) -> int:
        return self._image.height


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
            else:
                classifications[detection.classification] = detection.confidence

        return max(classifications, key=lambda x: classifications[x])


class TrackRepository:
    def __init__(self) -> None:
        self._tracks: dict[TrackId, Track] = {}
        self.observers = Subject[list[TrackId]]()

    def register_tracks_observer(self, observer: TrackListObserver) -> None:
        """
        Listen to changes of the repository.

        Args:
            observer (TrackListObserver): listener to be notifed about changes
        """
        self.observers.register(observer.notify_tracks)

    def add(self, track: Track) -> None:
        """
        Add a single track to the repository and notify the observers.

        Args:
            track (Track): track to be added
        """
        self.__add(track)
        self.observers.notify([track.id])

    def __add(self, track: Track) -> None:
        """Internal method to add a track without notifying observers.

        Args:
            track (Track): the track to be added
        """
        self._tracks[track.id] = track

    def add_all(self, tracks: list[Track]) -> None:
        """
        Add multiple tracks to the repository and notify only once about it.

        Args:
            tracks (Iterable[Track]): tracks to be added
        """
        if tracks:
            self.__add_all(tracks)

    def __add_all(self, tracks: list[Track]) -> None:
        """Internal method to add all tracks to the repository and notify only once
        about it.

        Args:
            tracks (list[Track]): tracks to be added
        """
        for track in tracks:
            self.__add(track)
        self.observers.notify([track.id for track in tracks])

    def delete_all(self) -> None:
        """Delete all tracks."""
        self._tracks = {}

    def get_for(self, id: TrackId) -> Optional[Track]:
        """
        Retrieve a track for the given id.

        Args:
            id (TrackId): id to search for

        Returns:
            Optional[Track]: track if it exists
        """
        return self._tracks.get(id)

    def get_all(self) -> list[Track]:
        """
        Retrieve all tracks.

        Returns:
            list[Track]: all tracks within the repository
        """
        return list(self._tracks.values())

    def clear(self) -> None:
        """
        Clear the repository and inform the observers about the empty repository.
        """
        self._tracks.clear()
        self.observers.notify([])


class TrackIdProvider(ABC):
    """Interface to provide track ids."""

    @abstractmethod
    def get_ids(self) -> Iterable[TrackId]:
        """Provide track ids.

        Returns:
            Iterable[TrackId]: the track ids.
        """
        pass
