from abc import ABC, abstractmethod
from typing import Iterable

from OTAnalytics.domain.event import Event
from OTAnalytics.domain.section import Section, SectionId
from OTAnalytics.domain.track import TrackId


class RunIntersect(ABC):
    """
    Interface defining the use case to intersect the given tracks with the given
    sections.
    """

    @abstractmethod
    def __call__(self, sections: Iterable[Section]) -> list[Event]:
        raise NotImplementedError
        # bla


class TracksIntersectingSections(ABC):
    @abstractmethod
    def __call__(self, sections: Iterable[Section]) -> dict[SectionId, set[TrackId]]:
        raise NotImplementedError
