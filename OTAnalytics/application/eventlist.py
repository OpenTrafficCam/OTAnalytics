from typing import Iterable, Optional

from OTAnalytics.domain.event import (
    Event,
    EventType,
    SceneEventBuilder,
    SectionEventBuilder,
)
from OTAnalytics.domain.intersect import Intersector
from OTAnalytics.domain.section import Section
from OTAnalytics.domain.track import Track


class SectionActionDetector:
    """Detect when a track enters or leaves a section and generate events.

    A track enters or leaves a section when they intersect.

    Args:
        intersector (Intersector): the intersector
        section_event_builder (SectionEventBuilder): the section event builder
    """

    def __init__(
        self, intersector: Intersector, section_event_builder: SectionEventBuilder
    ) -> None:
        self.intersector = intersector
        self.section_event_builder = section_event_builder

    def detect_enter_actions(
        self,
        sections: list[Section],
        tracks: list[Track],
    ) -> list[Event]:
        """Detect if tracks enter sections.

        Args:
            sections (list[Section]): the sections
            tracks (list[Track]): the tracks

        Returns:
            list[Event]: the events if tracks do enter any of the sections.
                Otherwise `None`.
        """
        event_list: list[Event] = []
        for section in sections:
            for track in tracks:
                enter_event = self._detect_enter(section, track)
                if enter_event:
                    event_list.extend(enter_event)

        return event_list

    def detect_leave_actions(
        self,
        sections: list[Section],
        tracks: list[Track],
    ) -> list[Event]:
        """Detect if tracks leave sections.

        Args:
            sections (list[Section]): the sections
            tracks (list[Track]): the tracks

        Returns:
            list[Event]: the event if tracks do leave any of the sections.
                Otherwise `None`.
        """
        raise NotImplementedError

    def _detect_enter(self, section: Section, track: Track) -> Optional[list[Event]]:
        """Detect when a track enters a section.

        Args:
            sections (Section): the section
            track (Track): the track

        Returns:
            list[Event]: the event if a track enters a section.
                Otherwise `None`.
        """
        self.section_event_builder.add_section_id(section.id)
        self.section_event_builder.add_event_type(EventType.SECTION_ENTER)
        self.section_event_builder.add_direction_vector(
            detection_1=track.detections[0], detection_2=track.detections[-1]
        )
        events: Optional[list[Event]] = self.intersector.intersect(
            track, event_builder=self.section_event_builder
        )

        if events:
            return events
        return None

    def _detect_leave(self, section: Section, track: Track) -> Optional[Event]:
        """Detect when a track leaves a section.

        Args:
            sections (Section): the section
            tracks (Track): the track

        Returns:
            list[Event]: the event if a track leaves a section.
                Otherwise `None`.
        """
        raise NotImplementedError


class SceneActionDetector:
    """Detect when a road user enters or leaves the scene.

    Args:
        scene_event_builder (SceneEventBuilder): the builder to build scene events
    """

    def __init__(self, scene_event_builder: SceneEventBuilder) -> None:
        self._event_builder = scene_event_builder

    def detect_enter_scene(self, track: Track) -> Event:
        """Detect the first time a road user enters the  scene.

        Args:
            tracks (list[Track]): the track associated with the road user

        Returns:
            list[Event]: the enter scene event
        """

        self._event_builder.add_event_type(EventType.ENTER_SCENE)
        self._event_builder.add_direction_vector(
            track.detections[0], track.detections[-1]
        )
        first_detection = track.detections[0]
        scene_enter_event = self._event_builder.create_event(first_detection)
        return scene_enter_event

    def detect_leave_scene(self, track: Track) -> Event:
        """Detect the last time before a road user leaves the  scene.

        Args:
            tracks (list[Track]): the track associated with the road user

        Returns:
            list[Event]: the leave scene event
        """
        self._event_builder.add_direction_vector(
            track.detections[0], track.detections[-1]
        )
        self._event_builder.add_event_type(EventType.LEAVE_SCENE)
        first_detection = track.detections[-1]
        leave_scene_event = self._event_builder.create_event(first_detection)
        return leave_scene_event


class EventRepository:
    """The repository to store events."""

    def __init__(self) -> None:
        self.events: list[Event] = []

    def add(self, event: Event) -> None:
        """Add an event to the repository.

        Args:
            event (Event): the event to add
        """
        self.events.append(event)

    def add_all(self, events: Iterable[Event]) -> None:
        """Add multiple events at once to the repository.

        Args:
            events (Iterable[Event]): the events
        """
        self.events.extend(events)

    def get_all(self) -> Iterable[Event]:
        """Get all events stored in the repository.

        Returns:
            Iterable[Event]: the events
        """
        return self.events
