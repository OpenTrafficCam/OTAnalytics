from abc import ABC, abstractmethod
from typing import Iterable

from OTAnalytics.domain.section import CuttingSection
from OTAnalytics.domain.track import Track, TrackId


class CutTracksIntersectingSection:
    """
    Interface defining the use case to cut tracks intersecting a section and saving
    the cut tracks to the track repository while removing the original tracks.
    """

    @abstractmethod
    def __call__(self, cutting_section: CuttingSection) -> None:
        """Cut tracks intersecting a section and saving the cut tracks to the track
        repository while removing the original tracks.

        Args:
            cutting_section (CuttingSection): the section to cut the tracks with.
        """
        pass


class CutTracksWithSection(ABC):
    """Interface defining the use case to use section to cut tracks."""

    @abstractmethod
    def __call__(
        self, track_ids: Iterable[TrackId], cutting_section: CuttingSection
    ) -> Iterable[Track]:
        """Cut tracks with a cutting section.

        Args:
            cutting_section (CuttingSection): the section used for cutting sections.

        Returns:
            Iterable[Track]: the track segments resulting from the cut.
        """
        raise NotImplementedError
