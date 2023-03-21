from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable, Optional

from OTAnalytics.domain.event import Event
from OTAnalytics.domain.track import Track

SECTIONS: str = "sections"
ID: str = "id"
TYPE: str = "type"
LINE: str = "line"
START: str = "start"
END: str = "end"
X: str = "x"
Y: str = "y"
AREA: str = "area"
COORDINATES: str = "coordinates"


@dataclass(frozen=True)
class Coordinate:
    """
    Models points in the image as x-y coordinates.
    """

    x: float
    y: float

    def to_dict(self) -> dict:
        return {
            X: self.x,
            Y: self.y,
        }


@dataclass(frozen=True)
class Section(ABC):
    """
    Sections define virtual detectors to generate vehicle events.
    """

    id: str

    @abstractmethod
    def enter(self, track: Track) -> Optional[Event]:
        """
        Generates an event if the track enters the section.

        Args:
            track (Track): track to intersect with the section

        Returns:
            Optional[Event]: event if the track enters the section
        """
        pass

    @abstractmethod
    def leave(self, track: Track) -> Optional[Event]:
        """
        Generates an event if the track leaves the section.

        Args:
            track (Track): track to intersect with the section

        Returns:
            Optional[Event]: event if the track leaves the section
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


@dataclass(frozen=True)
class LineSection(Section):
    """
    Section defined as line.
    """

    start: Coordinate
    end: Coordinate

    def enter(self, track: Track) -> Optional[Event]:
        """
        Generates an event for the first time the track crosses the line.
        """
        return None

    def leave(self, track: Track) -> Optional[Event]:
        """
        Generates an event for the last time the track crosses the line.
        """
        return None

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
        }


@dataclass(frozen=True)
class Area(Section):
    coordinates: list[Coordinate]

    def enter(self, track: Track) -> Optional[Event]:
        """
        Generates an event for the first point of the track which enters the area.
        """
        return None

    def leave(self, track: Track) -> Optional[Event]:
        """
        Generates an event for the last point of the track which leaves the area.
        """
        return None

    def to_dict(self) -> dict:
        """
        Convert section into dict to interact with other parts of the system,
        e.g. serialization.
        """
        return {
            TYPE: AREA,
            ID: self.id,
            COORDINATES: [coordinate.to_dict() for coordinate in self.coordinates],
        }


class SectionRepository:
    def __init__(self) -> None:
        self._sections: dict[str, Section] = {}

    def add(self, section: Section) -> None:
        self._sections[section.id] = section

    def add_all(self, sections: Iterable[Section]) -> None:
        for section in sections:
            self.add(section)

    def get_all(self) -> Iterable[Section]:
        return self._sections.values()

    def remove(self, section: Section) -> None:
        del self._sections[section.id]
