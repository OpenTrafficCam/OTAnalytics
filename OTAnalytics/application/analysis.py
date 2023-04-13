from typing import Iterable

from OTAnalytics.application.eventlist import SectionActionDetector
from OTAnalytics.domain.event import Event, SectionEventBuilder
from OTAnalytics.domain.intersect import (
    IntersectAreaByTrackPoints,
    IntersectBySplittingTrackLine,
    IntersectImplementation,
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
    ) -> None:
        self._intersect_implementation = intersect_implementation

    def run(
        self, tracks: Iterable[Track], sections: Iterable[Section]
    ) -> Iterable[Event]:
        """
        Intersect all tracks with all sections and write the result into the event
        repository.
        """
        events: list[Event] = []
        for _track in tracks:
            for _section in sections:
                if isinstance(_section, LineSection):
                    line_section_intersector = IntersectBySplittingTrackLine(
                        implementation=self._intersect_implementation,
                        line_section=_section,
                    )
                    section_event_builder = SectionEventBuilder()
                    section_action_detector = SectionActionDetector(
                        intersector=line_section_intersector,
                        section_event_builder=section_event_builder,
                    )
                    _events = section_action_detector._detect(
                        section=_section, track=_track
                    )
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
                    _events = section_action_detector._detect(
                        section=_section, track=_track
                    )
                    events.extend(_events)
        return events
