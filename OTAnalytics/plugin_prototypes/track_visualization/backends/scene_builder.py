from abc import ABC, abstractmethod
from typing import Mapping

import numpy
import polars as pl
from matplotlib import colors as mcolors
from numpy import ndarray
from polars import DataFrame

from OTAnalytics.domain import track
from OTAnalytics.plugin_prototypes.track_visualization.backends.scene import (
    MarkerLayer,
    PolylineLayer,
    Scene,
    Symbol,
)

DEFAULT_COLOR = "black"
MAX_COLOR_VALUE = 255
CATEGORY = "category"
IS_START = "is_start"
COORDINATE_COLUMNS = [track.X, track.Y]


class SceneBuilder(ABC):
    """Builds a backend neutral scene from the detections of a DataFrame.

    Each builder converts the DataFrame into numpy arrays exactly once per call. All
    further processing works on whole arrays.
    """

    @abstractmethod
    def build(self, data: DataFrame, color_palette: Mapping[str, str]) -> Scene:
        """Build the scene for the given detections.

        Args:
            data (DataFrame): detections sorted by track id and occurrence.
            color_palette (Mapping[str, str]): color name per classification.

        Returns:
            Scene: what to draw.
        """
        raise NotImplementedError


class CategoryColors:
    """Assigns a category index and an RGBA color to each classification.

    Categories are numbered in order of first appearance, like the legend of the
    matplotlib plotters.
    """

    def __init__(self, color_palette: Mapping[str, str], alpha: float) -> None:
        self._color_palette = color_palette
        self._alpha = alpha

    def encode(self, data: DataFrame) -> tuple[DataFrame, tuple[str, ...], ndarray]:
        """Add the column CATEGORY holding the category index of each row.

        Args:
            data (DataFrame): detections with a classification column.

        Returns:
            tuple[DataFrame, tuple[str, ...], ndarray]: data with category index,
                label per category and uint8 RGBA color per category.
        """
        classification = pl.col(track.TRACK_CLASSIFICATION).cast(pl.Utf8)
        labels: tuple[str, ...] = tuple(
            data.select(classification.unique(maintain_order=True)).to_series()
        )
        mapping = {label: index for index, label in enumerate(labels)}
        encoded = data.with_columns(
            classification.replace_strict(mapping, return_dtype=pl.Int32).alias(
                CATEGORY
            )
        )
        return encoded, labels, self._to_rgba(labels)

    def _to_rgba(self, labels: tuple[str, ...]) -> ndarray:
        colors = numpy.array(
            [
                mcolors.to_rgba(
                    self._color_palette.get(label, DEFAULT_COLOR), alpha=self._alpha
                )
                for label in labels
            ],
            dtype=numpy.float64,
        ).reshape(-1, 4)
        return numpy.round(colors * MAX_COLOR_VALUE).astype(numpy.uint8)


def to_coordinates(data: DataFrame, columns: list[str] = COORDINATE_COLUMNS) -> ndarray:
    """Convert coordinate columns into one contiguous float32 array of shape (n, 2)."""
    return numpy.ascontiguousarray(
        data.select(columns).to_numpy(), dtype=numpy.float32
    ).reshape(-1, len(columns))


def track_starts(data: DataFrame) -> ndarray:
    """Index of the first detection of each track. Expects data sorted by track."""
    is_start = (pl.col(track.TRACK_ID) != pl.col(track.TRACK_ID).shift(1)).fill_null(
        True
    )
    return data.select(is_start.arg_true()).to_series().to_numpy().astype(numpy.int64)


def finite_coordinates(data: DataFrame) -> DataFrame:
    """Drop detections without finite coordinates, which no backend can draw."""
    return data.filter(pl.col(track.X).is_finite() & pl.col(track.Y).is_finite())


class TrackGeometrySceneBuilder(SceneBuilder):
    """One polyline per track, like `TrackGeometryPlotter`."""

    def __init__(self, alpha: float, thickness: float, enable_legend: bool) -> None:
        self._alpha = alpha
        self._thickness = thickness
        self._enable_legend = enable_legend

    def build(self, data: DataFrame, color_palette: Mapping[str, str]) -> Scene:
        if data.is_empty():
            return Scene()
        data, labels, colors = CategoryColors(color_palette, self._alpha).encode(
            finite_coordinates(data)
        )
        starts = track_starts(data)
        categories = data.get_column(CATEGORY).to_numpy()
        polylines = PolylineLayer(
            xy=to_coordinates(data),
            starts=starts,
            categories=categories[starts].astype(numpy.int32),
            thickness=self._thickness,
        )
        return Scene(
            labels=labels,
            colors=colors,
            polylines=(polylines,),
            legend=self._enable_legend,
        )


class TrackStartEndPointSceneBuilder(SceneBuilder):
    """Start and end marker per track, like `TrackStartEndPointPlotter`."""

    def __init__(
        self,
        alpha: float,
        size: float,
        start_symbol: Symbol = Symbol.TRIANGLE_RIGHT,
        end_symbol: Symbol = Symbol.SQUARE,
    ) -> None:
        self._alpha = alpha
        self._size = size
        self._start_symbol = start_symbol
        self._end_symbol = end_symbol

    def build(self, data: DataFrame, color_palette: Mapping[str, str]) -> Scene:
        if data.is_empty():
            return Scene()
        data, labels, colors = CategoryColors(color_palette, self._alpha).encode(
            finite_coordinates(data)
        )
        xy = to_coordinates(data)
        categories = data.get_column(CATEGORY).to_numpy().astype(numpy.int32)
        starts = track_starts(data)
        ends = numpy.append(starts[1:], len(xy)) - 1
        return Scene(
            labels=labels,
            colors=colors,
            markers=(
                self._marker_layer(xy, categories, starts, self._start_symbol),
                self._marker_layer(xy, categories, ends, self._end_symbol),
            ),
        )

    def _marker_layer(
        self, xy: ndarray, categories: ndarray, rows: ndarray, symbol: Symbol
    ) -> MarkerLayer:
        return MarkerLayer(
            xy=numpy.ascontiguousarray(xy[rows]),
            categories=categories[rows],
            symbol=symbol,
            size=self._size,
        )


class PointSceneBuilder(SceneBuilder):
    """One marker per detection, like `TrackPointPlotter`."""

    def __init__(self, alpha: float, size: float, symbol: Symbol) -> None:
        self._alpha = alpha
        self._size = size
        self._symbol = symbol

    def build(self, data: DataFrame, color_palette: Mapping[str, str]) -> Scene:
        if data.is_empty():
            return Scene()
        data, labels, colors = CategoryColors(color_palette, self._alpha).encode(
            finite_coordinates(data)
        )
        markers = MarkerLayer(
            xy=to_coordinates(data),
            categories=data.get_column(CATEGORY).to_numpy().astype(numpy.int32),
            symbol=self._symbol,
            size=self._size,
        )
        return Scene(labels=labels, colors=colors, markers=(markers,))


class BoundingBoxSceneBuilder(SceneBuilder):
    """One closed rectangle per detection, like `TrackBoundingBoxPlotter`."""

    CORNERS = 4

    def __init__(self, alpha: float, thickness: float) -> None:
        self._alpha = alpha
        self._thickness = thickness

    def build(self, data: DataFrame, color_palette: Mapping[str, str]) -> Scene:
        if data.is_empty():
            return Scene()
        data, labels, colors = CategoryColors(color_palette, self._alpha).encode(
            finite_coordinates(data)
        )
        boxes = to_coordinates(data, [track.X, track.Y, track.W, track.H])
        x, y, w, h = boxes.T
        corners = numpy.stack(
            [
                numpy.stack([x, y], axis=1),
                numpy.stack([x + w, y], axis=1),
                numpy.stack([x + w, y + h], axis=1),
                numpy.stack([x, y + h], axis=1),
            ],
            axis=1,
        )
        polylines = PolylineLayer(
            xy=numpy.ascontiguousarray(corners.reshape(-1, 2), dtype=numpy.float32),
            starts=numpy.arange(len(boxes), dtype=numpy.int64) * self.CORNERS,
            categories=data.get_column(CATEGORY).to_numpy().astype(numpy.int32),
            thickness=self._thickness,
            closed=True,
        )
        return Scene(labels=labels, colors=colors, polylines=(polylines,))
