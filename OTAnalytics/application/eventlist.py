from OTAnalytics.domain.event import (
    Event,
    EventType,
    SceneEventBuilder,
    SectionEventBuilder,
)
from OTAnalytics.domain.geometry import calculate_direction_vector
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

    def detect(
        self,
        sections: list[Section],
        tracks: list[Track],
    ) -> list[Event]:
        """Detect section events.

        Args:
            sections (list[Section]): the sections
            tracks (list[Track]): the tracks

        Returns:
            list[Event]: the events if tracks intersect with any of the sections.
                Otherwise return empty list.
        """
        event_list: list[Event] = []
        for section in sections:
            for track in tracks:
                enter_event = self._detect(section, track)
                if enter_event:
                    event_list.extend(enter_event)

        return event_list

    def _detect(self, section: Section, track: Track) -> list[Event]:
        """Detect when a track enters a section.

        Args:
            sections (Section): the section
            track (Track): the track

        Returns:
            list[Event]: the event if a track enters a section.
                Otherwise return empty list.
        """
        self.section_event_builder.add_section_id(section.id)
        self.section_event_builder.add_event_type(EventType.SECTION_ENTER)
        events: list[Event] = self.intersector.intersect(
            track, event_builder=self.section_event_builder
        )
        return events


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
        first_detection = track.detections[0]
        next_detection = track.detections[1]
        self._event_builder.add_direction_vector(
            calculate_direction_vector(
                first_detection.x, first_detection.y, next_detection.x, next_detection.y
            )
        )
        first_detection = track.detections[0]
        return self._event_builder.create_event(first_detection)

    def detect_leave_scene(self, track: Track) -> Event:
        """Detect the last time before a road user leaves the  scene.

        Args:
            tracks (list[Track]): the track associated with the road user

        Returns:
            list[Event]: the leave scene event
        """
        last_detection = track.detections[-1]
        prev_detection = track.detections[-2]
        self._event_builder.add_direction_vector(
            calculate_direction_vector(
                prev_detection.x, prev_detection.y, last_detection.x, last_detection.y
            )
        )
        self._event_builder.add_event_type(EventType.LEAVE_SCENE)
        first_detection = track.detections[-1]
        return self._event_builder.create_event(first_detection)
