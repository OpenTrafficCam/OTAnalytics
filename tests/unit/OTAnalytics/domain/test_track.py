from dataclasses import dataclass
from unittest.mock import Mock

from OTAnalytics.domain.track import GEO_X, GEO_Y, Detection

GIVEN_GEO_X = 449245.82
GIVEN_GEO_Y = 5699325.96


@dataclass
class Given:
    detection: Detection


def create_given() -> Given:
    detection = Mock(spec=Detection)
    detection.geo_x = GIVEN_GEO_X
    detection.geo_y = GIVEN_GEO_Y
    return Given(detection=detection)


class TestDetectionGeoCoordinates:
    def test_geo_x_constant_value(self) -> None:
        assert GEO_X == "geo_x"

    def test_geo_y_constant_value(self) -> None:
        assert GEO_Y == "geo_y"

    def test_geo_x_accessible_on_detection(self) -> None:
        given = create_given()
        assert given.detection.geo_x == GIVEN_GEO_X

    def test_geo_y_accessible_on_detection(self) -> None:
        given = create_given()
        assert given.detection.geo_y == GIVEN_GEO_Y
