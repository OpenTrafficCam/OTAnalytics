from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

from OTAnalytics.domain.common import DataclassValidation
from OTAnalytics.domain.geometry import Coordinate


class RoadUserType(Enum):
    """Enum defining all road user types."""

    PERSON: str = "PERSON"
    BICYCLE: str = "BICYCLE"
    MOTORCYCLE: str = "MOTORCYCLE"
    CAR: str = "CAR"
    BUS: str = "BUS"
    TRUCK: str = "TRUCK"
    TRAIN: str = "TRAIN"


class EventType(Enum):
    """Enum defining all event types."""

    SECTION_ENTER: str = "section-enter"
    SECTION_LEAVE: str = "section-leave"


@dataclass(frozen=True)
class ImageCoordinate(Coordinate):
    """An image coordinate.

    Raises:
        ValueError: x < 0
        ValueError: y < 0

    Args:
        x (float): the x coordinate must be greater equal zero.
        y (float): the y coordinate must be greater equal zero.
    """

    def _validate(self) -> None:
        if self.x < 0:
            raise ValueError(
                f"x image coordinate must be greater equal zero, but is{self.x}"
            )
        if self.y < 0:
            raise ValueError(
                f"y image coordinate must be greater equal zero, but is{self.x}"
            )


@dataclass(frozen=True)
class DirectionVector2D:
    """Represents a 2-dimensional direction vector.

    Args:
        x1 (float): the first component of the 2-dim direction vector.
        x2 (float): the second component of the 2-dim direction vector.
    """

    x1: float
    x2: float


@dataclass(frozen=True, kw_only=True)
class Event(DataclassValidation):
    """A traffic event triggered by some traffic event holding all necessary
    information for further processing.

    One party involved in this event is a road user. It is not required for necessarily
    required for more than 1 party to be involved in this event.

    An event can be raised upon certain traffic actions.
    To give an example such actions could be:
    - a vehicle has entered a section
    - a vehicle has left a section
    - section entered by a vehicle

    Raises:
        ValueError: vehicle_id < 1
        ValueError: frame_number < 1

    Args:
        road_user_id (int): the road user id involved with this event. It must be
        greater equal one.
        road_user_type (RoadUserType): the road user type involved with this event.
        hostname (str): the OTCamera hostname that the video is associated with.
        occurrence (datetime): the time when this event occurred.
        frame_number (int): the video frame number that this event is associated with.
        section_id (Optional[int]): only set when event type is of section.
        Defaults to `None`.
        event_coordinate (ImageCoordinate): location where the event occurred in
        the video.
        event_type (EventType): this event's type.
        direction_vector (DirectionVector2D): a 2-dimensional direction vector denoting
        the direction of the road user associated with this event.
        video_name (str): the video name associated with this event.

    """

    road_user_id: int
    road_user_type: RoadUserType
    hostname: str
    occurrence: datetime
    frame_number: int
    section_id: Optional[int]
    event_coordinate: ImageCoordinate
    event_type: EventType
    direction_vector: DirectionVector2D
    video_name = str

    def _validate(self) -> None:
        self._validate_road_user_id_greater_zero()
        self._validate_frame_number_greater_equal_one()

    def _validate_frame_number_greater_equal_one(self) -> None:
        if self.frame_number < 1:
            raise (
                ValueError(
                    (
                        "frame number must be greater equal one, "
                        f"but it {self.frame_number}"
                    )
                )
            )

    def _validate_road_user_id_greater_zero(self) -> None:
        if self.road_user_id < 0:
            raise ValueError(
                f"vehicle_id must be greater than zero, but is {self.road_user_id}"
            )


@dataclass(frozen=True, kw_only=True)
class SectionEnterEvent(Event):
    """Defines an event where a road_user has entered a section.

    section_id (id): section ID involved with this event.
    event_type (EventType): the event type.
    """

    section_id: int
    event_type: EventType = EventType.SECTION_ENTER


@dataclass(frozen=True, kw_only=True)
class SectionLeaveEvent(Event):
    """Defines an event where a road_user has left a section.

    section_id (id): section ID involved with this event.
    event_type (EventType): the event type.
    """

    section_id: int
    event_type: EventType = EventType.SECTION_LEAVE
