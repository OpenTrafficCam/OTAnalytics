from dataclasses import dataclass

from OTAnalytics.domain.common import DataclassValidation
from OTAnalytics.domain.geometry import Coordinate


@dataclass(frozen=True)
class Section(DataclassValidation):
    """
    Sections define virtual detectors to generate vehicle events.

    Args:
        id (str): the section id.
    """

    id: str


@dataclass(frozen=True)
class LineSection(Section):
    """
    A line section is defined by two coordinates.

    Args:
        start (Coordinate): the start coordinate.
        end (Coordinate): the end coordinate.
    """

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
class Area(Section):
    """An area is defined by `[x1, x2, ..., x_n]` a list of coordinates
    where n is a natural number and `x1 = x_n`.

    Args:
        coordinates (list[Coordinate]): area defined by list of coordinates.
    """

    coordinates: list[Coordinate]

    def _validate(self) -> None:
        if len(self.coordinates) < 3:
            raise ValueError(
                (
                    "Number of coordinates to define a valid area must be "
                    f"greater equal three, but is {len(self.coordinates)}"
                )
            )

        if self.coordinates[0] != self.coordinates[-1]:
            raise ValueError("Coordinates don't define a closed area")
