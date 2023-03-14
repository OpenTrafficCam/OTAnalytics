import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

from domain.track import Detection

from OTAnalytics.domain.common import DataclassValidation
from OTAnalytics.domain.geometry import DirectionVector2D, ImageCoordinate

HOSTNAME = "hostname"
FILE_NAME_PATTERN = r"(?P<hostname>[A-Za-z0-9]+)" r"_.*\..*"


class InproperFormattedFilename(Exception):
    pass


class BuildError(Exception):
    pass


class EventType(Enum):
    """Enum defining all event types."""

    SECTION_ENTER: str = "section-enter"
    SECTION_LEAVE: str = "section-leave"


@dataclass(frozen=True, kw_only=True)
class Event(DataclassValidation):
    """A traffic event triggered by some traffic event holding all necessary
    information for further processing.

    One party involved in this event is a road user. It is not required for necessarily
    required for more than 1 party to be involved in this event.

    An event can be raised upon certain traffic actions.
    To give an example such actions could be:
    - a vehicle has entered a section
    - a vehicle has left a section
    - section entered by a vehicle

    Raises:
        ValueError: vehicle_id < 1
        ValueError: frame_number < 1

    Args:
        road_user_id (int): the road user id involved with this event. It must be
        greater equal one.
        road_user_type (str): the road user type involved with this event.
        hostname (str): the OTCamera hostname that the video is associated with.
        occurrence (datetime): the time when this event occurred.
        frame_number (int): the video frame number that this event is associated with.
        section_id (Optional[str]): only set when event type is of section.
        Defaults to `None`.
        event_coordinate (ImageCoordinate): location where the event occurred in
        the video.
        event_type (EventType): this event's type.
        direction_vector (DirectionVector2D): a 2-dimensional direction vector denoting
        the direction of the road user associated with this event.
        video_name (str): the video name associated with this event.

    """

    road_user_id: int
    road_user_type: str
    hostname: str
    occurrence: datetime
    frame_number: int
    section_id: Optional[str]
    event_coordinate: ImageCoordinate
    event_type: EventType
    direction_vector: DirectionVector2D
    video_name: str

    def _validate(self) -> None:
        self._validate_road_user_id_greater_zero()
        self._validate_frame_number_greater_equal_one()

    def _validate_frame_number_greater_equal_one(self) -> None:
        if self.frame_number < 1:
            raise (
                ValueError(
                    (
                        "frame number must be greater equal one, "
                        f"but it {self.frame_number}"
                    )
                )
            )

    def _validate_road_user_id_greater_zero(self) -> None:
        if self.road_user_id < 0:
            raise ValueError(
                f"vehicle_id must be greater than zero, but is {self.road_user_id}"
            )


class EventBuilder(ABC):
    @abstractmethod
    def create_event(self, detection: Detection) -> Event:
        pass

    def extract_hostname(self, file_path: Path) -> str:
        """Parse the given filename and retrieve the start date of the video.

        Args:
            video_file (Path): path to video file

        Raises:
            InproperFormattedFilename: if the filename is not formatted as expected, an
            exception will be raised

        Returns:
            datetime: start date of the video
        """
        match = re.search(
            FILE_NAME_PATTERN,
            file_path.name,
        )
        if match:
            hostname: str = match.group(HOSTNAME)
            return hostname
        raise InproperFormattedFilename(f"Could not parse {file_path.name}.")


class SectionEventBuilder(EventBuilder):
    def __init__(self) -> None:
        self.section_id: Optional[str] = None
        self.direction_vector: Optional[DirectionVector2D] = None
        self.event_type: Optional[EventType] = None

    def reset(self) -> None:
        self.section_id = None
        self.direction_vector = None
        self.event_type = None

    def add_section_id(self, section_id: str) -> None:
        self.section_id = section_id

    def add_event_type(self, event_type: EventType) -> None:
        self.event_type = event_type

    def add_direction_vector(
        self, detection_1: Detection, detection_2: Detection
    ) -> None:
        self.direction_vector = DirectionVector2D(
            x1=detection_2.x - detection_1.x, x2=detection_2.y - detection_1.y
        )

    def create_event(self, detection: Detection) -> Event:
        if not self.section_id:
            raise BuildError("attribute 'section_id' is not set")

        if not self.event_type:
            raise BuildError("attribute 'event_type' is not set")

        if not self.direction_vector:
            raise BuildError("attribute 'direction_vector' is not set")

        section_event = Event(
            road_user_id=detection.track_id,
            road_user_type=detection.classification,
            hostname=self.extract_hostname(detection.input_file_path),
            occurrence=detection.occurrence,
            frame_number=detection.frame,
            section_id=self.section_id,
            event_coordinate=ImageCoordinate(detection.x, detection.y),
            event_type=self.event_type,
            direction_vector=self.direction_vector,
            video_name=detection.input_file_path.name,
        )
        self.reset()
        return section_event
