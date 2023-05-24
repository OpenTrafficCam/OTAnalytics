from typing import Iterable

from OTAnalytics.application.eventlist import SceneActionDetector, SectionActionDetector
from OTAnalytics.domain.event import Event, SectionEventBuilder
from OTAnalytics.domain.intersect import (
    IntersectAreaByTrackPoints,
    IntersectBySmallTrackComponents,
    IntersectImplementation,
    IntersectParallelizationStrategy,
)
from OTAnalytics.domain.section import Area, LineSection, Section
from OTAnalytics.domain.track import Track


class RunIntersect:
    """
    This class defines the use case to intersect the given tracks with the given
    sections
    """

    def __init__(
        self,
        intersect_implementation: IntersectImplementation,
        intersect_parallelizer: IntersectParallelizationStrategy,
    ) -> None:
        self._intersect_implementation = intersect_implementation
        self._intersect_parallelizer = intersect_parallelizer

    def run(self, tracks: Iterable[Track], sections: Iterable[Section]) -> list[Event]:
        return self._intersect_parallelizer.execute(
            self._run_on_single_track, tracks, sections
        )

    def _run_on_single_track(
        self, track: Track, sections: Iterable[Section]
    ) -> list[Event]:
        events: list[Event] = []
        for _section in sections:
            if isinstance(_section, LineSection):
                line_section_intersector = IntersectBySmallTrackComponents(
                    implementation=self._intersect_implementation,
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
                    implementation=self._intersect_implementation,
                    area=_section,
                )
                section_event_builder = SectionEventBuilder()
                section_action_detector = SectionActionDetector(
                    intersector=area_section_intersector,
                    section_event_builder=section_event_builder,
                )
                _events = section_action_detector._detect(section=_section, track=track)
                events.extend(_events)

        return events


class RunSceneEventDetection:
    def __init__(self, scene_action_detector: SceneActionDetector) -> None:
        self._scene_action_detector = scene_action_detector

    def run(self, tracks: Iterable[Track]) -> list[Event]:
        return self._scene_action_detector.detect(tracks)
