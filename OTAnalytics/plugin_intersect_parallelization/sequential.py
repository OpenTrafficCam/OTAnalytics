from typing import Callable, Iterable

from OTAnalytics.domain.event import Event
from OTAnalytics.domain.intersect import IntersectParallelizationStrategy
from OTAnalytics.domain.section import Section
from OTAnalytics.domain.track import Track


class SequentialIntersect(IntersectParallelizationStrategy):
    def execute(
        self,
        intersect: Callable[[Track, Iterable[Section]], Iterable[Event]],
        tracks: Iterable[Track],
        sections: Iterable[Section],
    ) -> list[Event]:
        events: list[Event] = []
        for _track in tracks:
            events.extend(intersect(_track, sections))
        return events
