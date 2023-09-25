from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Iterator, Optional

from PIL import Image

from OTAnalytics.application.logger import logger
from OTAnalytics.domain.common import DataclassValidation
from OTAnalytics.domain.geometry import Coordinate, RelativeOffsetCoordinate
from OTAnalytics.domain.observer import Subject

MIN_NUMBER_OF_DETECTIONS = 5
CLASSIFICATION: str = "classification"
TRACK_CLASSIFICATION: str = "track_classification"
CONFIDENCE: str = "confidence"
X: str = "x"
Y: str = "y"
W: str = "w"
H: str = "h"
FRAME: str = "frame"
OCCURRENCE: str = "occurrence"
INTERPOLATED_DETECTION: str = "interpolated_detection"
TRACK_ID: str = "track_id"
VIDEO_NAME: str = "video_name"


@dataclass(frozen=True)
class TrackId(DataclassValidation):
    id: str


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


class TrackHasNoDetectionError(TrackError):
    pass


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
    def interpolated_detection(self) -> bool:
        raise NotImplementedError

    @property
    @abstractmethod
    def track_id(self) -> TrackId:
        raise NotImplementedError

    @property
    @abstractmethod
    def video_name(self) -> str:
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
            INTERPOLATED_DETECTION: self.interpolated_detection,
            TRACK_ID: self.track_id.id,
            VIDEO_NAME: self.video_name,
        }

    def get_coordinate(self, offset: RelativeOffsetCoordinate | None) -> Coordinate:
        """Get coordinate of this detection.

        Args:
            offset (RelativeOffsetCoordinate | None): relative offset to be applied.

        Returns:
            Coordinate: this detection's coordinate.
        """
        if offset:
            return Coordinate(
                x=self.x + self.w * offset.x,
                y=self.y + self.h * offset.y,
            )
        else:
            return Coordinate(self.x, self.y)


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

    @property
    @abstractmethod
    def first_detection(self) -> Detection:
        """Get first detection of track.

        Returns:
            Detection: the first detection.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def last_detection(self) -> Detection:
        """Get last detection of track.

        Returns:
            Detection: the last detection.
        """
        raise NotImplementedError

    @property
    def start(self) -> datetime:
        """Get start time of this track.

        Returns:
            datetime: the start time.
        """
        return self.first_detection.occurrence

    @property
    def end(self) -> datetime:
        """Get end time of this track.

        Returns:
            datetime: the end time.
        """
        return self.last_detection.occurrence


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
            Image.Image: image as pillow image
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
    Concrete implementation using pillow as image format.
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


class TrackRemoveError(Exception):
    def __init__(self, track_id: TrackId, message: str) -> None:
        """Exception to be raised if track can not be removed.

        Args:
            track_id (TrackId): the track id of the track to be removed.
            message (str): the error message.
        """
        super().__init__(message)
        self._track_id = track_id


class RemoveMultipleTracksError(Exception):
    """Exception to be raised if multiple tracks can not be removed.

    Args:
        track_ids (list[TrackId]): the track id of the track to be removed.
        message (str): the error message.
    """

    def __init__(self, track_ids: list[TrackId], message: str):
        super().__init__(message)
        self._track_ids = track_ids


class TrackDataset(ABC):
    def __iter__(self) -> Iterator[Track]:
        yield from self.as_list()

    @abstractmethod
    def add_all(self, other: Iterable[Track]) -> "TrackDataset":
        raise NotImplementedError

    @abstractmethod
    def get_all_ids(self) -> Iterable[TrackId]:
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
    def remove(self, track_id: TrackId) -> "TrackDataset":
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


class TrackRepository:
    def __init__(self, dataset: TrackDataset = PythonTrackDataset()) -> None:
        self._dataset = dataset
        self.observers = Subject[list[TrackId]]()

    def register_tracks_observer(self, observer: TrackListObserver) -> None:
        """
        Listen to changes of the repository.

        Args:
            observer (TrackListObserver): listener to be notified about changes
        """
        self.observers.register(observer.notify_tracks)

    def add_all(self, tracks: Iterable[Track]) -> None:
        """
        Add multiple tracks to the repository and notify only once about it.

        Args:
            tracks (Iterable[Track]): tracks to be added
        """
        self._dataset = self._dataset.add_all(tracks)
        new_tracks = [track.id for track in tracks]
        if new_tracks:
            self.observers.notify(new_tracks)

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

    def get_all_ids(self) -> Iterable[TrackId]:
        """Get all track ids in this repository.

        Returns:
            Iterable[TrackId]: the track ids.
        """
        return self._dataset.get_all_ids()

    def remove(self, track_id: TrackId) -> None:
        """Remove track by its id and notify observers

        Raises:
            TrackRemoveError: if track does not exist in repository.

        Args:
            track_id (TrackId): the id of the track to be removed.
        """
        try:
            self._remove(track_id)
        except KeyError:
            raise TrackRemoveError(
                track_id, f"Trying to remove non existing track with id '{track_id.id}'"
            )
        # TODO: Pass removed track id to notify when moving observers to
        #  application layer
        self.observers.notify([])

    def _remove(self, track_id: TrackId) -> None:
        """Remove track by its id without notifying observers.

        Raises:
            TrackRemoveError: if track does not exist in repository.

        Args:
            track_id (TrackId): the id of the track to be removed.
        """
        self._dataset = self._dataset.remove(track_id)

    def remove_multiple(self, track_ids: set[TrackId]) -> None:
        failed_tracks: list[TrackId] = []
        for track_id in track_ids:
            try:
                self._remove(track_id)
            except KeyError:
                failed_tracks.append(track_id)
            # TODO: Pass removed track id to notify when moving observers to
            #  application layer

        if failed_tracks:
            raise RemoveMultipleTracksError(
                failed_tracks,
                (
                    "Multiple tracks with following ids could not be removed."
                    f" '{[failed_track.id for failed_track in failed_tracks]}'"
                ),
            )
        self.observers.notify([])

    def clear(self) -> None:
        """
        Clear the repository and inform the observers about the empty repository.
        """
        self._dataset = self._dataset.clear()
        self.observers.notify([])


class TrackFileRepository:
    def __init__(self) -> None:
        self._files: set[Path] = set()

    def add(self, file: Path) -> None:
        """
        Add a single track file the repository.

        Args:
            file (Path): track file to be added.
        """
        self._files.add(file)

    def add_all(self, files: Iterable[Path]) -> None:
        """
        Add multiple files to the repository.

        Args:
            files (Iterable[Path]): the files to be added.
        """
        for file in files:
            self.add(file)

    def get_all(self) -> set[Path]:
        """
        Retrieve all track files.

        Returns:
            set[Path]: all tracks within the repository.
        """
        return self._files.copy()


class TrackIdProvider(ABC):
    """Interface to provide track ids."""

    @abstractmethod
    def get_ids(self) -> Iterable[TrackId]:
        """Provide track ids.

        Returns:
            Iterable[TrackId]: the track ids.
        """
        pass


class TrackBuilderError(Exception):
    pass


class TrackBuilder(ABC):
    """Interface to create Tracks with different configuration strategies."""

    @abstractmethod
    def add_detection(self, detection: Detection) -> None:
        """Add a detection to the track to be built.

        Args:
            detection (Detection): the detection.
        """
        raise NotImplementedError

    @abstractmethod
    def add_id(self, track_id: str) -> None:
        """Add the id of the track to be built.

        Args:
            track_id (str): the id.
        """
        raise NotImplementedError

    @abstractmethod
    def build(self) -> Track:
        """Build a track with the configured settings.

        The builder will be reset after building the track.

        Raises:
            TrackBuildError: if track id has not been set.

        Returns:
            Track: the built track.
        """
        raise NotImplementedError

    @abstractmethod
    def reset(self) -> None:
        """Resets the builder.

        All configurations made to the builder will be reset.
        """
        raise NotImplementedError
