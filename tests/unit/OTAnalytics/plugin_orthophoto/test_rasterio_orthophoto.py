from dataclasses import dataclass
from pathlib import Path

import numpy
import pytest
import rasterio
from affine import Affine
from pytest import approx

from OTAnalytics.domain.orthophoto import UnsupportedOrthophoto
from OTAnalytics.plugin_orthophoto.rasterio_orthophoto import (
    read_orthophoto_georeference,
    read_orthophoto_image,
)

SHIFTED_UTM_33N = (
    "+proj=tmerc +lat_0=0 +lon_0=15 +k=0.9996 +x_0=50800 +y_0=-5699200"
    " +ellps=GRS80 +units=m +no_defs"
)
TRACKS_CRS = "EPSG:25833"
SIZE = 983
PIXEL_SIZE = 0.09742862191502112
ORIGIN_X = -0.9034874779889105
ORIGIN_Y = 170.0478602033068
ROTATION = 0.01
RGBA_BANDS = 4
# geo_bounds of test_fusion_output_2026-04-22_09-33-10.ottrk, same image.
EXPECTED_MIN_X = 449199.096512522
EXPECTED_MIN_Y = 5699274.275524861
EXPECTED_MAX_X = 449294.8688478645
EXPECTED_MAX_Y = 5699370.047860203
BOUNDS_TOLERANCE = 1e-6
RED = (255, 0, 0, 255)
NORTH_UP = Affine(PIXEL_SIZE, 0, ORIGIN_X, 0, -PIXEL_SIZE, ORIGIN_Y)


@dataclass
class Given:
    file: Path


def create_given(tmp_path: Path) -> Given:
    return Given(file=tmp_path / "map.tiff")


def setup_default(given: Given) -> Given:
    data = numpy.zeros((RGBA_BANDS, SIZE, SIZE), dtype=numpy.uint8)
    data[:, 0, 0] = RED
    write_tiff(given.file, data, NORTH_UP)
    return given


def setup_with_rotation(given: Given) -> Given:
    data = numpy.zeros((RGBA_BANDS, SIZE, SIZE), dtype=numpy.uint8)
    rotated = Affine(PIXEL_SIZE, ROTATION, ORIGIN_X, ROTATION, -PIXEL_SIZE, ORIGIN_Y)
    write_tiff(given.file, data, rotated)
    return given


def setup_with_16_bit(given: Given) -> Given:
    data = numpy.zeros((RGBA_BANDS, SIZE, SIZE), dtype=numpy.uint16)
    write_tiff(given.file, data, NORTH_UP)
    return given


def write_tiff(file: Path, data: numpy.ndarray, transform: Affine) -> None:
    bands, height, width = data.shape
    with rasterio.open(
        file,
        "w",
        driver="GTiff",
        width=width,
        height=height,
        count=bands,
        dtype=data.dtype,
        crs=SHIFTED_UTM_33N,
        transform=transform,
    ) as dataset:
        dataset.write(data)


class TestReadOrthophotoGeoreference:
    def test_bounds_are_expressed_in_the_tracks_crs(self, tmp_path: Path) -> None:
        given = setup_default(create_given(tmp_path))

        actual = read_orthophoto_georeference(given.file, TRACKS_CRS)

        assert (actual.geo_min_x, actual.geo_min_y) == approx(
            (EXPECTED_MIN_X, EXPECTED_MIN_Y), abs=BOUNDS_TOLERANCE
        )
        assert (actual.geo_max_x, actual.geo_max_y) == approx(
            (EXPECTED_MAX_X, EXPECTED_MAX_Y), abs=BOUNDS_TOLERANCE
        )

    def test_image_size_is_the_raster_size_without_padding(
        self, tmp_path: Path
    ) -> None:
        given = setup_default(create_given(tmp_path))

        actual = read_orthophoto_georeference(given.file, TRACKS_CRS)

        assert (actual.birds_eye_view_width, actual.birds_eye_view_height) == (
            SIZE,
            SIZE,
        )
        assert actual.padding == 0
        assert actual.crs == TRACKS_CRS

    def test_rotated_orthophoto_is_unsupported(self, tmp_path: Path) -> None:
        given = setup_with_rotation(create_given(tmp_path))

        with pytest.raises(UnsupportedOrthophoto):
            read_orthophoto_georeference(given.file, TRACKS_CRS)


class TestReadOrthophotoImage:
    def test_image_keeps_size_and_pixels(self, tmp_path: Path) -> None:
        given = setup_default(create_given(tmp_path))

        image = read_orthophoto_image(given.file).as_image()

        assert image.size == (SIZE, SIZE)
        assert image.getpixel((0, 0)) == RED

    def test_image_of_16_bit_orthophoto_is_unsupported(self, tmp_path: Path) -> None:
        given = setup_with_16_bit(create_given(tmp_path))

        with pytest.raises(UnsupportedOrthophoto):
            read_orthophoto_image(given.file)
