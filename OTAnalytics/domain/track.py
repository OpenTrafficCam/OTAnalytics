from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Iterable, Iterator, Optional, Sequence

from PIL import Image

from OTAnalytics.domain.common import DataclassValidation
from OTAnalytics.domain.geometry import Coordinate, RelativeOffsetCoordinate
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


@dataclass(frozen=True, order=True)
class TrackId(DataclassValidation):
    id: str

    def __str__(self) -> str:
        return self.id


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
        if not offset or offset == RelativeOffsetCoordinate(0, 0):
            return Coordinate(self.x, self.y)
        else:
            return Coordinate(
                x=self.x + self.w * offset.x,
                y=self.y + self.h * offset.y,
            )


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

    @abstractmethod
    def get_detection(self, index: int) -> Detection:
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
    def intersecting_tracks(
        self, sections: list[Section], offset: RelativeOffsetCoordinate
    ) -> set[TrackId]:
        """Return a set of tracks intersecting a set of sections.

        Args:
            sections (list[Section]): the list of sections to intersect.
            offset (RelativeOffsetCoordinate): the offset to be applied to the tracks.

        Returns:
            set[TrackId]: the track ids intersecting the given sections.
        """
        raise NotImplementedError

    @abstractmethod
    def intersection_points(
        self, sections: list[Section], offset: RelativeOffsetCoordinate
    ) -> dict[TrackId, list[tuple[SectionId, IntersectionPoint]]]:
        """
        Return the intersection points resulting from the tracks and the
        given sections.

        Args:
            sections (list[Section]): the sections to intersect with.
            offset (RelativeOffsetCoordinate): the offset to be applied to the tracks.

        Returns:
            dict[TrackId, list[tuple[SectionId]]]: the intersection points.
        """
        raise NotImplementedError

    @abstractmethod
    def contained_by_sections(
        self, sections: list[Section], offset: RelativeOffsetCoordinate
    ) -> dict[TrackId, list[tuple[SectionId, list[bool]]]]:
        """Return whether track coordinates are contained by the given sections.

        Args:
             sections (list[Section]): the sections.
             offset (RelativeOffsetCoordinate): the offset to be applied to the tracks.

        Returns:
            dict[TrackId, list[tuple[SectionId, list[bool]]]]: boolean mask of track
                coordinates contained by given sections.
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

    @abstractmethod
    def calculate_geometries_for(
        self, offsets: Iterable[RelativeOffsetCoordinate]
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def apply_to_first_segments(self, consumer: Callable[[Any], None]) -> None:
        raise NotImplementedError

    @abstractmethod
    def apply_to_last_segments(self, consumer: Callable[[Any], None]) -> None:
        raise NotImplementedError


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


class TrackGeometryDataset(ABC):
    """Dataset containing track geometries.

    Only tracks of size greater equal two are contained in the dataset.
    Tracks of size less than two will not be contained in the dataset
    since it is not possible to construct a track with less than two
    coordinates.
    """

    @property
    @abstractmethod
    def track_ids(self) -> set[str]:
        """Get track ids of tracks stored in dataset.

        Returns:
            set[str]: the track ids stored.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def offset(self) -> RelativeOffsetCoordinate:
        raise NotImplementedError

    @property
    @abstractmethod
    def empty(self) -> bool:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def from_track_dataset(
        dataset: TrackDataset, offset: RelativeOffsetCoordinate
    ) -> "TrackGeometryDataset":
        raise NotImplementedError

    @abstractmethod
    def add_all(self, tracks: Iterable[Track]) -> "TrackGeometryDataset":
        """Add tracks to existing dataset.

        Pre-existing tracks will be overwritten.

        Args:
            tracks (Iterable[Track]): the tracks to add.

        Returns:
            TrackGeometryDataset: the dataset with tracks added.

        """
        raise NotImplementedError

    @abstractmethod
    def remove(self, ids: Iterable[TrackId]) -> "TrackGeometryDataset":
        """Remove track geometries with given ids from dataset.

        Args:
            ids (Iterable[TrackId]): the track geometries to remove.

        Returns:
            TrackGeometryDataset: the dataset with tracks removed.
        """
        raise NotImplementedError

    @abstractmethod
    def get_for(self, track_ids: Iterable[str]) -> "TrackGeometryDataset":
        """Get geometries for given track ids if they exist.

        Ids that do not exist will not be included in the dataset.

        Args:
            track_ids (Iterable[str]): the track ids.

        Returns:
            TrackGeometryDataset: the dataset with tracks.
        """
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
        self, sections: list[Section]
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
    def contained_by_sections(
        self, sections: list[Section]
    ) -> dict[TrackId, list[tuple[SectionId, list[bool]]]]:
        """Return whether track coordinates are contained by the given sections.

        Args:
             sections (list[Section]): the sections.

        Returns:
            dict[TrackId, list[tuple[SectionId, list[bool]]]]: boolean mask
                of track coordinates contained by given sections.
        """
        raise NotImplementedError


TRACK_GEOMETRY_FACTORY = Callable[
    [TrackDataset, RelativeOffsetCoordinate], TrackGeometryDataset
]
