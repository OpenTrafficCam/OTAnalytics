from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable, Optional

from OTAnalytics.domain.event import Event
from OTAnalytics.domain.track import Track


@dataclass(frozen=True)
class Coordinate:
    x: float
    y: float


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
