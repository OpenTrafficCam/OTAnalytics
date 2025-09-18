from typing import Callable, Iterable, Sequence

from OTAnalytics.domain.event import EventDataset, PythonEventDataset
from OTAnalytics.domain.intersect import IntersectParallelizationStrategy
from OTAnalytics.domain.section import Section
from OTAnalytics.domain.track_dataset.track_dataset import TrackDataset


class SequentialIntersect(IntersectParallelizationStrategy):
    """Executes the intersection of tracks and sections in sequential order."""

    @property
    def num_processes(self) -> int:
        return 1

    def execute(
        self,
        intersect: Callable[[TrackDataset, Iterable[Section]], EventDataset],
        tasks: Sequence[tuple[TrackDataset, Iterable[Section]]],
    ) -> EventDataset:
        event_dataset = PythonEventDataset()
        for task in tasks:
            track_dataset, sections = task
            event_dataset.extend(intersect(track_dataset, sections))
        return event_dataset

    def set_num_processes(self, value: int) -> None:
        pass
