from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

from PIL import Image

from OTAnalytics.domain.geometry import Coordinate, RelativeOffsetCoordinate

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
ORIGINAL_TRACK_ID: str = "original_track_id"
VIDEO_NAME: str = "video_name"
INPUT_FILE: str = "input_file"


@dataclass(frozen=True, order=True)
class TrackId:
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

    @property
    @abstractmethod
    def input_file(self) -> str:
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
            INPUT_FILE: self.input_file,
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
    def original_id(self) -> TrackId:
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

    def save(self, name: str) -> None:
        self.as_image().save(name)


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
    def add_original_id(self, original_track_id: TrackId) -> None:
        """Add the original id of the track to be built.

        Args:
            original_track_id (TrackId): the id.
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
