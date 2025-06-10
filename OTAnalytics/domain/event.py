import itertools
import re
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Iterable, Iterator, Optional, Sequence

from OTAnalytics.domain.common import DataclassValidation
from OTAnalytics.domain.geometry import DirectionVector2D, ImageCoordinate
from OTAnalytics.domain.observer import OBSERVER, Subject
from OTAnalytics.domain.section import Section, SectionId
from OTAnalytics.domain.track import Detection, TrackId
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
INTERPOLATED_OCCURRENCE = "interpolated_occurrence"
INTERPOLATED_EVENT_COORDINATE = "interpolated_event_coordinate"

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

    Attributes:
        road_user_id (str): the road user id involved with this event. It must be
            greater equal one.
        road_user_type (str): the road user type involved with this event.
        hostname (str): the OTCamera hostname that the video is associated with.
        occurrence (datetime): the time when this event occurred.
        frame_number (int): the video frame number that this event is associated with
        section_id (Optional[SectionId]): only set when event type is of section
            Defaults to `None`.
        event_coordinate (ImageCoordinate): location where the event occurred in
            the video.
        event_type (EventType): this event's type.
        direction_vector (DirectionVector2D): a 2-dimensional direction vector denoting
            the direction of the road user associated with this event.
        video_name (str): the video name associated with this event.
        interpolated_occurrence (datetime): the interpolated time when this
            event occurred.
        interpolated_event_coordinate (ImageCoordinate): interpolated event
            coordinate between two detections.
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
    interpolated_occurrence: datetime
    interpolated_event_coordinate: ImageCoordinate

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
            INTERPOLATED_OCCURRENCE: self.interpolated_occurrence.strftime(DATE_FORMAT),
            INTERPOLATED_EVENT_COORDINATE: self.interpolated_event_coordinate.to_list(),
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
            INTERPOLATED_OCCURRENCE: self.interpolated_occurrence,
            INTERPOLATED_EVENT_COORDINATE: self.interpolated_event_coordinate.to_list(),
        }

    def _serialized_section_id(self) -> Optional[str]:
        return self.section_id.serialize() if self.section_id else None


class EventBuilder(ABC):
    """Defines an interface to build various type of events.

    Raises:
        ImproperFormattedFilename: if hostname could not be extracted from filename
    """

    def __init__(self) -> None:
        self.road_user_type: Optional[str] = None
        self.event_type: Optional[EventType] = None
        self.direction_vector: Optional[DirectionVector2D] = None
        self.event_coordinate: Optional[ImageCoordinate] = None
        self.section_id: Optional[SectionId] = None
        self.interpolated_occurrence: Optional[datetime] = None
        self.interpolated_event_coordinate: Optional[ImageCoordinate] = None

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
            ImproperFormattedFilename: if the name is not formatted as expected, an
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
        """Add a section id to the event to be built.

        Args:
            section_id (SectionId): the section id
        """
        self.section_id = section_id

    def add_interpolated_occurrence(self, occurrence: datetime) -> None:
        self.interpolated_occurrence = occurrence

    def add_interpolated_event_coordinate(self, x: float, y: float) -> None:
        self.interpolated_event_coordinate = ImageCoordinate(x, y)


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
            IncompleteEventBuilderSetup: attribute 'interpolated_occurrence' is not set
            IncompleteEventBuilderSetup: attribute 'interpolated_event_coordinate' is
                not set


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

        if self.interpolated_occurrence is None:
            raise IncompleteEventBuilderSetup(
                "attribute 'interpolated_occurrence' is not set"
            )

        if self.interpolated_event_coordinate is None:
            raise IncompleteEventBuilderSetup(
                "attribute 'interpolated_event_coordinate' is not set"
            )

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
            interpolated_occurrence=self.interpolated_occurrence,
            interpolated_event_coordinate=self.interpolated_event_coordinate,
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
            interpolated_occurrence=detection.occurrence,
            interpolated_event_coordinate=self.event_coordinate,
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
        self._events: dict[SectionId, dict[str, list[Event]]] = defaultdict(
            lambda: defaultdict(list)
        )
        self._non_section_events: dict[str, list[Event]] = defaultdict(list)

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
        self.__discard_duplicates([event])
        self.__sort([event])
        self._subject.notify(EventRepositoryEvent([event], []))

    def __do_add(self, event: Event) -> None:
        """
        Internal add method that does not notify observers.
        """
        if event.section_id:
            self._events[event.section_id][event.road_user_id].append(event)
        else:
            self._non_section_events[event.road_user_id].append(event)

    def __discard_duplicates(self, change_events: Iterable[Event]) -> None:
        """Discard duplicate events in repository."""

        for event in change_events:
            if section_id := event.section_id:
                self.__discard_section_event_duplicates_for(
                    event.road_user_id, section_id
                )
            else:
                self.__discard_non_section_event_duplicates_for(event.road_user_id)

    def __discard_section_event_duplicates_for(
        self, road_user_id: str, section_id: SectionId
    ) -> None:
        """Discard duplicate section events in repository."""
        if track_dict := self._events.get(section_id):
            if events := track_dict.get(road_user_id):
                track_dict[road_user_id] = self.__remove_duplicates(events)

    def __discard_non_section_event_duplicates_for(self, road_user_id: str) -> None:
        """Discard duplicate non section events in repository."""
        if events := self._non_section_events.get(road_user_id):
            self._non_section_events[road_user_id] = self.__remove_duplicates(events)

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
            self._events[section]
        self.__discard_duplicates(events)
        self.__sort(events)
        self._subject.notify(EventRepositoryEvent(events, []))

    @staticmethod
    def comparator(event: Event) -> datetime:
        return event.occurrence

    def __sort(self, change_events: Iterable[Event]) -> None:
        for event in change_events:
            if section_id := event.section_id:
                self.__sort_section_events_for(event.road_user_id, section_id)
            else:
                self.__sort_non_section_events_for(event.road_user_id)

    def __sort_section_events_for(
        self, road_user_id: str, section_id: SectionId
    ) -> None:
        if track_dict := self._events.get(section_id):
            if events := track_dict.get(road_user_id):
                self._events[section_id][road_user_id] = sorted(
                    events, key=self.comparator
                )

    def __sort_non_section_events_for(self, road_user_id: str) -> None:
        if events := self._non_section_events.get(road_user_id, []):
            self._non_section_events[road_user_id] = sorted(events, key=self.comparator)

    def get_all(self) -> Iterable[Event]:
        """Get all events stored in the repository.

        Returns:
            Iterable[Event]: the events
        """

        return list(
            itertools.chain(
                self.get_non_section_events_iterator(),
                self.get_section_events_iterator(),
            )
        )

    def get_section_events_iterator(self) -> Iterator[Event]:
        return (
            event
            for events_by_section in self._events.values()
            for events_by_id in events_by_section.values()
            for event in events_by_id
        )

    def get_non_section_events_iterator(self) -> Iterator[Event]:
        return (
            event
            for track_dict in self._non_section_events.values()
            for event in track_dict
        )

    def clear(self) -> None:
        """
        Clear the repository and notify observers only if repository was filled.
        """
        if self._events or self._non_section_events:  # also clear non section events
            removed = list(self.get_all())
            self._events = defaultdict(lambda: defaultdict(list))
            self._non_section_events = defaultdict(list)
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
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        sections: Sequence[SectionId] | None = None,
        event_types: Sequence[EventType] | None = None,
    ) -> Iterable[Event]:
        if event_types is None:
            event_types = []
        if sections is None:
            sections = []
        type_filter = self.__create_type_filter(event_types)
        start_filter = self.__create_start_filter(start_date)
        end_filter = self.__create_end_filter(end_date)
        events = self.__create_event_list(sections)
        return list(
            filter(start_filter, filter(end_filter, filter(type_filter, events)))
        )

    def __create_event_list(self, sections: Sequence[SectionId]) -> Iterable[Event]:
        if sections:
            return list(
                (
                    event
                    for section in sections
                    for events_by_id in self._events[section].values()
                    for event in events_by_id
                )
            )
        return self.get_all()

    def remove_events_by_road_user_ids(self, road_user_ids: Iterable[TrackId]) -> None:
        """
        Removes events associated with the specified road user IDs.

        This method iterates through the provided iterable of road user IDs to delete
        both non-section and section events related to each ID. After removal, it
        notifies the subscribers with the updated information about the removed events.

        Args:
            road_user_ids: An iterable of strings representing the IDs of road users
                whose events are to be removed.

        Returns:
            None
        """
        removed = []
        for road_user_id in road_user_ids:
            removed.extend(
                self.__remove_non_section_events_by_road_user_id(road_user_id.id)
            )
            removed.extend(
                self.__remove_section_events_by_road_user_id(road_user_id.id)
            )

        self._subject.notify((EventRepositoryEvent([], removed)))

    def __remove_section_events_by_road_user_id(self, road_user_id: str) -> list[Event]:
        """
        Removes all events associated with a specific road user ID from the internal
        event tracking structure.

        This method iterates through the internal events dictionary, identifies and
        removes entries corresponding to the given road user ID. Any removed events
        associated with the specified ID are collected and returned as a list.

        Args:
            road_user_id (str): The unique identifier of the road user whose events
                should be removed.

        Returns:
            list[Event]: A list of Event objects that were associated with the given
                road user ID and have been removed.
        """
        removed = []
        for track_dict in self._events.values():
            if ids_to_remove := track_dict.get(road_user_id):
                removed.extend(ids_to_remove)
                del track_dict[road_user_id]
        return removed

    def __remove_non_section_events_by_road_user_id(
        self, road_user_id: str
    ) -> list[Event]:
        """
        Removes non-section events associated with a specific road user ID.

        This method retrieves and removes any non-section events linked to the given
        road user ID from an internal data structure. The removed events are returned
        as a list.

        Args:
            road_user_id (str): The identifier for the road user whose non-section
                events are to be removed.

        Returns:
            list[Event]: A list of removed non-section events associated with the
                provided road user ID.
        """
        removed = []
        if non_section_events := self._non_section_events.get(road_user_id):
            removed.extend(non_section_events)
            del self._non_section_events[road_user_id]
        return removed

    @staticmethod
    def __create_type_filter(
        event_types: Sequence[EventType],
    ) -> Callable[[Event], bool]:
        if event_types:
            return lambda actual: actual.event_type in event_types
        return lambda event: True

    @staticmethod
    def __create_start_filter(start_date: datetime | None) -> Callable[[Event], bool]:
        if start_date:
            return after_filter(start_date)
        return lambda event: True

    @staticmethod
    def __create_end_filter(end_date: datetime | None) -> Callable[[Event], bool]:
        if end_date:
            return before_filter(end_date)
        return lambda event: True


def after_filter(date: datetime) -> Callable[[Event], bool]:
    return lambda actual: actual.occurrence >= date


def before_filter(date: datetime) -> Callable[[Event], bool]:
    return lambda actual: actual.occurrence <= date
