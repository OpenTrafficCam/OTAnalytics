from typing import Iterable

from OTAnalytics.domain.event import Event, EventType, SceneEventBuilder
from OTAnalytics.domain.geometry import calculate_direction_vector
from OTAnalytics.domain.track import Track


class SceneActionDetector:
    """Detect when a road user enters or leaves the scene.

    Args:
        scene_event_builder (SceneEventBuilder): the builder to build scene events
    """

    def __init__(self, scene_event_builder: SceneEventBuilder) -> None:
        self._event_builder = scene_event_builder

    def detect_enter_scene(self, track: Track) -> Event:
        """Detect the first time a road user enters the scene.

        Args:
            tracks (Track): the track associated with the road user

        Returns:
            Iterable[Event]: the enter scene event
        """
        self._event_builder.add_event_type(EventType.ENTER_SCENE)
        self._event_builder.add_road_user_type(track.classification)
        first_detection = track.detections[0]
        next_detection = track.detections[1]
        self._event_builder.add_direction_vector(
            calculate_direction_vector(
                first_detection.x, first_detection.y, next_detection.x, next_detection.y
            )
        )
        self._event_builder.add_event_coordinate(first_detection.x, first_detection.y)

        return self._event_builder.create_event(first_detection)

    def detect_leave_scene(self, track: Track) -> Event:
        """Detect the last time a road user is seen before leaving the scene.

        Args:
            tracks (Track): the track associated with the road user

        Returns:
            Iterable[Event]: the leave scene event
        """
        self._event_builder.add_event_type(EventType.LEAVE_SCENE)
        self._event_builder.add_road_user_type(track.classification)
        last_detection = track.detections[-1]
        second_to_last_detection = track.detections[-2]
        self._event_builder.add_direction_vector(
            calculate_direction_vector(
                second_to_last_detection.x,
                second_to_last_detection.y,
                last_detection.x,
                last_detection.y,
            )
        )
        self._event_builder.add_event_coordinate(last_detection.x, last_detection.y)

        return self._event_builder.create_event(last_detection)

    def detect(self, tracks: Iterable[Track]) -> list[Event]:
        """Detect all enter and leave scene events.

        Args:
            tracks (Iterable[Track]): the tracks under inspection

        Returns:
            Iterable[Event]: the scene events
        """
        events: list[Event] = []
        for track in tracks:
            events.append(self.detect_enter_scene(track))
            events.append(self.detect_leave_scene(track))
        return events
