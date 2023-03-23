import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

from OTAnalytics.domain.common import DataclassValidation
from OTAnalytics.domain.geometry import DirectionVector2D, ImageCoordinate
from OTAnalytics.domain.track import Detection

HOSTNAME = "hostname"
FILE_NAME_PATTERN = r"(?P<hostname>[A-Za-z0-9]+)" r"_.*\..*"


class InproperFormattedFilename(Exception):
    """This exception indicates an in proper formatted file name."""

    pass


class IncompleteEventBuilderSetup(Exception):
    """This section indicates an incomplete event builder setup."""

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
            greater equal one
        road_user_type (str): the road user type involved with this event
        hostname (str): the OTCamera hostname that the video is associated with
        occurrence (datetime): the time when this event occurred
        frame_number (int): the video frame number that this event is associated with
        section_id (Optional[str]): only set when event type is of section
            Defaults to `None`.
        event_coordinate (ImageCoordinate): location where the event occurred in
            the video
        event_type (EventType): this event's type
        direction_vector (DirectionVector2D): a 2-dimensional direction vector denoting
            the direction of the road user associated with this event
        video_name (str): the video name associated with this event

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
                        f"but is {self.frame_number}"
                    )
                )
            )

    def _validate_road_user_id_greater_zero(self) -> None:
        if self.road_user_id < 1:
            raise ValueError(
                f"vehicle_id must be at least 1, but is {self.road_user_id}"
            )


class EventBuilder(ABC):
    """Defines an interface to build various type of events.

    Raises:
        InproperFormattedFilename: if hostname could not be extracted from filename
    """

    @abstractmethod
    def create_event(self, detection: Detection) -> Event:
        """Creates an event with the information stored in a detection.

        Args:
            detection (Detection): the detection holding the information

        Returns:
            Event: the event
        """
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
        raise InproperFormattedFilename(
            f"Could not parse {file_path.name}. Hostname is missing."
        )


class SectionEventBuilder(EventBuilder):
    """A builder to build section events."""

    def __init__(self) -> None:
        self.section_id: Optional[str] = None
        self.direction_vector: Optional[DirectionVector2D] = None
        self.event_type: Optional[EventType] = None

    def add_section_id(self, section_id: str) -> None:
        """Add a section id to add to the event to be build.

        Args:
            section_id (str): the section id
        """
        self.section_id = section_id

    def add_event_type(self, event_type: EventType) -> None:
        """Add an event type to add to the event to be build.

        Args:
            event_type (EventType): the event type
        """
        self.event_type = event_type

    def add_direction_vector(
        self, detection_1: Detection, detection_2: Detection
    ) -> None:
        """Build direction vector from two detections and add to the event to be build.

        Let x1 be `detection_1.x` and x2 be `detection_1.y` be a coordinate x = (x1,x2).
        Let y1 be `detection_2.x` and y2 be `detection_2.y` be a coordinate y = (x1,x2).
        The direction vector v is calculated by v = y-x.

        Args:
            detection_1 (Detection): the first detection
            detection_2 (Detection): the second detection
        """
        self.direction_vector = DirectionVector2D(
            x1=detection_2.x - detection_1.x, x2=detection_2.y - detection_1.y
        )

    def create_event(self, detection: Detection) -> Event:
        """Creates an event with the information stored in a detection.

        Args:
            detection (Detection): the detection holding the information

        Raises:
            BuildError: if attribute 'section_id' is not set
            BuildError: if attribute 'event_type' is not set
            BuildError: attribute 'direction_vector' is not set

        Returns:
            Event: the section event
        """
        if not self.section_id:
            raise IncompleteEventBuilderSetup("attribute 'section_id' is not set")

        if not self.event_type:
            raise IncompleteEventBuilderSetup("attribute 'event_type' is not set")

        if not self.direction_vector:
            raise IncompleteEventBuilderSetup("attribute 'direction_vector' is not set")

        return Event(
            road_user_id=detection.track_id.id,
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
