import numpy
import polars as pl
import pytest
from polars import DataFrame

from OTAnalytics.domain import track

CATEGORIES = ["car", "bicyclist", "pedestrian"]
COLOR_PALETTE = {"car": "blue", "bicyclist": "lime", "pedestrian": "red"}
IMAGE_WIDTH = 800
IMAGE_HEIGHT = 600
NUMBER_OF_TRACKS = 100
DETECTIONS_PER_TRACK = 1_000
STEP_SIZE = 2.0
BOX_SIZE = 20.0


def random_walk_tracks(
    number_of_tracks: int = NUMBER_OF_TRACKS,
    detections_per_track: int = DETECTIONS_PER_TRACK,
    seed: int = 42,
) -> DataFrame:
    """Random walk tracks in image coordinates, sorted by track id and occurrence.

    Tracks start inside the image but may leave it, which exercises clipping.
    """
    rng = numpy.random.default_rng(seed)
    starts = rng.uniform((0, 0), (IMAGE_WIDTH, IMAGE_HEIGHT), (number_of_tracks, 1, 2))
    steps = rng.normal(0, STEP_SIZE, (number_of_tracks, detections_per_track, 2))
    xy = (starts + numpy.cumsum(steps, axis=1)).reshape(-1, 2)
    track_ids = numpy.repeat(numpy.arange(number_of_tracks), detections_per_track)
    classifications = numpy.array(CATEGORIES)[track_ids % len(CATEGORIES)]
    return DataFrame(
        {
            track.TRACK_ID: track_ids.astype(str),
            track.OCCURRENCE: numpy.tile(
                numpy.arange(detections_per_track), number_of_tracks
            ),
            track.TRACK_CLASSIFICATION: classifications,
            track.X: xy[:, 0],
            track.Y: xy[:, 1],
            track.W: numpy.full(len(xy), BOX_SIZE),
            track.H: numpy.full(len(xy), BOX_SIZE),
        }
    )


def detections(rows: list[tuple[str, str, float, float]]) -> DataFrame:
    """Detections given as (track id, classification, x, y), in order."""
    return DataFrame(
        rows,
        schema={
            track.TRACK_ID: pl.Utf8,
            track.TRACK_CLASSIFICATION: pl.Utf8,
            track.X: pl.Float64,
            track.Y: pl.Float64,
        },
        orient="row",
    ).with_columns(
        pl.lit(BOX_SIZE).alias(track.W),
        pl.lit(BOX_SIZE).alias(track.H),
    )


@pytest.fixture(scope="session")
def tracks() -> DataFrame:
    return random_walk_tracks()
