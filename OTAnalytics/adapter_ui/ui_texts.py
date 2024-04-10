from OTAnalytics.application.project import DirectionOfStationing, WeatherType

DIRECTIONS_OF_STATIONING = {
    DirectionOfStationing.IN_DIRECTION: "In Stationierungsrichtung",
    DirectionOfStationing.OPPOSITE_DIRECTION: "Gegen Stationierungsrichtung",
}

WEATHER_TYPES = {
    WeatherType.SUN: "sonnig",
    WeatherType.CLOUD: "bewölkt",
    WeatherType.RAIN: "Regen",
    WeatherType.SNOW: "Schnee",
    WeatherType.FOG: "Nebel",
}
