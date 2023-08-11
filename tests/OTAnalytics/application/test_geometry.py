from unittest.mock import Mock

import pytest

from OTAnalytics.application.geometry import (
    SectionGeometryBuilder,
    TrackGeometryBuilder,
)
from OTAnalytics.domain.geometry import (
    Coordinate,
    Line,
    Polygon,
    RelativeOffsetCoordinate,
)
from OTAnalytics.domain.section import Section
from OTAnalytics.domain.track import Detection, Track


class TestTrackGeometryBuilder:
    def test_build(self) -> None:
        detection_1 = Mock(spec=Detection)
        detection_1.x = 0
        detection_1.y = 0
        detection_1.w = 1
        detection_1.h = 1

        detection_2 = Mock(spec=Detection)
        detection_2.x = 1
        detection_2.y = 1
        detection_2.w = 1
        detection_2.h = 1

        track = Mock(spec=Track)
        track.detections = [detection_1, detection_2]
        builder = TrackGeometryBuilder()
        result = builder.build(track, RelativeOffsetCoordinate(0.5, 0.5))

        assert result == Line([Coordinate(0.5, 0.5), Coordinate(1.5, 1.5)])


class TestSectionGeometryBuilder:
    @pytest.fixture
    def polygon_coordinates(self) -> list[Coordinate]:
        return [
            Coordinate(0, 0),
            Coordinate(1, 0),
            Coordinate(1, 1),
            Coordinate(0, 1),
            Coordinate(0, 0),
        ]

    @pytest.fixture
    def section(self, polygon_coordinates: list[Coordinate]) -> Mock:
        section = Mock(spec=Section)
        section.get_coordinates.return_value = polygon_coordinates
        return section

    def test_build_as_line(
        self, section: Mock, polygon_coordinates: list[Coordinate]
    ) -> None:
        builder = SectionGeometryBuilder()
        result = builder.build_as_line(section)

        assert isinstance(result, Line)
        assert result.coordinates == polygon_coordinates
        section.get_coordinates.assert_called_once()

    def test_build_as_polygon(
        self, section: Mock, polygon_coordinates: list[Coordinate]
    ) -> None:
        builder = SectionGeometryBuilder()
        result = builder.build_as_polygon(section)

        assert isinstance(result, Polygon)
        assert result.coordinates == polygon_coordinates
        section.get_coordinates.assert_called_once()
