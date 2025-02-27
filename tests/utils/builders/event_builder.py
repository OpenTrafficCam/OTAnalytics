from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Self

from OTAnalytics.domain.event import Event
from OTAnalytics.domain.geometry import DirectionVector2D, ImageCoordinate
from OTAnalytics.domain.section import SectionId
from OTAnalytics.domain.types import EventType
from tests.utils.builders.constants import (
    DEFAULT_HOSTNAME,
    DEFAULT_OCCURRENCE_DAY,
    DEFAULT_OCCURRENCE_HOUR,
    DEFAULT_OCCURRENCE_MICROSECOND,
    DEFAULT_OCCURRENCE_MINUTE,
    DEFAULT_OCCURRENCE_MONTH,
    DEFAULT_OCCURRENCE_SECOND,
    DEFAULT_OCCURRENCE_YEAR,
    DEFAULT_VIDEO_NAME,
)


@dataclass
class EventBuilder:
    road_user_id: str = "1"
    road_user_type: str = "car"
    hostname: str = DEFAULT_HOSTNAME
    occurrence_year: int = DEFAULT_OCCURRENCE_YEAR
    occurrence_month: int = DEFAULT_OCCURRENCE_MONTH
    occurrence_day: int = DEFAULT_OCCURRENCE_DAY
    occurrence_hour: int = DEFAULT_OCCURRENCE_HOUR
    occurrence_minute: int = DEFAULT_OCCURRENCE_MINUTE
    occurrence_second: int = DEFAULT_OCCURRENCE_SECOND
    occurrence_microsecond: int = DEFAULT_OCCURRENCE_MICROSECOND
    frame_number: int = 1
    section_id: str | None = "N"
    event_coordinate_x: float = 0.0
    event_coordinate_y: float = 0.0
    relative_position: float = 0.0
    event_type: str = "section-enter"
    direction_vector_x: float = 0.0
    direction_vector_y: float = 0.0
    video_name: str = DEFAULT_VIDEO_NAME
    interpolated_occurrence: datetime | None = None
    interpolated_event_coordinate: ImageCoordinate | None = None

    def __post_init__(self) -> None:
        self._events: list[Event] = []

    def build_events(self) -> list[Event]:
        return self._events

    def build_section_event(self) -> Event:
        occurrence = datetime(
            self.occurrence_year,
            self.occurrence_month,
            self.occurrence_day,
            self.occurrence_hour,
            self.occurrence_minute,
            self.occurrence_second,
            self.occurrence_microsecond,
            tzinfo=timezone.utc,
        )
        event_coordinate = ImageCoordinate(
            self.event_coordinate_x, self.event_coordinate_y
        )
        if self.interpolated_occurrence is None:
            interpolated_occurrence = occurrence
        else:
            interpolated_occurrence = self.interpolated_occurrence

        if self.interpolated_event_coordinate is None:
            interpolated_event_coordinate = event_coordinate
        else:
            interpolated_event_coordinate = self.interpolated_event_coordinate

        return Event(
            road_user_id=self.road_user_id,
            road_user_type=self.road_user_type,
            hostname=self.hostname,
            occurrence=occurrence,
            frame_number=self.frame_number,
            section_id=SectionId(self.section_id) if self.section_id else None,
            event_coordinate=event_coordinate,
            event_type=EventType.parse(self.event_type),
            direction_vector=DirectionVector2D(
                self.direction_vector_x, self.direction_vector_y
            ),
            video_name=self.video_name,
            interpolated_occurrence=interpolated_occurrence,
            interpolated_event_coordinate=interpolated_event_coordinate,
        )

    def append_section_event(self) -> Self:
        self._events.append(self.build_section_event())
        return self

    def add_second(self, second: int) -> Self:
        self.occurrence_second = second
        return self

    def add_microsecond(self, microsecond: int) -> Self:
        self.occurrence_microsecond = microsecond
        return self

    def add_frame_number(self, frame_number: int) -> Self:
        self.frame_number = frame_number
        return self

    def add_event_type(self, event_type: str) -> Self:
        self.event_type = event_type
        return self

    def add_event_coordinate(self, x: float, y: float) -> Self:
        self.event_coordinate_x = x
        self.event_coordinate_y = y
        return self

    def add_direction_vector(self, x: float, y: float) -> Self:
        self.direction_vector_x = x
        self.direction_vector_y = y
        return self

    def add_road_user_id(self, id: str) -> Self:
        self.road_user_id = id
        return self

    def add_road_user_type(self, type: str) -> Self:
        self.road_user_type = type
        return self

    def add_section_id(self, id: str) -> Self:
        self.section_id = id
        return self

    def clean_section_id(self) -> Self:
        self.section_id = None
        return self
