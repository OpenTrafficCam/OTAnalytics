from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

NAME: str = "name"
START_DATE: str = "start_date"
METADATA: str = "metadata"
TK_NUMBER: str = "tk_number"
COUNTING_LOCATION_NUMBER: str = "counting_location_number"
DIRECTION: str = "direction"
DIRECTION_DESCRIPTION: str = "direction_description"
HAS_BICYCLE_LANE: str = "has_bicycle_lane"
IS_BICYCLE_COUNTING: str = "is_bicycle_counting"
COUNTING_DAY: str = "counting_day"
WEATHER: str = "weather"
REMARK: str = "remark"
COORDINATE_X: str = "coordinate_x"
COORDINATE_Y: str = "coordinate_y"


class DirectionOfStationingParseError(Exception):
    pass


class DirectionOfStationing(Enum):
    IN_DIRECTION = "1"
    OPPOSITE_DIRECTION = "2"

    def serialize(self) -> str:
        return self.value

    @staticmethod
    def parse(direction: str) -> "DirectionOfStationing":
        match direction:
            case DirectionOfStationing.IN_DIRECTION.value:
                return DirectionOfStationing.IN_DIRECTION
            case DirectionOfStationing.OPPOSITE_DIRECTION.value:
                return DirectionOfStationing.OPPOSITE_DIRECTION
            case _:
                raise DirectionOfStationingParseError(
                    f"Unable to parse not existing direction '{direction}'"
                )


class CountingDayTypeParseError(Exception):
    pass


class CountingDayType(Enum):
    NOW_1 = "1"
    NOW_2 = "2"
    FR_1 = "3"
    FR_2 = "4"
    SO_1 = "5"
    SO_2 = "6"
    FEW_1 = "7"
    FEW_2 = "8"

    def serialize(self) -> str:
        return self.value

    @staticmethod
    def parse(counting_day_type: str) -> "CountingDayType":
        for type in [
            CountingDayType.NOW_1,
            CountingDayType.NOW_2,
            CountingDayType.FR_1,
            CountingDayType.FR_2,
            CountingDayType.SO_1,
            CountingDayType.SO_2,
            CountingDayType.FEW_1,
            CountingDayType.FEW_2,
        ]:
            if type.value == counting_day_type:
                return type
        raise CountingDayTypeParseError(
            f"Unable to parse not existing counting day type '{counting_day_type}'"
        )


class WeatherTypeParseError(Exception):
    pass


class WeatherType(Enum):
    SUN = "1"
    CLOUD = "2"
    RAIN = "3"
    SNOW = "4"
    FOG = "5"

    def serialize(self) -> str:
        return self.value

    @staticmethod
    def parse(weather_type: str) -> "WeatherType":
        for type in [
            WeatherType.SUN,
            WeatherType.CLOUD,
            WeatherType.RAIN,
            WeatherType.SNOW,
            WeatherType.FOG,
        ]:
            if type.value == weather_type:
                return type
        raise WeatherTypeParseError(
            f"Unable to parse not existing weather type '{weather_type}'"
        )


@dataclass
class SvzMetadata:
    tk_number: str | None
    counting_location_number: str | None
    direction: DirectionOfStationing | None
    direction_description: str | None
    has_bicycle_lane: bool | None
    is_bicycle_counting: bool | None
    counting_day: CountingDayType | None
    weather: WeatherType | None
    remark: str | None
    coordinate_x: str | None
    coordinate_y: str | None

    def to_dict(self) -> dict:
        return {
            TK_NUMBER: self.tk_number if self.tk_number else None,
            COUNTING_LOCATION_NUMBER: (
                self.counting_location_number if self.counting_location_number else None
            ),
            DIRECTION: self.direction.serialize() if self.direction else None,
            DIRECTION_DESCRIPTION: (
                self.direction_description if self.direction_description else None
            ),
            HAS_BICYCLE_LANE: (
                self.has_bicycle_lane if self.has_bicycle_lane else False
            ),
            IS_BICYCLE_COUNTING: (
                self.is_bicycle_counting if self.is_bicycle_counting else False
            ),
            COUNTING_DAY: self.counting_day.serialize() if self.counting_day else None,
            WEATHER: self.weather.serialize() if self.weather else None,
            REMARK: self.remark if self.remark else None,
            COORDINATE_X: self.coordinate_x if self.coordinate_x else None,
            COORDINATE_Y: self.coordinate_y if self.coordinate_y else None,
        }


@dataclass
class Project:
    name: str
    start_date: Optional[datetime] = None
    metadata: Optional[SvzMetadata] = None

    def to_dict(self) -> dict:
        return {
            NAME: self.name,
            START_DATE: self.start_date.timestamp() if self.start_date else None,
            METADATA: self.metadata.to_dict() if self.metadata else None,
        }
