import re

from OTAnalytics.domain import track
from OTAnalytics.domain.event import (
    FILE_NAME_PATTERN,
    HOSTNAME,
    Event,
    ImproperFormattedFilename,
)
from OTAnalytics.domain.geometry import ImageCoordinate, calculate_direction_vector
from OTAnalytics.domain.track_dataset import (
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
)
from OTAnalytics.domain.types import EventType


def extract_hostname(name: str) -> str:
    """Extract hostname from name.

    Args:
        name (Path): name containing the hostname.

    Raises:
        InproperFormattedFilename: if the name is not formatted as expected, an
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


class SceneActionDetector:
    """Detect when a road user enters or leaves the scene."""

    def detect(self, tracks: TrackDataset) -> list[Event]:
        """Detect all enter and leave scene events.

        Args:
            tracks (Iterable[Track]): the tracks under inspection

        Returns:
            Iterable[Event]: the scene events
        """
        events: list[Event] = []
        tracks.apply_to_first_segments(
            lambda segments: segments.apply(
                lambda segment: events.append(self._create_enter_scene_event(segment))
            )
        )
        tracks.apply_to_last_segments(
            lambda segments: segments.apply(
                lambda segment: events.append(self._create_leave_scene_event(segment))
            )
        )
        return events

    def _create_enter_scene_event(self, value: dict) -> Event:
        event = Event(
            road_user_id=value[track.TRACK_ID],
            road_user_type=value[track.TRACK_CLASSIFICATION],
            hostname=extract_hostname(value[START_VIDEO_NAME]),
            occurrence=value[START_OCCURRENCE],
            frame_number=value[START_FRAME],
            section_id=None,
            event_coordinate=ImageCoordinate(value[START_X], value[START_Y]),
            event_type=EventType.ENTER_SCENE,
            direction_vector=calculate_direction_vector(
                value[START_X],
                value[START_Y],
                value[END_X],
                value[END_Y],
            ),
            video_name=value[START_VIDEO_NAME],
        )
        return event

    def _create_leave_scene_event(self, value: dict) -> Event:
        event = Event(
            road_user_id=value[track.TRACK_ID],
            road_user_type=value[track.TRACK_CLASSIFICATION],
            hostname=extract_hostname(value[END_VIDEO_NAME]),
            occurrence=value[END_OCCURRENCE],
            frame_number=value[END_FRAME],
            section_id=None,
            event_coordinate=ImageCoordinate(value[END_X], value[END_Y]),
            event_type=EventType.LEAVE_SCENE,
            direction_vector=calculate_direction_vector(
                value[START_X],
                value[START_Y],
                value[END_X],
                value[END_Y],
            ),
            video_name=value[END_VIDEO_NAME],
        )
        return event
