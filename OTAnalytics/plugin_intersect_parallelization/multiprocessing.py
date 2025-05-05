import itertools
from multiprocessing import Pool
from typing import Callable, Iterable, Sequence

from OTAnalytics.application.config import DEFAULT_NUM_PROCESSES
from OTAnalytics.application.logger import logger
from OTAnalytics.domain.event import Event
from OTAnalytics.domain.intersect import IntersectParallelizationStrategy
from OTAnalytics.domain.section import Section
from OTAnalytics.domain.track_dataset.track_dataset import TrackDataset


class MultiprocessingIntersectParallelization(IntersectParallelizationStrategy):
    """Executes the intersection of tracks and sections in parallel if num_processes
    is greater than 1. Otherwise, executes sequentially"""

    def __init__(self, num_processes: int = DEFAULT_NUM_PROCESSES):
        self._validate_num_processes(num_processes)
        self._num_processes = num_processes

    @property
    def num_processes(self) -> int:
        return self._num_processes

    def _validate_num_processes(self, value: int) -> None:
        if value < 1:
            raise ValueError("Number of processes must be greater than zero.")

    def set_num_processes(self, value: int) -> None:
        self._validate_num_processes(value)
        self._num_processes = value

    def execute(
        self,
        intersect: Callable[[TrackDataset, Iterable[Section]], Iterable[Event]],
        tasks: Sequence[tuple[TrackDataset, Iterable[Section]]],
    ) -> list[Event]:
        logger().debug(
            f"Start intersection in parallel with {self._num_processes} processes."
        )
        if self._num_processes > 1:
            with Pool(processes=self._num_processes) as pool:
                events = pool.starmap(intersect, tasks)
        else:
            events = [intersect(tracks, sections) for tracks, sections in tasks]

        return self._flatten_events(events)

    def _flatten_events(self, events: Iterable[Iterable[Event]]) -> list[Event]:
        return list(itertools.chain.from_iterable(events))
