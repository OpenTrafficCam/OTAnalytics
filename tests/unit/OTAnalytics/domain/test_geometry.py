import math

import pytest

from OTAnalytics.domain.geometry import (
    Coordinate,
    DirectionVector2D,
    ImageCoordinate,
    Line,
    Polygon,
    RelativeOffsetCoordinate,
    apply_offset,
    calculate_direction_vector,
)


class TestLine:
    def test_instantiate_closed_line(self) -> None:
        coordinates = [
            Coordinate(0, 0),
            Coordinate(1, 0),
            Coordinate(2, 0),
            Coordinate(0, 0),
        ]

        line = Line(coordinates)
        assert line.coordinates == coordinates

    def test_instantiate_line_with_one_coordinate_raises_value_error(self) -> None:
        coordinates = [Coordinate(0, 0)]

        with pytest.raises(ValueError):
            Line(coordinates)

    def test_instantiate_line_with_valid_coordinates(self) -> None:
        coordinates = [Coordinate(0, 0), Coordinate(1, 0)]
        line = Line(coordinates)
        assert line.coordinates == coordinates


class TestPolygon:
    def test_instantiate_polygon_with_valid_coordinates(self) -> None:
        coordinates = [
            Coordinate(0, 0),
            Coordinate(1, 0),
            Coordinate(2, 0),
            Coordinate(0, 0),
        ]
        polygon = Polygon(coordinates)
        assert polygon.coordinates == coordinates

    def test_instantiate_not_closed_raises_value_error(self) -> None:
        coordinates = [
            Coordinate(0, 0),
            Coordinate(1, 0),
            Coordinate(2, 0),
            Coordinate(3, 0),
        ]
        with pytest.raises(ValueError):
            Polygon(coordinates)

    def test_instantiate_with_not_enough_coordinates_raises_value_error(self) -> None:
        coordinates = [
            Coordinate(0, 0),
            Coordinate(1, 0),
            Coordinate(2, 0),
        ]
        with pytest.raises(ValueError):
            Polygon(coordinates)


class TestImageCoordinate:
    @pytest.mark.parametrize("x,y", [(-1, 0), (0, -1)])
    def test_instantiate_with_invalid_xy_values_raises_value_error(
        self, x: float, y: float
    ) -> None:
        with pytest.raises(ValueError):
            ImageCoordinate(x, y)

    def test_instantiate_with_valid_xy_values(self) -> None:
        coord = ImageCoordinate(0, 0)
        assert coord.x == 0
        assert coord.y == 0


class TestRelativeOffset:
    @pytest.mark.parametrize("x,y", [(-1, 0), (0, -1), (0, 10), (10, 0), (10, 10)])
    def test_instantiate_with_invalid_xy_values_raises_value_error(
        self, x: float, y: float
    ) -> None:
        with pytest.raises(ValueError):
            RelativeOffsetCoordinate(x, y)

    def test_instantiate_with_valid_xy_values(self) -> None:
        offset = RelativeOffsetCoordinate(0, 0)
        assert offset.x == 0
        assert offset.y == 0


class TestCalculateDirectionVector:
    def test_calculate_direction_vector(self) -> None:
        result = calculate_direction_vector(0, 0, 1, 1)
        assert result == DirectionVector2D(1 / math.sqrt(2), 1 / math.sqrt(2))

    def test_calculate_direction_vector_with_zero_length_returns_zero_vector(
        self,
    ) -> None:
        """
        #Bug https://openproject.platomo.de/projects/001-opentrafficcam-live/work_packages/7660
        """  # noqa
        actual = calculate_direction_vector(0, 0, 0, 0)
        expected = DirectionVector2D(0, 0)
        assert actual == expected


def test_apply_offset() -> None:
    result = apply_offset(x=0, y=0, w=1, h=1, offset=RelativeOffsetCoordinate(0.5, 0.5))

    assert result == (0.5, 0.5)
