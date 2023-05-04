from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, Generic, Iterable, Optional, TypeVar

from OTAnalytics.domain.common import DataclassValidation
from OTAnalytics.domain.geometry import Coordinate, RelativeOffsetCoordinate
from OTAnalytics.domain.types import EventType

SECTIONS: str = "sections"
ID: str = "id"
TYPE: str = "type"
LINE: str = "line"
AREA: str = "area"
COORDINATES: str = "coordinates"
RELATIVE_OFFSET_COORDINATES: str = "relative_offset_coordinates"
PLUGIN_DATA: str = "plugin_data"


@dataclass(frozen=True)
class SectionId:
    id: str

    def serialize(self) -> str:
        return self.id


class SectionListObserver(ABC):
    """
    Interface to listen to changes to a list of sections.
    """

    @abstractmethod
    def notify_sections(self, sections: list[SectionId]) -> None:
        """
        Notifies that the given sections have been added.

        Args:
            sections (list[SectionId]): list of added sections
        """
        pass


VALUE = TypeVar("VALUE")


SectionChangedObserver = Callable[[SectionId], None]


class SectionChangedSubject(Generic[VALUE]):
    """
    Helper class to handle and notify observers
    """

    def __init__(self) -> None:
        self.observers: set[SectionChangedObserver] = set()

    def register(self, observer: SectionChangedObserver) -> None:
        """
        Listen to events.

        Args:
            observer (SectionChangedObserver): listener to add
        """
        self.observers.add(observer)

    def notify(self, value: SectionId) -> None:
        """
        Notifies observers about the changed value.

        Args:
            value (SectionId): changed value
        """
        [observer(value) for observer in self.observers]


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

    def notify(self, sections: list[SectionId]) -> None:
        """
        Notifies observers about the list of sections.

        Args:
            tracks (list[SectionId]): list of added sections
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
    relative_offset_coordinates: dict[EventType, RelativeOffsetCoordinate]
    plugin_data: dict[str, dict]

    @abstractmethod
    def get_coordinates(self) -> list[Coordinate]:
        """
        Returns a list of all coordinates of this section.

        Returns:
            list[Coordinate]: all coordinates of this section
        """
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        """
        Convert section into dict to interact with other parts of the system,
        e.g. serialization.

        Returns:
            dict: serialized section
        """
        pass

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

    Raises:
        ValueError: if start and end point coordinates are the same and therefore
        define a point.

    Args:
        id (str): the section id
        relative_offset_coordinates (list[RelativeOffsetCoordinate]): used to determine
            which coordinates of a track to build the geometry to intersect
        plugin_data (dict[str,any]): data that plugins or prototypes can use which are
            not modelled in the domain layer yet
        start (Coordinate): the start coordinate
        end (Coordinate): the end coordinate
    """

    coordinates: list[Coordinate]

    def _validate(self) -> None:
        if len(self.coordinates) < 2:
            raise ValueError(
                "The number of coordinates to make up a line must be greater equal 2, "
                f"but is {len(self.coordinates)}"
            )

        if self.coordinates[0] == self.coordinates[-1]:
            raise ValueError(
                (
                    "Start and end point of coordinate must be different to be a line, "
                    "but are same"
                )
            )

    def get_coordinates(self) -> list[Coordinate]:
        return self.coordinates.copy()

    def to_dict(self) -> dict:
        """
        Convert section into dict to interact with other parts of the system,
        e.g. serialization.
        """
        return {
            ID: self.id.serialize(),
            TYPE: LINE,
            RELATIVE_OFFSET_COORDINATES: self._serialize_relative_offset_coordinates(),
            COORDINATES: [coordinate.to_dict() for coordinate in self.coordinates],
            PLUGIN_DATA: self.plugin_data,
        }


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
        if len(self.coordinates) < 4:
            raise ValueError(
                (
                    "Number of coordinates to define a valid area must be "
                    f"greater equal four, but is {len(self.coordinates)}"
                )
            )

        if self.coordinates[0] != self.coordinates[-1]:
            raise ValueError("Coordinates do not define a closed area")

    def get_coordinates(self) -> list[Coordinate]:
        return self.coordinates.copy()

    def to_dict(self) -> dict:
        """
        Convert section into dict to interact with other parts of the system,
        e.g. serialization.
        """
        return {
            TYPE: AREA,
            ID: self.id.serialize(),
            RELATIVE_OFFSET_COORDINATES: self._serialize_relative_offset_coordinates(),
            COORDINATES: [coordinate.to_dict() for coordinate in self.coordinates],
            PLUGIN_DATA: self.plugin_data,
        }


class MissingSection(Exception):
    pass


class SectionRepository:
    """Repository used to store sections."""

    def __init__(self) -> None:
        self._sections: dict[SectionId, Section] = {}
        self._repository_content_observers: SectionListSubject = SectionListSubject()
        self._section_content_observers: SectionChangedSubject = SectionChangedSubject()

    def register_sections_observer(self, observer: SectionListObserver) -> None:
        self._repository_content_observers.register(observer)

    def register_section_changed_observer(
        self, observer: SectionChangedObserver
    ) -> None:
        self._section_content_observers.register(observer)

    def add(self, section: Section) -> None:
        """Add a section to the repository.

        Args:
            section (Section): the section to add
        """
        self._add(section)
        self._repository_content_observers.notify([section.id])

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
        self._repository_content_observers.notify([section.id for section in sections])

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

    def remove(self, section: SectionId) -> None:
        """Remove section from the repository.

        Args:
            section (Section): the section to be removed
        """
        del self._sections[section]
        self._repository_content_observers.notify([section])

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
