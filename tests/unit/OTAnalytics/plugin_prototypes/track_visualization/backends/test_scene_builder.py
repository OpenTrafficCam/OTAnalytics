import numpy
import pytest
from polars import DataFrame

from OTAnalytics.plugin_prototypes.track_visualization.backends.scene import Symbol
from OTAnalytics.plugin_prototypes.track_visualization.backends.scene_builder import (
    DEFAULT_COLOR,
    MAX_COLOR_VALUE,
    BoundingBoxSceneBuilder,
    PointSceneBuilder,
    SceneBuilder,
    TrackGeometrySceneBuilder,
    TrackStartEndPointSceneBuilder,
)
from tests.unit.OTAnalytics.plugin_prototypes.track_visualization.backends.conftest import (  # noqa
    BOX_SIZE,
    CATEGORIES,
    COLOR_PALETTE,
    DETECTIONS_PER_TRACK,
    NUMBER_OF_TRACKS,
    detections,
)

OPAQUE = 1.0
HALF_TRANSPARENT = 0.5
TRANSLUCENT = 0.7
THICKNESS = 1.0
THICK = 1.5
MARKER_SIZE = 5.0
LARGE_MARKER_SIZE = 8.0

CAR = "car"
PEDESTRIAN = "pedestrian"
UNKNOWN = "unknown"
FIRST_TRACK = "1"
SECOND_TRACK = "2"

BOX_X = 10.0
BOX_Y = 20.0


def rgba(rgb: tuple[int, int, int], alpha: float) -> list[int]:
    return [*rgb, round(alpha * MAX_COLOR_VALUE)]


def diagonal(start: float, count: int) -> list[tuple[float, float]]:
    """Points on the diagonal x == y, starting at start with step one."""
    return [(start + offset, start + offset) for offset in range(count)]


class TestTrackGeometrySceneBuilder:
    def test_build_one_polyline_per_track(self, tracks: DataFrame) -> None:
        builder = TrackGeometrySceneBuilder(
            alpha=HALF_TRANSPARENT, thickness=THICK, enable_legend=True
        )

        scene = builder.build(tracks, COLOR_PALETTE)

        number_of_detections = NUMBER_OF_TRACKS * DETECTIONS_PER_TRACK
        assert scene.labels == tuple(CATEGORIES)
        assert scene.legend
        (polylines,) = scene.polylines
        assert polylines.xy.dtype == numpy.float32
        assert polylines.xy.flags.c_contiguous
        assert polylines.xy.shape == (number_of_detections, 2)
        assert polylines.starts.tolist() == list(
            range(0, number_of_detections, DETECTIONS_PER_TRACK)
        )
        expected_categories = numpy.arange(NUMBER_OF_TRACKS) % len(CATEGORIES)
        assert polylines.categories.tolist() == expected_categories.tolist()
        assert polylines.thickness == THICK
        assert not polylines.closed

    def test_build_colors_with_alpha(self) -> None:
        data = detections([(FIRST_TRACK, CAR, x, y) for x, y in diagonal(0, 2)])
        builder = TrackGeometrySceneBuilder(
            alpha=HALF_TRANSPARENT, thickness=THICKNESS, enable_legend=False
        )

        scene = builder.build(data, COLOR_PALETTE)

        assert scene.colors.dtype == numpy.uint8
        assert scene.colors.tolist() == [rgba(COLOR_PALETTE[CAR], HALF_TRANSPARENT)]

    def test_build_unknown_classification_in_default_color(self) -> None:
        data = detections([(FIRST_TRACK, UNKNOWN, 0, 0)])
        builder = TrackGeometrySceneBuilder(
            alpha=OPAQUE, thickness=THICKNESS, enable_legend=False
        )

        scene = builder.build(data, COLOR_PALETTE)

        assert scene.colors.tolist() == [rgba(DEFAULT_COLOR, OPAQUE)]

    def test_build_drops_detections_without_coordinates(self) -> None:
        first, missing, last = diagonal(0, 3)
        data = detections(
            [
                (FIRST_TRACK, CAR, *first),
                (FIRST_TRACK, CAR, float("nan"), missing[1]),
                (FIRST_TRACK, CAR, *last),
            ]
        )
        builder = TrackGeometrySceneBuilder(
            alpha=OPAQUE, thickness=THICKNESS, enable_legend=False
        )

        scene = builder.build(data, COLOR_PALETTE)

        assert scene.polylines[0].xy.tolist() == [list(first), list(last)]


class TestTrackStartEndPointSceneBuilder:
    def test_build_first_and_last_detection_of_each_track(self) -> None:
        car_points = diagonal(0, 3)
        pedestrian_points = diagonal(10, 2)
        data = detections(
            [(FIRST_TRACK, CAR, x, y) for x, y in car_points]
            + [(SECOND_TRACK, PEDESTRIAN, x, y) for x, y in pedestrian_points]
        )
        builder = TrackStartEndPointSceneBuilder(alpha=OPAQUE, size=MARKER_SIZE)

        scene = builder.build(data, COLOR_PALETTE)

        start, end = scene.markers
        assert start.symbol == Symbol.TRIANGLE_RIGHT
        assert start.xy.tolist() == [list(car_points[0]), list(pedestrian_points[0])]
        assert end.symbol == Symbol.SQUARE
        assert end.xy.tolist() == [list(car_points[-1]), list(pedestrian_points[-1])]
        assert start.categories.tolist() == [0, 1]
        assert scene.labels == (CAR, PEDESTRIAN)


class TestPointSceneBuilder:
    def test_build_one_marker_per_detection(self, tracks: DataFrame) -> None:
        builder = PointSceneBuilder(
            alpha=TRANSLUCENT, size=LARGE_MARKER_SIZE, symbol=Symbol.CROSS
        )

        scene = builder.build(tracks, COLOR_PALETTE)

        (markers,) = scene.markers
        assert len(markers) == len(tracks)
        assert markers.symbol == Symbol.CROSS
        assert markers.size == LARGE_MARKER_SIZE
        assert markers.categories.dtype == numpy.int32


class TestBoundingBoxSceneBuilder:
    def test_build_closed_rectangle_per_detection(self) -> None:
        data = detections([(FIRST_TRACK, CAR, BOX_X, BOX_Y)])
        builder = BoundingBoxSceneBuilder(alpha=TRANSLUCENT, thickness=THICK)

        scene = builder.build(data, COLOR_PALETTE)

        (boxes,) = scene.polylines
        assert boxes.closed
        assert boxes.starts.tolist() == [0]
        assert boxes.xy.tolist() == [
            [BOX_X, BOX_Y],
            [BOX_X + BOX_SIZE, BOX_Y],
            [BOX_X + BOX_SIZE, BOX_Y + BOX_SIZE],
            [BOX_X, BOX_Y + BOX_SIZE],
        ]


@pytest.mark.parametrize(
    "builder",
    [
        TrackGeometrySceneBuilder(
            alpha=OPAQUE, thickness=THICKNESS, enable_legend=True
        ),
        TrackStartEndPointSceneBuilder(alpha=OPAQUE, size=MARKER_SIZE),
        PointSceneBuilder(alpha=OPAQUE, size=MARKER_SIZE, symbol=Symbol.CIRCLE),
        BoundingBoxSceneBuilder(alpha=OPAQUE, thickness=THICKNESS),
    ],
)
def test_build_empty_scene_for_empty_data(builder: SceneBuilder) -> None:
    scene = builder.build(DataFrame(), COLOR_PALETTE)

    assert scene.is_empty()
    assert scene.labels == ()
