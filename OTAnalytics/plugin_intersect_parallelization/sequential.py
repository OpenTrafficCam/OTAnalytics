from typing import Callable, Iterable, Sequence

from OTAnalytics.domain.event import Event
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
        intersect: Callable[[TrackDataset, Iterable[Section]], Iterable[Event]],
        tasks: Sequence[tuple[TrackDataset, Iterable[Section]]],
    ) -> list[Event]:
        events: list[Event] = []
        for task in tasks:
            track_dataset, sections = task
            events.extend(intersect(track_dataset, sections))
        return events

    def set_num_processes(self, value: int) -> None:
        pass
