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
        coordinates (list[Coordinate]): the coordinates defining the line

    Raises:
        ValueError: if number of coordinates to define a valid line is less than two
        ValueError: if coordinates define a closed line
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

        # if self.coordinates[0] == self.coordinates[-1]:
        #     raise ValueError(("Coordinates define a closed line"))


@dataclass(frozen=True)
class Polygon(DataclassValidation):
    """A polygon is made up of line segments which form a closed polygonal chain.

    Args:
        coordinates (list[Coordinate]): the coordinates defining the polygon

    Raises:
        ValueError: if coordinates defining the polygon is less than 4
        ValueError: if coordinates do not define a closed polygonal chain
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
        x1 (float): the first component of the 2-dim direction vector
        x2 (float): the second component of the 2-dim direction vector
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
        x (float): the x coordinate must be greater equal zero
        y (float): the y coordinate must be greater equal zero
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


@dataclass(frozen=True)
class RelativeOffsetCoordinate(Coordinate):
    """A relative offset coordinate.

    Raises:
        ValueError: if x not in range [0,1]
        ValueError: if y not in range [0,1]

    Args:
        x (float): the x coordinate offset must be in range [0,1]
        y (float): the y coordinate offset must be in range [0,1]
    """

    def _validate(self) -> None:
        if self.x < 0 or self.x > 1:
            raise ValueError(
                (
                    "relative offset coordinate 'x' must be in range [0,1], "
                    f"but is {self.x}"
                )
            )
        if self.y < 0 or self.y > 1:
            raise ValueError(
                (
                    "relative offset coordinate 'y' must be in range [0,1], "
                    f"but is {self.y}"
                )
            )


def calculate_direction_vector(
    x1: float, x2: float, y1: float, y2: float
) -> DirectionVector2D:
    """Calculate direction vector from coordinates x and y.

    Let x = (x1, x2)^T and y = (y1, y2)^T.

    Calculate direction vector with: direction_vector = y - x.

    Args:
        x1 (float): the first component of coordinate x
        x2 (float): the second component of coordinate x
        y1 (float): the first component of coordinate y
        y2 (float): the second component of coordinate y

    Returns:
        DirectionVector2D: the two dimensional direction vector
    """
    return DirectionVector2D(x1=y1 - x1, x2=y2 - x2)
