from typing import Callable, Iterable

from OTAnalytics.domain.event import Event
from OTAnalytics.domain.intersect import (
    IntersectImplementation,
    IntersectParallelizationStrategy,
)
from OTAnalytics.domain.section import Section
from OTAnalytics.domain.track import Track


class SequentialIntersect(IntersectParallelizationStrategy):
    """Executes the intersection of tracks and sections in sequential order."""

    def execute(
        self,
        intersect: Callable[
            [Track, Iterable[Section], IntersectImplementation, Callable[[int], None]],
            Iterable[Event],
        ],
        tracks: Iterable[Track],
        sections: Iterable[Section],
        intersect_implementation: IntersectImplementation,
        update_progress: Callable[[int], None],
    ) -> list[Event]:
        events: list[Event] = []
        for _track in list(tracks):
            events.extend(
                intersect(_track, sections, intersect_implementation, update_progress)
            )
        return events
