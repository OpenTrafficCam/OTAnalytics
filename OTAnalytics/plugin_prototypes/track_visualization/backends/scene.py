from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import StrEnum

import numpy
from numpy import ndarray

RGBA_CHANNELS = 4
POINTS_PER_INCH = 72
EMPTY_COORDINATES = numpy.empty((0, 2), dtype=numpy.float32)
EMPTY_CATEGORIES = numpy.empty(0, dtype=numpy.int32)
EMPTY_SIZES = numpy.empty(0, dtype=numpy.float32)
EMPTY_STARTS = numpy.empty(0, dtype=numpy.int64)


class Symbol(StrEnum):
    """Marker symbols supported by all array based backends.

    The values match existing plotting library marker names, e.g. matplotlib.
    """

    CIRCLE = "o"
    SQUARE = "s"
    PLUS = "+"
    CROSS = "x"
    TRIANGLE_RIGHT = ">"


def points_to_pixels(points: float, dpi: float) -> float:
    """Convert a length in typographic points to pixels.

    Args:
        points (float): length in points.
        dpi (float): resolution of the image in dots per inch.

    Returns:
        float: length in pixels.
    """
    return points * dpi / POINTS_PER_INCH


@dataclass(frozen=True)
class Viewport:
    """Rectangle of the background image to show, in background image pixels.

    Args:
        x (float): left edge of the shown area.
        y (float): top edge of the shown area.
        width (float): width of the shown area.
        height (float): height of the shown area.
    """

    x: float
    y: float
    width: float
    height: float

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError(
                f"Viewport must have a positive size, got {self.width}x{self.height}"
            )

    @staticmethod
    def full(width: int, height: int) -> "Viewport":
        """Viewport showing the whole image of the given size."""
        return Viewport(0, 0, width, height)

    def to_output(self, xy: ndarray, width: int, height: int) -> ndarray:
        """Map image coordinates into pixel coordinates of an output image.

        Args:
            xy (ndarray): coordinates of shape (n, 2) in background image pixels.
            width (int): width of the output image.
            height (int): height of the output image.

        Returns:
            ndarray: float32 coordinates of shape (n, 2) in output pixels.
        """
        offset = numpy.array([self.x, self.y], dtype=numpy.float32)
        scale = numpy.array(
            [width / self.width, height / self.height], dtype=numpy.float32
        )
        return (xy - offset) * scale


@dataclass(frozen=True)
class MarkerLayer:
    """Markers of one symbol, colored by category.

    Args:
        xy (ndarray): contiguous float32 coordinates of shape (n, 2).
        categories (ndarray): int32 category index per marker of shape (n,).
        symbol (Symbol): symbol to draw at each coordinate.
        size (float): marker diameter in output pixels.
    """

    xy: ndarray
    categories: ndarray
    symbol: Symbol
    size: float

    def __len__(self) -> int:
        return len(self.xy)


@dataclass(frozen=True)
class PolylineLayer:
    """Several polylines stored in one coordinate array, colored by category.

    Polyline i covers the rows `starts[i]` up to (excluding) `starts[i + 1]`.

    Args:
        xy (ndarray): contiguous float32 coordinates of shape (n, 2).
        starts (ndarray): int64 index of the first row of each polyline, ascending.
        categories (ndarray): int32 category index per polyline.
        thickness (float): line width in output pixels.
        closed (bool): whether the last point connects back to the first one.
    """

    xy: ndarray
    starts: ndarray
    categories: ndarray
    thickness: float
    closed: bool = False

    def __len__(self) -> int:
        return len(self.starts)

    def lengths(self) -> ndarray:
        """Number of points of each polyline."""
        return numpy.diff(numpy.append(self.starts, len(self.xy)))


@dataclass(frozen=True)
class Scene:
    """Backend neutral description of one track layer.

    Args:
        labels (tuple[str, ...]): name of each category, indexed by category index.
        colors (ndarray): uint8 RGBA color per category of shape (k, 4). The alpha
            channel holds the transparency of the layer.
        markers (tuple[MarkerLayer, ...]): markers to draw on top of the polylines.
        polylines (tuple[PolylineLayer, ...]): polylines to draw.
        legend (bool): whether to draw a legend of all categories.
    """

    labels: tuple[str, ...] = ()
    colors: ndarray = field(
        default_factory=lambda: numpy.empty((0, RGBA_CHANNELS), dtype=numpy.uint8)
    )
    markers: tuple[MarkerLayer, ...] = ()
    polylines: tuple[PolylineLayer, ...] = ()
    legend: bool = False

    def is_empty(self) -> bool:
        return not any(len(layer) for layer in self.markers) and not any(
            len(layer) for layer in self.polylines
        )


class RasterRenderer(ABC):
    """Renders a scene into a transparent RGBA image."""

    @abstractmethod
    def render(
        self, scene: Scene, viewport: Viewport, width: int, height: int
    ) -> ndarray:
        """Render the scene.

        Args:
            scene (Scene): what to draw.
            viewport (Viewport): area of the background image to show.
            width (int): width of the output image in pixels.
            height (int): height of the output image in pixels.

        Returns:
            ndarray: uint8 RGBA image of shape (height, width, 4) with straight
                (not premultiplied) alpha. Pixels without content are fully
                transparent.
        """
        raise NotImplementedError


def empty_image(width: int, height: int) -> ndarray:
    """Fully transparent RGBA image of the given size."""
    return numpy.zeros((height, width, RGBA_CHANNELS), dtype=numpy.uint8)
