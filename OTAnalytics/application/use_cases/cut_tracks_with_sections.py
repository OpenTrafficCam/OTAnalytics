from abc import ABC, abstractmethod
from typing import Any, Iterable

from OTAnalytics.domain.observer import OBSERVER
from OTAnalytics.domain.section import Section, SectionListObserver
from OTAnalytics.domain.track import Track, TrackId


class CutTracksIntersectingSection(SectionListObserver):
    """
    Interface defining the use case to cut tracks intersecting a section and saving
    the cut tracks to the track repository while removing the original tracks.
    """

    @abstractmethod
    def __call__(self, cutting_section: Section) -> None:
        """Cut tracks intersecting a section and saving the cut tracks to the track
        repository while removing the original tracks.

        Args:
            cutting_section (Section): the section to cut the tracks with.
        """
        raise NotImplementedError

    @abstractmethod
    def register(self, observer: OBSERVER[Any]) -> None:
        """Register to this use case.

        Args:
            observer (OBSERVER[Any]): the observer to listen to this use case.
        """
        raise NotImplementedError


class CutTracksWithSection(ABC):
    """Interface defining the use case to use section to cut tracks."""

    @abstractmethod
    def __call__(
        self, track_ids: Iterable[TrackId], cutting_section: Section
    ) -> Iterable[Track]:
        """Cut tracks with a cutting section.

        Args:
            cutting_section (Section): the section used for cutting sections.

        Returns:
            Iterable[Track]: the track segments resulting from the cut.
        """
        raise NotImplementedError
