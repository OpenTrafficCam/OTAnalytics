import pytest

from OTAnalytics.domain.geometry import (
    Coordinate,
    ImageCoordinate,
    Line,
    Polygon,
    RelativeOffsetCoordinate,
)


class TestLine:
    def test_instantiate_closed_line_raises_value_error(self) -> None:
        coordinates = [
            Coordinate(0, 0),
            Coordinate(1, 0),
            Coordinate(2, 0),
            Coordinate(0, 0),
        ]

        with pytest.raises(ValueError):
            Line(coordinates)

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
