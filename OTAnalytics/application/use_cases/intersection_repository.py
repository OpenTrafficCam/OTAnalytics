from typing import Iterable

from OTAnalytics.application.use_cases.highlight_intersections import (
    IntersectionRepository,
)
from OTAnalytics.domain.section import (
    SectionId,
    SectionListObserver,
    SectionRepositoryEvent,
)
from OTAnalytics.domain.track_repository import TrackListObserver, TrackRepositoryEvent


class ClearAllIntersections(SectionListObserver, TrackListObserver):
    """Clears the event repository also on section state changes.

    Args:
        intersection_repository (EventRepository): the event repository
    """

    def __init__(self, intersection_repository: IntersectionRepository) -> None:
        self._intersection_repository = intersection_repository

    def clear(self) -> None:
        self._intersection_repository.clear()

    def remove(self, sections: Iterable[SectionId]) -> None:
        self._intersection_repository.remove(set(sections))

    def notify_sections(self, section_event: SectionRepositoryEvent) -> None:
        self.remove(section_event.removed)

    def notify_tracks(self, track_event: TrackRepositoryEvent) -> None:
        self._intersection_repository.clear()

    def on_section_changed(self, section_id: SectionId) -> None:
        self.remove([section_id])
