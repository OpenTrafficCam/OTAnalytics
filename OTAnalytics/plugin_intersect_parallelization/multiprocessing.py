import itertools
from multiprocessing import Pool
from os import cpu_count
from typing import Callable, Iterable

from OTAnalytics.domain.event import Event
from OTAnalytics.domain.intersect import IntersectParallelizationStrategy
from OTAnalytics.domain.section import Section
from OTAnalytics.domain.track import Track


class MultiprocessingIntersectParallelization(IntersectParallelizationStrategy):
    """Executes the intersection of tracks and sections in parallel."""

    def execute(
        self,
        intersect: Callable[[Track, Iterable[Section]], Iterable[Event]],
        tracks: Iterable[Track],
        sections: Iterable[Section],
    ) -> list[Event]:
        with Pool(processes=cpu_count()) as pool:
            events = pool.starmap(
                intersect,
                zip(
                    tracks,
                    itertools.repeat(sections),
                ),
            )
        return self._flatten_events(events)

    def _flatten_events(self, events: Iterable[Iterable[Event]]) -> list[Event]:
        return list(itertools.chain.from_iterable(events))
