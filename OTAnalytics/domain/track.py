from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional

from PIL import Image

from OTAnalytics.domain.common import DataclassValidation
from OTAnalytics.domain.observer import Subject

CLASSIFICATION: str = "classification"
TRACK_CLASSIFICATION: str = "track_classification"
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


class Detection(ABC):
    @property
    @abstractmethod
    def classification(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def confidence(self) -> float:
        raise NotImplementedError

    @property
    @abstractmethod
    def x(self) -> float:
        raise NotImplementedError

    @property
    @abstractmethod
    def y(self) -> float:
        raise NotImplementedError

    @property
    @abstractmethod
    def w(self) -> float:
        raise NotImplementedError

    @property
    @abstractmethod
    def h(self) -> float:
        raise NotImplementedError

    @property
    @abstractmethod
    def frame(self) -> int:
        raise NotImplementedError

    @property
    @abstractmethod
    def occurrence(self) -> datetime:
        raise NotImplementedError

    @property
    @abstractmethod
    def input_file_path(self) -> Path:
        raise NotImplementedError

    @property
    @abstractmethod
    def interpolated_detection(self) -> bool:
        raise NotImplementedError

    @property
    @abstractmethod
    def track_id(self) -> TrackId:
        raise NotImplementedError

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

    _classification: str
    _confidence: float
    _x: float
    _y: float
    _w: float
    _h: float
    _frame: int
    _occurrence: datetime
    _input_file_path: Path
    _interpolated_detection: bool
    _track_id: TrackId

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
    def input_file_path(self) -> Path:
        return self._input_file_path

    @property
    def interpolated_detection(self) -> bool:
        return self._interpolated_detection

    @property
    def track_id(self) -> TrackId:
        return self._track_id

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


class Track(ABC):
    @property
    @abstractmethod
    def id(self) -> TrackId:
        raise NotImplementedError

    @property
    @abstractmethod
    def classification(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def detections(self) -> list[Detection]:
        raise NotImplementedError


@dataclass(frozen=True)
class PythonTrack(Track, DataclassValidation):
    """Represents the track of an object as seen in the task of object tracking
    (computer vision).


    Args:
        id (TrackId): the track id.
        detections (list[Detection]): the detections belonging to this track.

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
        self._validate_track_has_at_least_five_detections()
        self._validate_detections_sorted_by_occurrence()

    def _validate_track_has_at_least_five_detections(self) -> None:
        if len(self._detections) < 5:
            raise BuildTrackWithLessThanNDetectionsError(self._id)

    def _validate_detections_sorted_by_occurrence(self) -> None:
        if self._detections != sorted(self._detections, key=lambda det: det.occurrence):
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
        raise NotImplementedError


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


class TrackDataset(ABC):
    @abstractmethod
    def add_all(self, other: "TrackDataset") -> "TrackDataset":
        raise NotImplementedError

    @abstractmethod
    def get_for(self, id: TrackId) -> Optional[Track]:
        """
        Retrieve a track for the given id.

        Args:
            id (TrackId): id to search for

        Returns:
            Optional[Track]: track if it exists
        """
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> "TrackDataset":
        """
        Return an empty version of the current TrackDataset.
        """
        raise NotImplementedError

    @abstractmethod
    def as_list(self) -> list[Track]:
        raise NotImplementedError


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

    def add_all(self, other: "TrackDataset") -> "TrackDataset":
        if isinstance(other, PythonTrackDataset):
            return self.__merge(other._tracks)
        new_tracks = {track.id: track for track in other.as_list()}
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
            except BuildTrackWithLessThanNDetectionsError as build_error:
                # TODO: log error
                # Skip tracks with less than 2 detections
                print(build_error)
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

    def get_for(self, id: TrackId) -> Optional[Track]:
        return self._tracks.get(id)

    def clear(self) -> TrackDataset:
        return PythonTrackDataset()

    def as_list(self) -> list[Track]:
        return list(self._tracks.values())


class TrackRepository:
    def __init__(self, dataset: TrackDataset = PythonTrackDataset()) -> None:
        self._dataset = dataset
        self.observers = Subject[list[TrackId]]()

    def register_tracks_observer(self, observer: TrackListObserver) -> None:
        """
        Listen to changes of the repository.

        Args:
            observer (TrackListObserver): listener to be notifed about changes
        """
        self.observers.register(observer.notify_tracks)

    def add_all(self, tracks: TrackDataset) -> None:
        """
        Add multiple tracks to the repository and notify only once about it.

        Args:
            tracks (Iterable[Track]): tracks to be added
        """
        self._dataset = self._dataset.add_all(tracks)
        new_tracks = [track.id for track in tracks.as_list()]
        if new_tracks:
            self.observers.notify(new_tracks)

    def delete_all(self) -> None:
        """Delete all tracks."""
        self._dataset = PythonTrackDataset()

    def get_for(self, id: TrackId) -> Optional[Track]:
        """
        Retrieve a track for the given id.

        Args:
            id (TrackId): id to search for

        Returns:
            Optional[Track]: track if it exists
        """
        return self._dataset.get_for(id)

    def get_all(self) -> TrackDataset:
        """
        Retrieve all tracks.

        Returns:
            list[Track]: all tracks within the repository
        """
        return self._dataset

    def clear(self) -> None:
        """
        Clear the repository and inform the observers about the empty repository.
        """
        self._dataset = self._dataset.clear()
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
