from typing import Iterable, Optional

from OTAnalytics.domain.event import Event, EventType, SectionEventBuilder
from OTAnalytics.domain.intersect import Intersector
from OTAnalytics.domain.section import Section
from OTAnalytics.domain.track import Track


class EventList:
    def __init__(self) -> None:
        self.events: list[Event] = []

    def add_event(self, event: Event) -> None:
        self.events.append(event)


class SectionActionDetector:
    def __init__(
        self, intersector: Intersector, section_event_builder: SectionEventBuilder
    ) -> None:
        self.intersector = intersector
        self.section_event_builder = section_event_builder
        pass

    def detect_enter(self, section: Section, track: Track) -> Optional[Event]:
        """Detects the first time a track crosses the section.

        Args:
            section (Section): the section.
            track (Track): the track.

        Returns:
            Optional[Event]: an event if section has been crossed. Otherwise `None`.
        """
        self.section_event_builder.add_section_id(section.id)
        self.section_event_builder.add_event_type(EventType.SECTION_ENTER)
        self.section_event_builder.add_direction_vector(
            detection_1=track.detections[0], detection_2=track.detections[-1]
        )
        event: Optional[Event] = self.intersector.intersect(
            track, event_builder=self.section_event_builder
        )

        if event:
            return event
        return None

    def detect_leave(self, section: Section, track: Track) -> Optional[Event]:
        """Detects the last time a track crosses the section.

        Args:
            section (Section): the section.
            track (Track): the track.

        Returns:
            Optional[Event]: an event if section has been crossed. Otherwise `None`.
        """
        raise NotImplementedError


class SectionEventCreator:
    def __init__(
        self,
        section_action_detector: SectionActionDetector,
    ) -> None:
        self.section_action_detector = section_action_detector

    def create_enter_events(
        self,
        sections: list[Section],
        tracks: list[Track],
    ) -> list[Event]:
        event_list: list[Event] = []
        for section in sections:
            for track in tracks:
                enter_event = self.section_action_detector.detect_enter(section, track)
                if enter_event:
                    event_list.append(enter_event)

        return event_list

    def create_leave_events(
        self, sections: list[Section], tracks: list[Track]
    ) -> list[Event]:
        raise NotImplementedError


class EventListRepository:
    def __init__(self) -> None:
        self.events: list[Event] = []

    def add(self, event: Event) -> None:
        self.events.append(event)

    def add_all(self, events: Iterable[Event]) -> None:
        self.events.extend(events)

    def get_all(self) -> Iterable[Event]:
        return self.events
