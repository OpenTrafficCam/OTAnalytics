import re

from OTAnalytics.domain import track
from OTAnalytics.domain.event import (
    FILE_NAME_PATTERN,
    HOSTNAME,
    Event,
    ImproperFormattedFilename,
)
from OTAnalytics.domain.geometry import ImageCoordinate, calculate_direction_vector
from OTAnalytics.domain.track_dataset.track_dataset import (
    END_FRAME,
    END_OCCURRENCE,
    END_VIDEO_NAME,
    END_X,
    END_Y,
    START_FRAME,
    START_OCCURRENCE,
    START_VIDEO_NAME,
    START_X,
    START_Y,
    TrackDataset,
    TrackSegmentDataset,
)
from OTAnalytics.domain.types import EventType


def extract_hostname(name: str) -> str:
    """Extract hostname from name.

    Args:
        name (Path): name containing the hostname.

    Raises:
        ImproperFormattedFilename: if the name is not formatted as expected, an
            exception will be raised.

    Returns:
        str: the hostname.
    """
    match = re.search(
        FILE_NAME_PATTERN,
        name,
    )
    if match:
        hostname: str = match.group(HOSTNAME)
        return hostname
    raise ImproperFormattedFilename(f"Could not parse {name}. Hostname is missing.")


class SceneEventListBuilder:
    """Create enter and leave scene events for track segments."""

    def __init__(self) -> None:
        self._events: list[Event] = []

    def add_enter_scene_events(
        self, segments: TrackSegmentDataset
    ) -> "SceneEventListBuilder":
        """Create an enter scene event for each track segment.

        Args:
            segments (TrackSegmentDataset): segments to be used to create events for
        """
        segments.apply(self._create_enter_scene_event)
        return self

    def add_leave_scene_events(
        self, segments: TrackSegmentDataset
    ) -> "SceneEventListBuilder":
        """Create a leave scene event for each track segment.

        Args:
            segments (TrackSegmentDataset): segments to be used to create events for
        """
        segments.apply(self._create_leave_scene_event)
        return self

    def build(self) -> list[Event]:
        """Create the complete event list.

        Returns:
            list[Event]: complete event list
        """
        return self._events.copy()

    def _create_enter_scene_event(self, value: dict) -> None:
        event = self.__create_event(
            value=value,
            event_type=EventType.ENTER_SCENE,
            key_x=START_X,
            key_y=START_Y,
            key_occurrence=START_OCCURRENCE,
            key_frame=START_FRAME,
            key_video_name=START_VIDEO_NAME,
        )
        self._events.append(event)

    def _create_leave_scene_event(self, value: dict) -> None:
        event = self.__create_event(
            value=value,
            event_type=EventType.LEAVE_SCENE,
            key_x=END_X,
            key_y=END_Y,
            key_occurrence=END_OCCURRENCE,
            key_frame=END_FRAME,
            key_video_name=END_VIDEO_NAME,
        )
        self._events.append(event)

    @staticmethod
    def __create_event(
        value: dict,
        event_type: EventType,
        key_x: str,
        key_y: str,
        key_occurrence: str,
        key_frame: str,
        key_video_name: str,
    ) -> Event:
        image_coordinate = ImageCoordinate(value[key_x], value[key_y])
        occurrence = value[key_occurrence]
        return Event(
            road_user_id=value[track.TRACK_ID],
            road_user_type=value[track.TRACK_CLASSIFICATION],
            hostname=extract_hostname(value[key_video_name]),
            occurrence=occurrence,
            frame_number=value[key_frame],
            section_id=None,
            event_coordinate=image_coordinate,
            event_type=event_type,
            direction_vector=calculate_direction_vector(
                value[START_X],
                value[START_Y],
                value[END_X],
                value[END_Y],
            ),
            video_name=value[key_video_name],
            interpolated_occurrence=occurrence,
            interpolated_event_coordinate=image_coordinate,
        )


class SceneActionDetector:
    """Detect when a road user enters or leaves the scene."""

    def detect(self, tracks: TrackDataset) -> list[Event]:
        """Detect all enter and leave scene events.

        Args:
            tracks (Iterable[Track]): the tracks under inspection

        Returns:
            Iterable[Event]: the scene events
        """
        builder = SceneEventListBuilder()
        builder.add_enter_scene_events(tracks.get_first_segments())
        builder.add_leave_scene_events(tracks.get_last_segments())
        return builder.build()
