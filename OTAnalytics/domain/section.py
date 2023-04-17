from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Iterable, Optional

from OTAnalytics.domain.common import DataclassValidation
from OTAnalytics.domain.geometry import Coordinate, RelativeOffsetCoordinate
from OTAnalytics.domain.types import EventType

SECTIONS: str = "sections"
ID: str = "id"
TYPE: str = "type"
LINE: str = "line"
START: str = "start"
END: str = "end"
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


class SectionObserver(ABC):
    """
    Interface to listen to changes of a single section.
    """

    @abstractmethod
    def notify_section(self, section_id: Optional[SectionId]) -> None:
        """
        Notifies that the section of the given id has changed.

        Args:
            track_id (Optional[SectionId]): id of the changed section
        """
        pass


class SectionSubject:
    """
    Helper class to handle and notify observers
    """

    def __init__(self) -> None:
        self.observers: set[SectionObserver] = set()

    def register(self, observer: SectionObserver) -> None:
        """
        Listen to events.

        Args:
            observer (SectionObserver): listener to add
        """
        self.observers.add(observer)

    def notify(self, section_id: Optional[SectionId]) -> None:
        """
        Notifies observers about the section id.

        Args:
            track_id (Optional[SectionId]): id of the changed section
        """
        [observer.notify_section(section_id) for observer in self.observers]


class SectionListSubject:
    """
    Helper class to handle and notify observers
    """

    def __init__(self) -> None:
        self.observers: set[SectionListObserver] = set()

    def register(self, observer: SectionListObserver) -> None:
        """
        Listen to events.

        Args:
            observer (SectionListObserver): listener to add
        """
        self.observers.add(observer)

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
    plugin_data: dict[str, Any]

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

    start: Coordinate
    end: Coordinate

    def _validate(self) -> None:
        if self.start == self.end:
            raise ValueError(
                (
                    "Start and end point of coordinate must be different to be a line, "
                    "but are same"
                )
            )

    def to_dict(self) -> dict:
        """
        Convert section into dict to interact with other parts of the system,
        e.g. serialization.
        """
        return {
            ID: self.id.serialize(),
            TYPE: LINE,
            RELATIVE_OFFSET_COORDINATES: self._serialize_relative_offset_coordinates(),
            START: self.start.to_dict(),
            END: self.end.to_dict(),
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


class SectionRepository:
    """Repository used to store sections."""

    def __init__(self) -> None:
        self._sections: dict[SectionId, Section] = {}
        self.observers: SectionListSubject = SectionListSubject()

    def register_sections_observer(self, observer: SectionListObserver) -> None:
        self.observers.register(observer)

    def add(self, section: Section) -> None:
        """Add a section to the repository.

        Args:
            section (Section): the section to add
        """
        self._add(section)
        self.observers.notify([section.id])

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
        self.observers.notify([section.id for section in sections])

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

    def update(self, section: Section) -> None:
        """Update the section in the repository.

        Args:
            section (Section): updated section
        """
        self._sections[section.id] = section
