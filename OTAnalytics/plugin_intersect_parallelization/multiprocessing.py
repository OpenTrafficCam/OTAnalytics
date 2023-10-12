import itertools
from multiprocessing import Pool
from typing import Callable, Iterable

from OTAnalytics.application.config import DEFAULT_NUM_PROCESSES
from OTAnalytics.application.logger import logger
from OTAnalytics.domain.event import Event
from OTAnalytics.domain.intersect import IntersectParallelizationStrategy
from OTAnalytics.domain.section import Section
from OTAnalytics.domain.track import Track


class MultiprocessingIntersectParallelization(IntersectParallelizationStrategy):
    """Executes the intersection of tracks and sections in parallel."""

    def __init__(self, num_processes: int = DEFAULT_NUM_PROCESSES):
        self._validate_num_processes(num_processes)
        self._num_processes = num_processes

    def _validate_num_processes(self, value: int) -> None:
        if value < 1:
            raise ValueError("Number of processes must be greater than zero.")

    def set_num_processes(self, value: int) -> None:
        self._validate_num_processes(value)
        self._num_processes = value

    def execute(
        self,
        intersect: Callable[[Track, Iterable[Section]], Iterable[Event]],
        tracks: Iterable[Track],
        sections: Iterable[Section],
    ) -> list[Event]:
        logger().debug(
            f"Start intersection in parallel with {self._num_processes} processes."
        )
        with Pool(processes=self._num_processes) as pool:
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
