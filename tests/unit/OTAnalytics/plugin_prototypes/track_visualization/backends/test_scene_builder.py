import numpy
import pytest
from polars import DataFrame

from OTAnalytics.plugin_prototypes.track_visualization.backends.scene import Symbol
from OTAnalytics.plugin_prototypes.track_visualization.backends.scene_builder import (
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

BLUE_HALF_TRANSPARENT = [0, 0, 255, 128]
BLACK = [0, 0, 0, 255]


class TestTrackGeometrySceneBuilder:
    def test_build_one_polyline_per_track(self, tracks: DataFrame) -> None:
        builder = TrackGeometrySceneBuilder(
            alpha=0.5, thickness=1.5, enable_legend=True
        )

        scene = builder.build(tracks, COLOR_PALETTE)

        assert scene.labels == tuple(CATEGORIES)
        assert scene.legend
        (polylines,) = scene.polylines
        assert polylines.xy.dtype == numpy.float32
        assert polylines.xy.flags.c_contiguous
        assert polylines.xy.shape == (NUMBER_OF_TRACKS * DETECTIONS_PER_TRACK, 2)
        assert polylines.starts.tolist() == list(
            range(0, NUMBER_OF_TRACKS * DETECTIONS_PER_TRACK, DETECTIONS_PER_TRACK)
        )
        expected_categories = numpy.arange(NUMBER_OF_TRACKS) % len(CATEGORIES)
        assert polylines.categories.tolist() == expected_categories.tolist()
        assert polylines.thickness == 1.5
        assert not polylines.closed

    def test_build_colors_with_alpha(self) -> None:
        data = detections([("1", "car", 0, 0), ("1", "car", 1, 1)])
        builder = TrackGeometrySceneBuilder(alpha=0.5, thickness=1, enable_legend=False)

        scene = builder.build(data, COLOR_PALETTE)

        assert scene.colors.dtype == numpy.uint8
        assert scene.colors.tolist() == [BLUE_HALF_TRANSPARENT]

    def test_build_unknown_classification_in_default_color(self) -> None:
        data = detections([("1", "unknown", 0, 0)])
        builder = TrackGeometrySceneBuilder(alpha=1, thickness=1, enable_legend=False)

        scene = builder.build(data, COLOR_PALETTE)

        assert scene.colors.tolist() == [BLACK]

    def test_build_drops_detections_without_coordinates(self) -> None:
        data = detections(
            [("1", "car", 0, 0), ("1", "car", float("nan"), 1), ("1", "car", 2, 2)]
        )
        builder = TrackGeometrySceneBuilder(alpha=1, thickness=1, enable_legend=False)

        scene = builder.build(data, COLOR_PALETTE)

        assert scene.polylines[0].xy.tolist() == [[0, 0], [2, 2]]


class TestTrackStartEndPointSceneBuilder:
    def test_build_first_and_last_detection_of_each_track(self) -> None:
        data = detections(
            [
                ("1", "car", 0, 0),
                ("1", "car", 1, 1),
                ("1", "car", 2, 2),
                ("2", "pedestrian", 10, 10),
                ("2", "pedestrian", 11, 11),
            ]
        )
        builder = TrackStartEndPointSceneBuilder(alpha=1, size=5)

        scene = builder.build(data, COLOR_PALETTE)

        start, end = scene.markers
        assert start.symbol == Symbol.TRIANGLE_RIGHT
        assert start.xy.tolist() == [[0, 0], [10, 10]]
        assert end.symbol == Symbol.SQUARE
        assert end.xy.tolist() == [[2, 2], [11, 11]]
        assert start.categories.tolist() == [0, 1]
        assert scene.labels == ("car", "pedestrian")


class TestPointSceneBuilder:
    def test_build_one_marker_per_detection(self, tracks: DataFrame) -> None:
        builder = PointSceneBuilder(alpha=0.7, size=8, symbol=Symbol.CROSS)

        scene = builder.build(tracks, COLOR_PALETTE)

        (markers,) = scene.markers
        assert len(markers) == len(tracks)
        assert markers.symbol == Symbol.CROSS
        assert markers.size == 8
        assert markers.categories.dtype == numpy.int32


class TestBoundingBoxSceneBuilder:
    def test_build_closed_rectangle_per_detection(self) -> None:
        data = detections([("1", "car", 10, 20)])
        builder = BoundingBoxSceneBuilder(alpha=0.7, thickness=2)

        scene = builder.build(data, COLOR_PALETTE)

        (boxes,) = scene.polylines
        assert boxes.closed
        assert boxes.starts.tolist() == [0]
        assert boxes.xy.tolist() == [
            [10, 20],
            [10 + BOX_SIZE, 20],
            [10 + BOX_SIZE, 20 + BOX_SIZE],
            [10, 20 + BOX_SIZE],
        ]


@pytest.mark.parametrize(
    "builder",
    [
        TrackGeometrySceneBuilder(alpha=1, thickness=1, enable_legend=True),
        TrackStartEndPointSceneBuilder(alpha=1, size=5),
        PointSceneBuilder(alpha=1, size=5, symbol=Symbol.CIRCLE),
        BoundingBoxSceneBuilder(alpha=1, thickness=1),
    ],
)
def test_build_empty_scene_for_empty_data(builder: SceneBuilder) -> None:
    scene = builder.build(DataFrame(), COLOR_PALETTE)

    assert scene.is_empty()
    assert scene.labels == ()
