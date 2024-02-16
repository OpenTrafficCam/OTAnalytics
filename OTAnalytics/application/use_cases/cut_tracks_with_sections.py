from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable

from OTAnalytics.domain.observer import OBSERVER
from OTAnalytics.domain.section import Section, SectionId, SectionListObserver
from OTAnalytics.domain.track import Track, TrackId


@dataclass(frozen=True)
class CutTracksDto:
    """Holds information tracks that have been cut with a section.

    Args:
        section (str): name of the cutting section.
        original_tracks (list[TrackId]): ids of original tracks that have been
            cut.
    """

    section: str
    original_tracks: list[TrackId]


class CutTracksIntersectingSection(SectionListObserver):
    """
    Interface defining the use case to cut tracks intersecting a section and saving
    the cut tracks to the track repository while removing the original tracks.
    """

    @abstractmethod
    def __call__(
        self, cutting_section: Section, preserve_cutting_section: bool = False
    ) -> None:
        """Cut tracks intersecting a section and saving the cut tracks to the track
        repository while removing the original tracks.

        Args:
            cutting_section (Section): the section to cut the tracks with.
            preserve_cutting_section (bool): Whether to preserve or discard
                cutting section after cut. Defaults to False.
        """
        raise NotImplementedError

    @abstractmethod
    def register(self, observer: OBSERVER[CutTracksDto]) -> None:
        """Register to this use case.

        Args:
            observer (OBSERVER[Any]): the observer to listen to this use case.
        """
        raise NotImplementedError

    @abstractmethod
    def notify_section_changed(self, section_id: SectionId) -> None:
        """Observer to listen to section changed events in the section repository.

        Args:
            section_id: id of section that has changed.
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
