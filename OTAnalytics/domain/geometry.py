from dataclasses import dataclass

from OTAnalytics.domain.common import DataclassValidation

X: str = "x"
Y: str = "y"
X1: str = "x1"
X2: str = "x2"


@dataclass(frozen=True)
class Coordinate(DataclassValidation):
    x: float
    y: float

    def to_dict(self) -> dict:
        return {
            X: self.x,
            Y: self.y,
        }

    def to_list(self) -> list[float]:
        return [self.x, self.y]


@dataclass(frozen=True)
class Line(DataclassValidation):
    """A `Line` is a geometry that can consist of multiple line segments.

    Args:
        coordinates (list[Coordinate]): the coordinates defining the line.

    Raises:
        ValueError: if number of coordinates to define a valid line is less than two.
        ValueError: if coordinates define a closed line.
    """

    coordinates: list[Coordinate]

    def _validate(self) -> None:
        if len(self.coordinates) < 2:
            raise ValueError(
                (
                    "Number of coordinates to define a valid line must be "
                    f"greater equal 2, but is {len(self.coordinates)}"
                )
            )

        if self.coordinates[0] == self.coordinates[-1]:
            raise ValueError(("Coordinates define a closed line"))


@dataclass(frozen=True)
class Polygon(DataclassValidation):
    """A polygon is made up of line segments which form a closed polygonal chain.

    Args:
        coordinates (list[Coordinate]): the coordinates defining the polygon.

    Raises:
        ValueError: if coordinates defining the polygon is less than 4.
        ValueError: if coordinates do not define a closed polygonal chain.
    """

    coordinates: list[Coordinate]

    def _validate(self) -> None:
        if len(self.coordinates) < 4:
            raise ValueError(
                (
                    "Number of coordinates to define a valid polygon must be "
                    f"greater equal four, but is {len(self.coordinates)}"
                )
            )

        if self.coordinates[0] != self.coordinates[-1]:
            raise ValueError("Coordinates do not define a closed polygonal chain")


@dataclass(frozen=True)
class DirectionVector2D:
    """Represents a 2-dimensional direction vector.

    Args:
        x1 (float): the first component of the 2-dim direction vector.
        x2 (float): the second component of the 2-dim direction vector.
    """

    x1: float
    x2: float

    def to_dict(self) -> dict:
        return {
            X1: self.x1,
            X2: self.x2,
        }

    def to_list(self) -> list[float]:
        return [self.x1, self.x2]


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
                f"x image coordinate must be greater equal zero, but is {self.x}"
            )
        if self.y < 0:
            raise ValueError(
                f"y image coordinate must be greater equal zero, but is {self.x}"
            )
