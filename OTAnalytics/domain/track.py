from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional

from PIL import Image

from OTAnalytics.domain.common import DataclassValidation
from OTAnalytics.domain.geometry import Coordinate, RelativeOffsetCoordinate
from OTAnalytics.domain.observer import Subject

CLASSIFICATION: str = "classification"
CONFIDENCE: str = "confidence"
X: str = "x"
Y: str = "y"
W: str = "w"
H: str = "h"
FRAME: str = "frame"
OCCURRENCE: str = "occurrence"
INTERPOLATED_DETECTION: str = "interpolated_detection"
TRACK_ID: str = "track_id"


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
        occurrence (datetime): the time of the detection's occurrence.
        interpolated_detection (bool): whether this detection is interpolated.
        track_id (TrackId): the track id this detection belongs to.
        video_name (str): name of video that this detection belongs.
    """

    classification: str
    confidence: float
    x: float
    y: float
    w: float
    h: float
    frame: int
    occurrence: datetime
    interpolated_detection: bool
    track_id: TrackId
    video_name: str

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
            INTERPOLATED_DETECTION: self.interpolated_detection,
            TRACK_ID: self.track_id.id,
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
class Track(DataclassValidation):
    """Represents the track of an object as seen in the task of object tracking
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
        self._validate_track_has_detections()
        self._validate_detections_sorted_by_occurrence()

    def _validate_track_has_detections(self) -> None:
        if not self.detections:
            raise TrackHasNoDetectionError(
                self.id,
                (
                    f"Trying to construct track (track_id={self.id.id})"
                    " with no detections."
                ),
            )

    def _validate_detections_sorted_by_occurrence(self) -> None:
        if self.detections != sorted(self.detections, key=lambda det: det.occurrence):
            raise ValueError("detections must be sorted by occurrence")

    @property
    def start(self) -> datetime:
        """Get start time of this track.

        Returns:
            datetime: the start time.
        """
        return self.detections[0].occurrence

    @property
    def end(self) -> datetime:
        """Get end time of this track.

        Returns:
            datetime: the end time.
        """
        return self.detections[-1].occurrence

    @property
    def first_detection(self) -> Detection:
        """Get first detection of track.

        Returns:
            Detection: the first detection.
        """
        return self.detections[0]

    @property
    def last_detection(self) -> Detection:
        """Get last detection of track.

        Returns:
            Detection: the last detection.
        """
        return self.detections[-1]


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


class TrackRemoveError(Exception):
    def __init__(self, track_id: TrackId, message: str) -> None:
        """Exception to be raised if track can not be removed.

        Args:
            track_id (TrackId): the track id of the track to be removed.
            message (str): the error message.
        """
        self._track_id = track_id
        super().__init__(message)


class RemoveMultipleTracksError(Exception):
    """Exception to be raised if multiple tracks can not be removed.

    Args:
        track_ids (list[TrackId]): the track id of the track to be removed.
        message (str): the error message.
    """

    def __init__(self, track_ids: list[TrackId], message: str):
        self._track_ids = track_ids
        super().__init__(message)


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

    def add_all(self, tracks: Iterable[Track]) -> None:
        """
        Add multiple tracks to the repository and notify only once about it.

        Args:
            tracks (Iterable[Track]): tracks to be added
        """
        if tracks:
            self.__add_all(tracks)

    def __add_all(self, tracks: Iterable[Track]) -> None:
        """Internal method to add all tracks to the repository and notify only once
        about it.

        Args:
            tracks (list[Track]): tracks to be added
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
        return self._tracks.get(id)

    def get_all(self) -> list[Track]:
        """
        Retrieve all tracks.

        Returns:
            list[Track]: all tracks within the repository
        """
        return list(self._tracks.values())

    def get_all_ids(self) -> Iterable[TrackId]:
        """Get all track ids in this repository.

        Returns:
            Iterable[TrackId]: the track ids.
        """
        return self._tracks.keys()

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
        del self._tracks[track_id]

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
        self._tracks.clear()
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
