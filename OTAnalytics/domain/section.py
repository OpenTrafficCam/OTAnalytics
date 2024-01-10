from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Iterable, Optional, TypeVar

from OTAnalytics.application.config import CUTTING_SECTION_MARKER
from OTAnalytics.domain.common import DataclassValidation
from OTAnalytics.domain.geometry import Coordinate, RelativeOffsetCoordinate
from OTAnalytics.domain.observer import Subject
from OTAnalytics.domain.types import EventType

SECTIONS: str = "sections"
ID: str = "id"
NAME: str = "name"
TYPE: str = "type"
LINE: str = "line"
AREA: str = "area"
CUTTING: str = "cutting"
COORDINATES: str = "coordinates"
RELATIVE_OFFSET_COORDINATES: str = "relative_offset_coordinates"
PLUGIN_DATA: str = "plugin_data"

T = TypeVar("T")


class SectionType(Enum):
    AREA = AREA
    LINE = LINE
    CUTTING = CUTTING


@dataclass(frozen=True)
class SectionId:
    id: str

    def serialize(self) -> str:
        return self.id


@dataclass
class SectionRepositoryEvent:
    """Holds information on changes made in the event repository.

    `Added` holding an empty iterable indicates remove events.

    Args:
        added (Iterable[Event]): events added to repository.
        removed (Iterable[Event]): events removed from the repository.
    """

    added: Iterable[SectionId]
    removed: Iterable[SectionId]

    @staticmethod
    def create_added(sections: list[SectionId]) -> "SectionRepositoryEvent":
        return SectionRepositoryEvent(sections, [])

    @staticmethod
    def create_removed(sections: list[SectionId]) -> "SectionRepositoryEvent":
        return SectionRepositoryEvent([], sections)


class SectionListObserver(ABC):
    """
    Interface to listen to changes to a list of sections.
    """

    @abstractmethod
    def notify_sections(self, sections: SectionRepositoryEvent) -> None:
        """
        Notifies that the given sections have been added.

        Args:
            sections (list[SectionId]): list of added sections
        """
        pass


SectionChangedObserver = Callable[[SectionId], None]


class SectionListSubject:
    """
    Helper class to handle and notify observers
    """

    def __init__(self) -> None:
        self.observers: list[SectionListObserver] = []

    def register(self, observer: SectionListObserver) -> None:
        """
        Listen to events.

        Args:
            observer (SectionListObserver): listener to add
        """
        self.observers.append(observer)

    def notify(self, sections: SectionRepositoryEvent) -> None:
        """
        Notifies observers about the list of sections.

        Args:
            sections (list[SectionId]): list of added sections
        """
        [observer.notify_sections(sections) for observer in self.observers]


@dataclass(frozen=True)
class Section(DataclassValidation):
    """
    A section defines a geometry a coordinate space and is used by traffic detectors to
    create vehicle events.

    Args:
        id (SectionId): the section id
        relative_offset_coordinates (list[RelativeOffsetCoordinate]): used to determine
            which coordinates of a track to build the geometry to intersect
        plugin_data (dict): data that plugins or prototypes can use which are not
            modelled in the domain layer yet
    """

    id: SectionId
    name: str
    relative_offset_coordinates: dict[EventType, RelativeOffsetCoordinate]
    plugin_data: dict[str, Any]

    @abstractmethod
    def get_coordinates(self) -> list[Coordinate]:
        """
        Returns a list of all coordinates of this section.

        Returns:
            list[Coordinate]: all coordinates of this section
        """
        raise NotImplementedError

    @abstractmethod
    def update_coordinates(self, coordinates: list[Coordinate]) -> None:
        """
        Updates the coordinates of this section.

        Args:
            coordinates (list[Coordinate]): new coordinates of the section
        """
        raise NotImplementedError

    @abstractmethod
    def to_dict(self) -> dict:
        """
        Convert section into dict to interact with other parts of the system,
        e.g. serialization.

        Returns:
            dict: serialized section
        """
        raise NotImplementedError

    @abstractmethod
    def get_type(self) -> SectionType:
        """Get type of this section.

        Returns:
            SectionType: this sections type.

        """
        raise NotImplementedError

    def get_offset(self, event_type: EventType) -> RelativeOffsetCoordinate:
        """Get this sections relative offset coordinate for event type if defined.

        Args:
            event_type (EventType): the event type.

        Returns:
            RelativeOffsetCoordinate | None: the offset. Otherwise, None.

        """
        return self.relative_offset_coordinates.get(
            event_type, RelativeOffsetCoordinate(0, 0)
        )

    def _serialize_relative_offset_coordinates(self) -> dict[str, dict]:
        """Serializes this class' `relative_offset_coordinates` value to a dict.

        Here is an example of the serialized data that can be returned:
        ```python
        {
            "section-enter": {
                "x": 0,
                "y": 0
            },
            "section-leave": {
                "x": 0.5,
                "y": 0.5
            },
        }
        ```

        Returns:
            dict[str, dict]: the serialized `relative_coordinate_offsets` value
        """
        return {
            event_type.serialize(): offset.to_dict()
            for event_type, offset in self.relative_offset_coordinates.items()
        }


@dataclass(frozen=True)
class LineSection(Section):
    """
    A section that is defined by a line.

    If the section name starts with `CUTTING_SECTION_MARKER` this section will become
    a cutting section.

    Raises:
        ValueError: number of coordinates defining this section must be greater equal
            two.
        ValueError: if start and end point coordinates are the same and therefore
            define a point.

    Args:
        id (str): the section id.
        name (str): the section name.
        relative_offset_coordinates (list[RelativeOffsetCoordinate]): used to determine
            which coordinates of a track to build the geometry to intersect.
        plugin_data (dict[str,any]): data that plugins or prototypes can use which are
            not modelled in the domain layer yet
        coordinates (list[Coordinate]): the coordinates defining the section geometry.
    """

    coordinates: list[Coordinate]

    def _validate(self) -> None:
        self.__validate_coordinates(self.coordinates)

    def __validate_coordinates(self, coordinates: list[Coordinate]) -> None:
        if len(coordinates) < 2:
            raise ValueError(
                "The number of coordinates to make up a line must be greater equal 2, "
                f"but is {len(self.coordinates)}"
            )

        if coordinates[0] == coordinates[-1]:
            raise ValueError(
                (
                    "Start and end point of coordinate must be different to be a line, "
                    "but are same"
                )
            )

    def get_coordinates(self) -> list[Coordinate]:
        return self.coordinates.copy()

    def update_coordinates(self, coordinates: list[Coordinate]) -> None:
        self.__validate_coordinates(coordinates)
        self.coordinates.clear()
        self.coordinates.extend(coordinates)

    def to_dict(self) -> dict:
        """
        Convert section into dict to interact with other parts of the system,
        e.g. serialization.
        """
        return {
            ID: self.id.serialize(),
            NAME: self.name,
            TYPE: self.get_type().value,
            RELATIVE_OFFSET_COORDINATES: self._serialize_relative_offset_coordinates(),
            COORDINATES: [coordinate.to_dict() for coordinate in self.coordinates],
            PLUGIN_DATA: self.plugin_data,
        }

    def get_type(self) -> SectionType:
        """Get this sections type.

        Returns:
            SectionType: this sections type.

        """
        if self._is_cutting_section():
            return SectionType.CUTTING

        return SectionType.LINE

    def _is_cutting_section(self) -> bool:
        return self.name.startswith(CUTTING_SECTION_MARKER)


@dataclass(frozen=True)
class Area(Section):
    """
    A section that is defined by a polygon.

    An area is defined by `[x1, x2, x3 ..., x_n]` a list of coordinates
    where n is a natural number and `x1 = x_n`.

    Raises:
        ValueError: if coordinates do not define a closed area
        ValueError: if the number of coordinates is less than four thus defining an
            invalid area

    Args:
        id (str): the section id
        relative_offset_coordinates (list[RelativeOffsetCoordinate]): used to determine
            which coordinates of a track to build the geometry to intersect
        plugin_data (dict[str, Any]): data that plugins or prototypes can use which are
            not modelled in the domain layer yet
        coordinates (list[Coordinate]): area defined by list of coordinates
    """

    coordinates: list[Coordinate]

    def _validate(self) -> None:
        self.__validate_coordinates(self.coordinates)

    def __validate_coordinates(self, coordinates: list[Coordinate]) -> None:
        if len(coordinates) < 4:
            raise ValueError(
                (
                    "Number of coordinates to define a valid area must be "
                    f"greater equal four, but is {len(self.coordinates)}"
                )
            )

        if coordinates[0] != coordinates[-1]:
            raise ValueError("Coordinates do not define a closed area")

    def get_coordinates(self) -> list[Coordinate]:
        return self.coordinates.copy()

    def update_coordinates(self, coordinates: list[Coordinate]) -> None:
        self.__validate_coordinates(coordinates)
        self.coordinates.clear()
        self.coordinates.extend(coordinates)

    def to_dict(self) -> dict:
        """
        Convert section into dict to interact with other parts of the system,
        e.g. serialization.
        """
        return {
            TYPE: self.get_type().value,
            ID: self.id.serialize(),
            NAME: self.name,
            RELATIVE_OFFSET_COORDINATES: self._serialize_relative_offset_coordinates(),
            COORDINATES: [coordinate.to_dict() for coordinate in self.coordinates],
            PLUGIN_DATA: self.plugin_data,
        }

    def get_type(self) -> SectionType:
        return SectionType.AREA


class MissingSection(Exception):
    pass


class SectionRepository:
    """Repository used to store sections."""

    def __init__(self) -> None:
        self._sections: dict[SectionId, Section] = {}
        self._current_id = 0
        self._repository_content_observers: SectionListSubject = SectionListSubject()
        self._section_content_observers: Subject[SectionId] = Subject[SectionId]()

    def register_sections_observer(self, observer: SectionListObserver) -> None:
        self._repository_content_observers.register(observer)

    def register_section_changed_observer(
        self, observer: SectionChangedObserver
    ) -> None:
        self._section_content_observers.register(observer)

    def get_id(self) -> SectionId:
        self._current_id += 1
        candidate = SectionId(str(self._current_id))
        return self.get_id() if candidate in self._sections.keys() else candidate

    def add(self, section: Section) -> None:
        """Add a section to the repository.

        Args:
            section (Section): the section to add
        """
        self._add(section)
        self._repository_content_observers.notify(
            SectionRepositoryEvent.create_added([section.id])
        )

    def _add(self, section: Section) -> None:
        """Internal method to add sections without notifying observers.

        Args:
            section (Section): the section to be added
        """
        self._sections[section.id] = section

    def add_all(self, sections: Iterable[Section]) -> None:
        """Add several sections at once to the repository.

        Args:
            sections (Iterable[Section]): the sections to add
        """
        for section in sections:
            self._add(section)
        self._repository_content_observers.notify(
            SectionRepositoryEvent.create_added([section.id for section in sections])
        )

    def get_all(self) -> list[Section]:
        """Get all sections from the repository.

        Returns:
            Iterable[Section]: the sections
        """
        return list(self._sections.values())

    def get(self, id: SectionId) -> Optional[Section]:
        """Get the section for the given id or nothing, if the id is missing.

        Args:
            id (SectionId): id to get section for

        Returns:
            Optional[Section]: section if present
        """
        return self._sections.get(id)

    def get_section_ids(self) -> Iterable[SectionId]:
        """Get all section ids used in repository.

        Returns:
            Iterable[SectionId]: the section ids.
        """
        return self._sections.keys()

    def remove(self, section: SectionId) -> None:
        """Remove section from the repository.

        Args:
            section (Section): the section to be removed
        """
        del self._sections[section]
        self._repository_content_observers.notify(
            SectionRepositoryEvent.create_removed([section])
        )

    def update(self, section: Section) -> None:
        """Update the section in the repository.

        Args:
            section (Section): updated section
        """
        self._sections[section.id] = section
        self._section_content_observers.notify(section.id)

    def set_section_plugin_data(self, section_id: SectionId, plugin_data: dict) -> None:
        """
        Set the plugin data of the section. The data will be overridden.

        Args:
            section_id (SectionId): section id to override the plugin data at
            plugin_data (dict): value of the new plugin data
        """
        section = self.get(section_id)
        if section is None:
            raise MissingSection(f"Section for id: {section_id} could not be found.")
        section.plugin_data.clear()
        section.plugin_data.update(plugin_data)
        self._section_content_observers.notify(section_id)

    def clear(self) -> None:
        """
        Clear the repository and inform the observers about the empty repository.
        """
        removed = list(self._sections.keys())
        self._sections.clear()
        self._repository_content_observers.notify(
            SectionRepositoryEvent.create_removed(removed)
        )
