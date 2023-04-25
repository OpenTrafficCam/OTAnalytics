# NOTE: To use uncomment below code and `pip install ray`
# import itertools
# from os import cpu_count
# from typing import Callable, Iterable

# import ray
# from ray.util.multiprocessing import Pool

# from OTAnalytics.domain.event import Event
# from OTAnalytics.domain.intersect import IntersectParallelizationStrategy
# from OTAnalytics.domain.section import Section
# from OTAnalytics.domain.track import Track


# class RayIntersectParallelization(IntersectParallelizationStrategy):
#     def __init__(self) -> None:
#         ray.init(num_cpus=cpu_count(), ignore_reinit_error=True)

#     def execute(
#         self,
#         intersect: Callable[[Track, Iterable[Section]], Iterable[Event]],
#         tracks: Iterable[Track],
#         sections: Iterable[Section],
#     ) -> Iterable[Event]:
#         pool = Pool()

#         def func_wrapper(track: Track) -> Iterable[Event]:
#             return intersect(track, sections)

#         events: list[list[Event]] = []
#         events = pool.map(func_wrapper, tracks)
#         return self._flatten_events(events)

#     def _flatten_events(self, events: Iterable[Iterable[Event]]) -> Iterable[Event]:
#         return list(itertools.chain.from_iterable(events))
