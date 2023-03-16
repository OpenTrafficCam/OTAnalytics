from dataclasses import dataclass

from OTAnalytics.domain.common import DataclassValidation


@dataclass(frozen=True)
class Coordinate(DataclassValidation):
    x: float
    y: float


@dataclass(frozen=True)
class Line(DataclassValidation):
    start: Coordinate
    end: Coordinate

    def _validate(self) -> None:
        if self.start == self.end:
            raise ValueError(
                (
                    "Start and end point of coordinate must be different to be a line, "
                    "but are same"
                )
            )


@dataclass(frozen=True)
class Polygon(DataclassValidation):
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
            raise ValueError("Coordinates don't define a closed area")


@dataclass(frozen=True)
class DirectionVector2D:
    """Represents a 2-dimensional direction vector.

    Args:
        x1 (float): the first component of the 2-dim direction vector.
        x2 (float): the second component of the 2-dim direction vector.
    """

    x1: float
    x2: float


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
