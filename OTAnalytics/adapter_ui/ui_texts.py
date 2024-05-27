from OTAnalytics.application.project import (
    CountingDayType,
    DirectionOfStationing,
    WeatherType,
)

DIRECTIONS_OF_STATIONING = {
    DirectionOfStationing.IN_DIRECTION: "In Stationierungsrichtung",
    DirectionOfStationing.OPPOSITE_DIRECTION: "Gegen Stationierungsrichtung",
}

COUNTING_DAY_TYPES = {
    CountingDayType.NOW_1: "1. NoW",
    CountingDayType.NOW_2: "2. NoW",
    CountingDayType.FR_1: "1. Fr",
    CountingDayType.FR_2: "2. Fr",
    CountingDayType.SO_1: "1. So",
    CountingDayType.SO_2: "2. So",
    CountingDayType.FEW_1: "1. FeW",
    CountingDayType.FEW_2: "2. FeW",
}

WEATHER_TYPES = {
    WeatherType.SUN: "sonnig",
    WeatherType.CLOUD: "bewölkt",
    WeatherType.RAIN: "Regen",
    WeatherType.SNOW: "Schnee",
    WeatherType.FOG: "Nebel",
}
