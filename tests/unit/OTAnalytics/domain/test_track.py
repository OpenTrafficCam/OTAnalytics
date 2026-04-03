from dataclasses import dataclass
from unittest.mock import Mock

from OTAnalytics.domain.track import GEO_X, GEO_Y, Detection


@dataclass
class Given:
    detection: Detection


def create_given() -> Given:
    detection = Mock(spec=Detection)
    detection.geo_x = 449245.82
    detection.geo_y = 5699325.96
    return Given(detection=detection)


class TestDetectionGeoCoordinates:
    def test_geo_x_constant_value(self) -> None:
        assert GEO_X == "geo_x"

    def test_geo_y_constant_value(self) -> None:
        assert GEO_Y == "geo_y"

    def test_geo_x_accessible_on_detection(self) -> None:
        given = create_given()
        assert given.detection.geo_x == 449245.82

    def test_geo_y_accessible_on_detection(self) -> None:
        given = create_given()
        assert given.detection.geo_y == 5699325.96
