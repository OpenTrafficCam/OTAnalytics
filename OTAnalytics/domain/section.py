from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Iterable

from OTAnalytics.domain.common import DataclassValidation
from OTAnalytics.domain.geometry import Coordinate

SECTIONS: str = "sections"
ID: str = "id"
TYPE: str = "type"
LINE: str = "line"
START: str = "start"
END: str = "end"
AREA: str = "area"
COORDINATES: str = "coordinates"
PLUGIN_DATA: str = "plugin_data"


@dataclass(frozen=True)
class Section(DataclassValidation):
    """
    A section defines a geometry a coordinate space and is used by traffic detectors to
    create vehicle events.

    Args:
        id (str): the section id.
        plugin_data (dict): data that plugins or prototypes can use which are not
            modelled in the domain layer yet
    """

    id: str
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


@dataclass(frozen=True)
class LineSection(Section):
    """
    A section that is defined by a line.

    Raises:
        ValueError: if start and end point coordinates are the same and therefore
        define a point.

    Args:
        id (str): the section id
        plugin_data (dict[str,any]): data that plugins or prototypes can use which are
            not modelled in the domain layer yet
        start (Coordinate): the start coordinate.
        end (Coordinate): the end coordinate.
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
            ID: self.id,
            TYPE: LINE,
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
        ValueError: if coordinates do not define a closed area.
        ValueError: if the number of coordinates is less than four thus defining an
            invalid area.

    Args:
        id (str): the section id
        plugin_data (dict[str, Any]): data that plugins or prototypes can use which are
            not modelled in the domain layer yet
        coordinates (list[Coordinate]): area defined by list of coordinates.
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
            ID: self.id,
            COORDINATES: [coordinate.to_dict() for coordinate in self.coordinates],
            PLUGIN_DATA: self.plugin_data,
        }


class SectionRepository:
    """Repository used to store sections."""

    def __init__(self) -> None:
        self._sections: dict[str, Section] = {}

    def add(self, section: Section) -> None:
        """Add a section to the repository.

        Args:
            section (Section): the section to add.
        """
        self._sections[section.id] = section

    def add_all(self, sections: Iterable[Section]) -> None:
        """Add several sections at once to the repository.

        Args:
            sections (Iterable[Section]): the sections to add.
        """
        for section in sections:
            self.add(section)

    def get_all(self) -> Iterable[Section]:
        """Get all sections from the repository.

        Returns:
            Iterable[Section]: the sections.
        """
        return self._sections.values()

    def remove(self, section: Section) -> None:
        """Remove section from the repository.

        Args:
            section (Section): the section to be removed.
        """
        del self._sections[section.id]
