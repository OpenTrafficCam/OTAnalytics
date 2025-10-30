from multiprocessing import Pool
from typing import Callable, Iterable, Sequence

from OTAnalytics.application.config import DEFAULT_NUM_PROCESSES
from OTAnalytics.application.logger import logger
from OTAnalytics.domain.event import EventDataset, PythonEventDataset
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
        intersect: Callable[[TrackDataset, Iterable[Section]], EventDataset],
        tasks: Sequence[tuple[TrackDataset, Iterable[Section]]],
    ) -> EventDataset:
        logger().debug(
            f"Start intersection in parallel with {self._num_processes} processes."
        )
        if self._num_processes > 1:
            with Pool(processes=self._num_processes) as pool:
                event_datasets = pool.starmap(intersect, tasks)
        else:
            event_datasets = [intersect(tracks, sections) for tracks, sections in tasks]

        return self._combine_event_datasets(event_datasets)

    def _combine_event_datasets(
        self, event_datasets: Iterable[EventDataset]
    ) -> EventDataset:
        combined = PythonEventDataset()
        for dataset in event_datasets:
            combined.extend(dataset)
        return combined
