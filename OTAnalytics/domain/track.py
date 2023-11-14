from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Iterator, Optional, Sequence

from PIL import Image

from OTAnalytics.domain.common import DataclassValidation
from OTAnalytics.domain.geometry import Coordinate, RelativeOffsetCoordinate
from OTAnalytics.domain.observer import Subject
from OTAnalytics.domain.section import Section, SectionId

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


@dataclass(frozen=True)
class TrackRepositoryEvent:
    added: list[TrackId]
    removed: list[TrackId]


class TrackListObserver(ABC):
    """
    Interface to listen to changes to a list of tracks.
    """

    @abstractmethod
    def notify_tracks(self, track_event: TrackRepositoryEvent) -> None:
        """
        Notifies that the given tracks have been added.

        Args:
            track_event (TrackRepositoryEvent): list of added or removed tracks.
        """
        raise NotImplementedError


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


@dataclass
class IntersectionPoint:
    index: int


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

    @abstractmethod
    def intersecting_tracks(self, sections: list[Section]) -> set[TrackId]:
        """Return a set of tracks intersecting a set of sections.

        Args:
            sections (list[Section]): the list of sections to intersect.

        Returns:
            set[TrackId]: the track ids intersecting the given sections.
        """
        raise NotImplementedError

    @abstractmethod
    def intersection_points(
        self,
        sections: list[Section],
    ) -> dict[TrackId, list[tuple[SectionId, IntersectionPoint]]]:
        """
        Return the intersection points resulting from the tracks and the
        given sections.

        Args:
            sections (list[Section]): the sections to intersect with.

        Returns:
            dict[TrackId, list[tuple[SectionId]]]: the intersection points.
        """
        raise NotImplementedError

    @abstractmethod
    def split(self, chunks: int) -> Sequence["TrackDataset"]:
        raise NotImplementedError

    @abstractmethod
    def __len__(self) -> int:
        """Number of tracks in the dataset."""
        raise NotImplementedError

    @abstractmethod
    def filter_by_min_detection_length(self, length: int) -> "TrackDataset":
        """Filter tracks by the minimum length of detections.

        Args:
            length (int): minimum number detections a track should have.

        Returns:
             TrackDataset: the filtered dataset.
        """
        raise NotImplementedError


class TrackRepository:
    def __init__(self, dataset: TrackDataset) -> None:
        self._dataset = dataset
        self.observers = Subject[TrackRepositoryEvent]()

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
            self.observers.notify(TrackRepositoryEvent(new_tracks, []))

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
            self._dataset = self._dataset.remove(track_id)
        except KeyError:
            raise TrackRemoveError(
                track_id, f"Trying to remove non existing track with id '{track_id.id}'"
            )
        # TODO: Pass removed track id to notify when moving observers to
        #  application layer
        self.observers.notify(TrackRepositoryEvent([], [track_id]))

    def remove_multiple(self, track_ids: set[TrackId]) -> None:
        failed_tracks: list[TrackId] = []
        for track_id in track_ids:
            try:
                self._dataset = self._dataset.remove(track_id)
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
        self.observers.notify(TrackRepositoryEvent([], list(track_ids)))

    def split(self, chunks: int) -> Iterable[TrackDataset]:
        return self._dataset.split(chunks)

    def clear(self) -> None:
        """
        Clear the repository and inform the observers about the empty repository.
        """
        removed = list(self._dataset.get_all_ids())
        self._dataset = self._dataset.clear()
        self.observers.notify(TrackRepositoryEvent([], removed))


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
