from typing import Callable, Iterable

from OTAnalytics.domain.event import Event
from OTAnalytics.domain.intersect import IntersectParallelizationStrategy
from OTAnalytics.domain.progress import ProgressbarBuilder
from OTAnalytics.domain.section import Section
from OTAnalytics.domain.track import Track


class SequentialIntersect(IntersectParallelizationStrategy):
    """Executes the intersection of tracks and sections in sequential order."""

    def __init__(self, progressbar: ProgressbarBuilder) -> None:
        self._progressbar = progressbar

    def execute(
        self,
        intersect: Callable[[Track, Iterable[Section]], Iterable[Event]],
        tracks: Iterable[Track],
        sections: Iterable[Section],
    ) -> list[Event]:
        events: list[Event] = []
        for _track in self._progressbar(list(tracks), "Intersected tracks: ", "tracks"):
            events.extend(intersect(_track, sections))
        return events
