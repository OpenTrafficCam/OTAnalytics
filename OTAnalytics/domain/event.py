import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Optional

from OTAnalytics.domain.common import DataclassValidation
from OTAnalytics.domain.geometry import DirectionVector2D, ImageCoordinate
from OTAnalytics.domain.section import SectionId
from OTAnalytics.domain.track import Detection
from OTAnalytics.domain.types import EventType

EVENT_LIST = "event_list"
ROAD_USER_ID = "road_user_id"
ROAD_USER_TYPE = "road_user_type"
HOSTNAME = "hostname"
OCCURRENCE = "occurrence"
FRAME_NUMBER = "frame_number"
SECTION_ID = "section_id"
EVENT_COORDINATE = "event_coordinate"
EVENT_TYPE = "event_type"
DIRECTION_VECTOR = "direction_vector"
VIDEO_NAME = "video_name"

DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S.%f"
FILE_NAME_PATTERN = r"(?P<hostname>[A-Za-z0-9]+)_.*\..*"


class InproperFormattedFilename(Exception):
    """This exception indicates an in proper formatted file name."""

    pass


class IncompleteEventBuilderSetup(Exception):
    """This section indicates an incomplete event builder setup."""

    pass


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
        section_id (Optional[SectionId]): only set when event type is of section
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
    section_id: Optional[SectionId]
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

    def to_dict(self) -> dict:
        """Convert event into dict to interact with other parts of the system,
        e.g. serialization.

        Returns:
            dict: serialized event
        """
        return {
            ROAD_USER_ID: self.road_user_id,
            ROAD_USER_TYPE: self.road_user_type,
            HOSTNAME: self.hostname,
            OCCURRENCE: self.occurrence.strftime(DATE_FORMAT),
            FRAME_NUMBER: self.frame_number,
            SECTION_ID: self._serialized_section_id(),
            EVENT_COORDINATE: self.event_coordinate.to_list(),
            EVENT_TYPE: self.event_type.value,
            DIRECTION_VECTOR: self.direction_vector.to_list(),
            VIDEO_NAME: self.video_name,
        }

    def _serialized_section_id(self) -> Optional[str]:
        return self.section_id.serialize() if self.section_id else None


class EventBuilder(ABC):
    """Defines an interface to build various type of events.

    Raises:
        InproperFormattedFilename: if hostname could not be extracted from filename
    """

    def __init__(self) -> None:
        self.road_user_type: Optional[str] = None
        self.event_type: Optional[EventType] = None
        self.direction_vector: Optional[DirectionVector2D] = None
        self.event_coordinate: Optional[ImageCoordinate] = None

    @abstractmethod
    def create_event(self, detection: Detection) -> Event:
        """Creates an event with the information stored in a detection.

        Args:
            detection (Detection): the detection holding the information

        Returns:
            Event: the event
        """
        pass

    @staticmethod
    def extract_hostname(name: str) -> str:
        """Extract hostname from name.

        Args:
            name (Path): name containing the hostname.

        Raises:
            InproperFormattedFilename: if the name is not formatted as expected, an
                exception will be raised.

        Returns:
            str: the hostname.
        """
        match = re.search(
            FILE_NAME_PATTERN,
            name,
        )
        if match:
            hostname: str = match.group(HOSTNAME)
            return hostname
        raise InproperFormattedFilename(f"Could not parse {name}. Hostname is missing.")

    def add_road_user_type(self, road_user_type: str) -> None:
        """Add a road user type to add to the event to be build.

        Args:
            road_user_type (str): the road user type
        """
        self.road_user_type = road_user_type

    def add_event_type(self, event_type: EventType) -> None:
        """Add an event type to add to the event to be build.

        Args:
            event_type (EventType): the event type
        """
        self.event_type = event_type

    def add_direction_vector(self, vector: DirectionVector2D) -> None:
        """Add direction vector to add to the event to be build.

        Args:
            vector (DirectionVector2D): the direction vector to be build
        """
        self.direction_vector = vector

    def add_event_coordinate(self, x: float, y: float) -> None:
        """Add event coordinate to the event to be build.

        Args:
            x (float): the x component coordinate
            y (float): the y component coordinate
        """
        self.event_coordinate = ImageCoordinate(x, y)


class SectionEventBuilder(EventBuilder):
    """A builder to build section events."""

    def __init__(self) -> None:
        super().__init__()
        self.section_id: Optional[SectionId] = None

    def add_section_id(self, section_id: SectionId) -> None:
        """Add a section id to add to the event to be build.

        Args:
            section_id (SectionId): the section id
        """
        self.section_id = section_id

    def create_event(self, detection: Detection) -> Event:
        """Creates an section event with the information stored in a detection.

        Args:
            detection (Detection): the detection holding the information

        Raises:
            IncompleteEventBuilderSetup: if attribute 'section_id' is not set
            IncompleteEventBuilderSetup: if attribute 'event_type' is not set
            IncompleteEventBuilderSetup: attribute 'direction_vector' is not set
            IncompleteEventBuilderSetup: attribute 'event_coordinate' is not set

        Returns:
            Event: the section event
        """
        if not self.section_id:
            raise IncompleteEventBuilderSetup("attribute 'section_id' is not set")

        if not self.event_type:
            raise IncompleteEventBuilderSetup("attribute 'event_type' is not set")

        if not self.direction_vector:
            raise IncompleteEventBuilderSetup("attribute 'direction_vector' is not set")

        if not self.road_user_type:
            raise IncompleteEventBuilderSetup("attribute 'road_user_type' is not set")

        if not self.event_coordinate:
            raise IncompleteEventBuilderSetup("attribute 'event_coordinate' is not set")

        return Event(
            road_user_id=detection.track_id.id,
            road_user_type=self.road_user_type,
            hostname=self.extract_hostname(detection.video_name),
            occurrence=detection.occurrence,
            frame_number=detection.frame,
            section_id=self.section_id,
            event_coordinate=self.event_coordinate,
            event_type=self.event_type,
            direction_vector=self.direction_vector,
            video_name=detection.video_name,
        )


class SceneEventBuilder(EventBuilder):
    """A builder to build scene events."""

    def __init__(self) -> None:
        super().__init__()

    def create_event(self, detection: Detection) -> Event:
        """Creates a scene event with the information stored in a detection.

        Args:
            detection (Detection): the detection holding the information

        Raises:
            IncompleteEventBuilderSetup: if attribute 'event_type' is not set
            IncompleteEventBuilderSetup: attribute 'direction_vector' is not set
            IncompleteEventBuilderSetup: attribute 'event_coordinate' is not set
            IncompleteEventBuilderSetup: attribute 'road_user_type' is not set

        Returns:
            Event: the scene event
        """
        if not self.event_type:
            raise IncompleteEventBuilderSetup("attribute 'event_type' is not set")

        if not self.direction_vector:
            raise IncompleteEventBuilderSetup("attribute 'direction_vector' is not set")

        if not self.event_coordinate:
            raise IncompleteEventBuilderSetup("attribute 'event_coordinate' is not set")

        if not self.road_user_type:
            raise IncompleteEventBuilderSetup("attribute 'road_user_type' is not set")

        return Event(
            road_user_id=detection.track_id.id,
            road_user_type=self.road_user_type,
            hostname=self.extract_hostname(detection.video_name),
            occurrence=detection.occurrence,
            frame_number=detection.frame,
            section_id=None,
            event_coordinate=self.event_coordinate,
            event_type=self.event_type,
            direction_vector=self.direction_vector,
            video_name=detection.video_name,
        )


class EventRepository:
    """The repository to store events."""

    def __init__(self) -> None:
        self._events: list[Event] = []

    def add(self, event: Event) -> None:
        """Add an event to the repository.

        Args:
            event (Event): the event to add
        """
        self._events.append(event)

    def add_all(self, events: Iterable[Event]) -> None:
        """Add multiple events at once to the repository.

        Args:
            events (Iterable[Event]): the events
        """
        self._events.extend(events)

    def get_all(self) -> Iterable[Event]:
        """Get all events stored in the repository.

        Returns:
            Iterable[Event]: the events
        """
        return self._events

    def clear(self) -> None:
        """
        Clear the repository.
        """
        self._events.clear()
