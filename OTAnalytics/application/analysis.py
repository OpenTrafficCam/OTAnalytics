from collections import defaultdict
from typing import Iterable

from OTAnalytics.application.eventlist import SceneActionDetector, SectionActionDetector
from OTAnalytics.domain.event import Event, SectionEventBuilder
from OTAnalytics.domain.flow import Flow, FlowId
from OTAnalytics.domain.intersect import (
    IntersectAreaByTrackPoints,
    IntersectBySmallTrackComponents,
    IntersectImplementation,
    IntersectParallelizationStrategy,
)
from OTAnalytics.domain.section import Area, LineSection, Section, SectionId
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


class RunTrafficCounting:
    def run(self, events: list[Event], flows: list[Flow]) -> dict[FlowId, int]:
        flows_by_start_and_end: dict[
            tuple[SectionId, SectionId], list[Flow]
        ] = defaultdict(list)
        for flow in flows:
            flows_by_start_and_end[(flow.start.id, flow.end.id)].append(flow)

        sections_by_road_user: dict[int, list[SectionId]] = defaultdict(list)
        for event in events:
            if event.section_id:
                sections_by_road_user[event.road_user_id].append(event.section_id)

        user_to_flow: dict[int, Flow] = {}
        sections: list[SectionId]
        for road_user, sections in sections_by_road_user.items():
            candidate_events = self.__create_candidates(sections)
            candidate_flows: list[Flow] = []
            for candidate in candidate_events:
                candidate_flows.extend(flows_by_start_and_end.get(candidate, []))
            flow = max(candidate_flows, key=lambda current: current.distance)
            user_to_flow[road_user] = flow

        flow_to_user: dict[FlowId, list[int]] = defaultdict(list)
        for user, flow in user_to_flow.items():
            flow_to_user[flow.id].append(user)

        counts = {flow: len(users) for flow, users in flow_to_user.items()}
        for flow in flows:
            if flow.id not in counts:
                counts[flow.id] = 0
        return counts

    def __create_candidates(
        self, sections: list[SectionId]
    ) -> list[tuple[SectionId, SectionId]]:
        candidates: list[tuple[SectionId, SectionId]] = []
        for start in sections:
            candidates.extend((start, end) for end in sections)
        return candidates
