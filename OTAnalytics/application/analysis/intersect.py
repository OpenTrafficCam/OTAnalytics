from threading import Thread
from typing import Callable, Iterable

from OTAnalytics.application.eventlist import SceneActionDetector, SectionActionDetector
from OTAnalytics.domain.event import Event, SectionEventBuilder
from OTAnalytics.domain.intersect import (
    IntersectAreaByTrackPoints,
    IntersectBySmallTrackComponents,
    IntersectImplementation,
    IntersectParallelizationStrategy,
)
from OTAnalytics.domain.progress import Progressbar, ProgressbarBuilder
from OTAnalytics.domain.section import Area, LineSection, Section
from OTAnalytics.domain.track import Track


def _run_on_single_track(
    track: Track,
    sections: Iterable[Section],
    _intersect_implementation: IntersectImplementation,
    update_progress: Callable[[int], None],
) -> list[Event]:
    events: list[Event] = []
    for _section in sections:
        if isinstance(_section, LineSection):
            line_section_intersector = IntersectBySmallTrackComponents(
                implementation=_intersect_implementation,
                line_section=_section,
            )
            section_event_builder = SectionEventBuilder()
            section_action_detector = SectionActionDetector(
                intersector=line_section_intersector,
                section_event_builder=section_event_builder,
            )
            _events = section_action_detector._detect(section=_section, track=track)
            events.extend(_events)
        if isinstance(_section, Area):
            area_section_intersector = IntersectAreaByTrackPoints(
                implementation=_intersect_implementation,
                area=_section,
            )
            section_event_builder = SectionEventBuilder()
            section_action_detector = SectionActionDetector(
                intersector=area_section_intersector,
                section_event_builder=section_event_builder,
            )
            _events = section_action_detector._detect(section=_section, track=track)
            events.extend(_events)
    update_progress(1)
    return events


def _intersect(
    tracks: Progressbar,
    sections: Iterable[Section],
    add_events: Callable[[Iterable[Event]], None],
    intersect_implementation: IntersectImplementation,
    intersect_parallelizer: IntersectParallelizationStrategy,
) -> None:
    events = intersect_parallelizer.execute(
        _run_on_single_track, tracks, sections, intersect_implementation, tracks.update
    )
    add_events(events)


class RunIntersect:
    """
    This class defines the use case to intersect the given tracks with the given
    sections
    """

    def __init__(
        self,
        intersect_implementation: IntersectImplementation,
        intersect_parallelizer: IntersectParallelizationStrategy,
        progressbar: ProgressbarBuilder,
        add_events: Callable[[Iterable[Event]], None],
    ) -> None:
        self._intersect_implementation = intersect_implementation
        self._intersect_parallelizer = intersect_parallelizer
        self._progressbar = progressbar
        self._add_events = add_events

    def run(self, tracks: Iterable[Track], sections: Iterable[Section]) -> None:
        _tracks = self._progressbar(list(tracks), "Intersected tracks: ", "tracks")
        Thread(
            target=_intersect,
            args=(
                _tracks,
                sections,
                self._add_events,
                self._intersect_implementation,
                self._intersect_parallelizer,
            ),
        ).start()


class RunSceneEventDetection:
    def __init__(self, scene_action_detector: SceneActionDetector) -> None:
        self._scene_action_detector = scene_action_detector

    def run(self, tracks: Iterable[Track]) -> list[Event]:
        return self._scene_action_detector.detect(tracks)
