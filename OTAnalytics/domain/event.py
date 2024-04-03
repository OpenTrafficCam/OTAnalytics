import itertools
import re
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Iterable, Optional, Sequence

from OTAnalytics.domain.common import DataclassValidation
from OTAnalytics.domain.geometry import DirectionVector2D, ImageCoordinate
from OTAnalytics.domain.observer import OBSERVER, Subject
from OTAnalytics.domain.section import Section, SectionId
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


class ImproperFormattedFilename(Exception):
    """This exception indicates an improper formatted file name."""

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
        road_user_id (str): the road user id involved with this event. It must be
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

    road_user_id: str
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

    def to_typed_dict(self) -> dict:
        """Convert event into dict to interact with other parts of the system,
        e.g. serialization.

        Returns:
            dict: serialized event
        """
        return {
            ROAD_USER_ID: self.road_user_id,
            ROAD_USER_TYPE: self.road_user_type,
            HOSTNAME: self.hostname,
            OCCURRENCE: self.occurrence,
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
        self.section_id: Optional[SectionId] = None

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
        raise ImproperFormattedFilename(f"Could not parse {name}. Hostname is missing.")

    def add_road_user_type(self, road_user_type: str) -> None:
        """Add a road user type to add to the event to be built.

        Args:
            road_user_type (str): the road user type
        """
        self.road_user_type = road_user_type

    def add_event_type(self, event_type: EventType) -> None:
        """Add an event type to add to the event to be built.

        Args:
            event_type (EventType): the event type
        """
        self.event_type = event_type

    def add_direction_vector(self, vector: DirectionVector2D) -> None:
        """Add direction vector to add to the event to be built.

        Args:
            vector (DirectionVector2D): the direction vector to be build
        """
        self.direction_vector = vector

    def add_event_coordinate(self, x: float, y: float) -> None:
        """Add event coordinate to the event to be built.

        Args:
            x (float): the x component coordinate
            y (float): the y component coordinate
        """
        self.event_coordinate = ImageCoordinate(x, y)

    def add_section_id(self, section_id: SectionId) -> None:
        """Add a section id to add to the event to be built.

        Args:
            section_id (SectionId): the section id
        """
        self.section_id = section_id


class SectionEventBuilder(EventBuilder):
    """A builder to build section events."""

    def __init__(self) -> None:
        super().__init__()
        self.section_id: Optional[SectionId] = None

    def create_event(self, detection: Detection) -> Event:
        """Creates a section event with the information stored in a detection.

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


@dataclass
class EventRepositoryEvent:
    """Holds information on changes made in the event repository.

    `Added` holding an empty iterable indicates remove events.

    Args:
        added (Iterable[Event]): events added to repository.
        removed (Iterable[Event]): events removed from the repository.
    """

    added: Iterable[Event]
    removed: Iterable[Event]


class EventRepository:
    """The repository to store events."""

    def __init__(
        self, subject: Subject[EventRepositoryEvent] = Subject[EventRepositoryEvent]()
    ) -> None:
        self._subject = subject
        self._events: dict[SectionId, list[Event]] = defaultdict(list)
        self._non_section_events = list[Event]()

    def register_observer(self, observer: OBSERVER[EventRepositoryEvent]) -> None:
        """Register observer to listen to repository changes.

        Args:
            observer (OBSERVER[EventRepositoryEvent]): the observer to registered.
        """
        self._subject.register(observer)

    def add(self, event: Event) -> None:
        """Add an event to the repository.

        Args:
            event (Event): the event to add
        """
        self.__do_add(event)
        self.__discard_duplicates()
        self.__sort()
        self._subject.notify(EventRepositoryEvent([event], []))

    def __do_add(self, event: Event) -> None:
        """
        Internal add method that does not notify observers.
        """
        if event.section_id:
            self._events[event.section_id].append(event)
        else:
            self._non_section_events.append(event)

    def __discard_duplicates(self) -> None:
        """Discard duplicate events in repository."""
        self._non_section_events = self.__remove_duplicates(self._non_section_events)
        for section_id, events in self._events.items():
            self._events[section_id] = self.__remove_duplicates(events)

    def __remove_duplicates(self, events: Iterable[Event]) -> list[Event]:
        """Discard duplicate events while retaining insertion order."""
        return list(dict.fromkeys(events))

    def add_all(
        self, events: Iterable[Event], sections: list[SectionId] | None = None
    ) -> None:
        """
        Add multiple events at once to the repository. Preserve the sections used
        to generate the events for later usage.

        Args:
            events (Iterable[Event]): the events
            sections (list[SectionId]): the  sections which have been used to generate
                the events
        """
        if sections is None:
            sections = []
        for event in events:
            self.__do_add(event)
        for section in sections:
            self._events.setdefault(section, [])
        self.__discard_duplicates()
        self.__sort()
        self._subject.notify(EventRepositoryEvent(events, []))

    @staticmethod
    def comparator(event: Event) -> datetime:
        return event.occurrence

    def __sort(self) -> None:
        self._non_section_events = sorted(self._non_section_events, key=self.comparator)
        for section_id, events in self._events.items():
            self._events[section_id] = sorted(events, key=self.comparator)

    def get_all(self) -> Iterable[Event]:
        """Get all events stored in the repository.

        Returns:
            Iterable[Event]: the events
        """
        return list(
            itertools.chain.from_iterable(
                [self._non_section_events, *self._events.values()]
            )
        )

    def clear(self) -> None:
        """
        Clear the repository and notify observers only if repository was filled.
        """
        if self._events:
            removed = list(self.get_all())
            self._events = defaultdict(list)
            self._non_section_events = list[Event]()
            self._subject.notify(EventRepositoryEvent([], removed))

    def remove(self, sections: list[SectionId]) -> None:
        if self._events:
            removed = [
                event for event in self.get_all() if event.section_id in sections
            ]
            for section in sections:
                if section in self._events.keys():
                    del self._events[section]
            self._subject.notify((EventRepositoryEvent([], removed)))

    def is_empty(self) -> bool:
        """Whether repository is empty."""
        return not self._events

    def retain_missing(self, all: list[Section]) -> list[Section]:
        """
        Returns a new list of sections. The list contains all Sections from the input
        except the ones event have been generated for.
        """
        return [section for section in all if section.id not in self._events.keys()]

    def get_next_after(
        self,
        date: datetime,
        sections: Sequence[SectionId] | None = None,
        event_types: Sequence[EventType] | None = None,
    ) -> Optional[Event]:
        if sections is None:
            sections = []
        for event in sorted(
            self.get(sections=sections, event_types=event_types),
            key=lambda actual: actual.occurrence,
        ):
            if event.occurrence > date:
                return event
        return None

    def get_previous_before(
        self,
        date: datetime,
        sections: Sequence[SectionId] | None = None,
        event_types: Sequence[EventType] | None = None,
    ) -> Optional[Event]:
        if sections is None:
            sections = []
        for event in sorted(
            self.get(sections=sections, event_types=event_types),
            key=lambda actual: actual.occurrence,
            reverse=True,
        ):
            if event.occurrence < date:
                return event
        return None

    def get(
        self,
        sections: Sequence[SectionId] | None = None,
        event_types: Sequence[EventType] | None = None,
    ) -> Iterable[Event]:
        if event_types is None:
            event_types = []
        if sections is None:
            sections = []
        filter_function = self.__create_filter(event_types)
        events = self.__create_event_list(sections)
        return list(filter(filter_function, events))

    def __create_event_list(self, sections: Sequence[SectionId]) -> Iterable[Event]:
        if sections:
            event_lists = [self._events[section] for section in sections]
            return list(itertools.chain.from_iterable(event_lists))
        return self.get_all()

    @staticmethod
    def __create_filter(event_types: Sequence[EventType]) -> Callable[[Event], bool]:
        if event_types:
            return lambda actual: actual.event_type in event_types
        return lambda event: True
