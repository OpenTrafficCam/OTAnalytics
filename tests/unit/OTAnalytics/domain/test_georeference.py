import pytest
from pytest import approx

from OTAnalytics.domain.georeference import (
    GeoreferenceMetadata,
    geo_to_pixel,
    pixel_to_geo,
)

# Real values from test_fusion_output_2026-04-14_16-34-59.ottrk.json
GEO_MIN_X = 449199.096512522
GEO_MIN_Y = 5699274.275524861
GEO_MAX_X = 449294.8688478645
GEO_MAX_Y = 5699370.047860203
BEV_WIDTH = 983
BEV_HEIGHT = 983
PADDING = 20
SAMPLE_CRS = "EPSG:25833"

# Known values for geo_to_pixel tests
KNOWN_GEO_X = 449226.28994160134
KNOWN_GEO_Y = 5699327.2198470775
KNOWN_PIXEL_X = 287.7537676212576
KNOWN_PIXEL_Y = 441.6960590287385
# The same detection on the unpadded orthophoto: 20 px padding removed and the
# 943 px drawing area stretched back to 983 px.
KNOWN_ORTHOPHOTO_PIXEL_X = 279.11129753049903
KNOWN_ORTHOPHOTO_PIXEL_Y = 439.5834846490163

ORTHOPHOTO_METADATA = GeoreferenceMetadata(
    geo_min_x=GEO_MIN_X,
    geo_min_y=GEO_MIN_Y,
    geo_max_x=GEO_MAX_X,
    geo_max_y=GEO_MAX_Y,
    birds_eye_view_width=BEV_WIDTH,
    birds_eye_view_height=BEV_HEIGHT,
    padding=0,
    crs=SAMPLE_CRS,
)


@pytest.fixture
def sample_metadata() -> GeoreferenceMetadata:
    return GeoreferenceMetadata(
        geo_min_x=GEO_MIN_X,
        geo_min_y=GEO_MIN_Y,
        geo_max_x=GEO_MAX_X,
        geo_max_y=GEO_MAX_Y,
        birds_eye_view_width=BEV_WIDTH,
        birds_eye_view_height=BEV_HEIGHT,
        padding=PADDING,
        crs=SAMPLE_CRS,
    )


def test_pixel_to_geo_known_detection(sample_metadata: GeoreferenceMetadata) -> None:
    # Known detection from the sample ottrk file:
    # pixel (287.7537676212576, 441.6960590287385) -> geo (449226.28994, 5699327.21984)
    geo_x, geo_y = pixel_to_geo(287.7537676212576, 441.6960590287385, sample_metadata)
    assert geo_x == approx(449226.28994160134, rel=1e-6)
    assert geo_y == approx(5699327.2198470775, rel=1e-6)


def test_pixel_to_geo_top_left_corner(sample_metadata: GeoreferenceMetadata) -> None:
    # Padding pixel maps to geo_min_x, geo_max_y (top-left in geo = min_x, max_y)
    geo_x, geo_y = pixel_to_geo(PADDING, PADDING, sample_metadata)
    assert geo_x == approx(GEO_MIN_X, rel=1e-9)
    assert geo_y == approx(GEO_MAX_Y, rel=1e-9)


def test_pixel_to_geo_bottom_right_corner(
    sample_metadata: GeoreferenceMetadata,
) -> None:
    # (bev_width - padding, bev_height - padding) maps to geo_max_x, geo_min_y
    geo_x, geo_y = pixel_to_geo(
        BEV_WIDTH - PADDING, BEV_HEIGHT - PADDING, sample_metadata
    )
    assert geo_x == approx(GEO_MAX_X, rel=1e-9)
    assert geo_y == approx(GEO_MIN_Y, rel=1e-9)


def test_geo_to_pixel_known_detection(sample_metadata: GeoreferenceMetadata) -> None:
    pixel_x, pixel_y = geo_to_pixel(KNOWN_GEO_X, KNOWN_GEO_Y, sample_metadata)
    assert pixel_x == approx(KNOWN_PIXEL_X, rel=1e-6)
    assert pixel_y == approx(KNOWN_PIXEL_Y, rel=1e-6)


def test_geo_to_pixel_on_unpadded_orthophoto() -> None:
    pixel_x, pixel_y = geo_to_pixel(KNOWN_GEO_X, KNOWN_GEO_Y, ORTHOPHOTO_METADATA)
    assert pixel_x == approx(KNOWN_ORTHOPHOTO_PIXEL_X, rel=1e-9)
    assert pixel_y == approx(KNOWN_ORTHOPHOTO_PIXEL_Y, rel=1e-9)


def test_geo_to_pixel_top_left_of_unpadded_orthophoto_is_origin() -> None:
    pixel_x, pixel_y = geo_to_pixel(GEO_MIN_X, GEO_MAX_Y, ORTHOPHOTO_METADATA)
    assert pixel_x == approx(0.0, abs=1e-6)
    assert pixel_y == approx(0.0, abs=1e-6)
