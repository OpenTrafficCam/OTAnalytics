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
