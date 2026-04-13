import pytest
from pytest import approx

from OTAnalytics.domain.otfusion import OtfusionMetadata, pixel_to_geo

# Real values from test_fusion_output_2026-04-13_14-36-10.ottrk.json
GEO_MIN_X = 449199.096512522
GEO_MIN_Y = 5699274.275524861
GEO_MAX_X = 449294.8688478645
GEO_MAX_Y = 5699370.047860203
BEV_WIDTH = 983
BEV_HEIGHT = 983
PADDING = 20


@pytest.fixture
def sample_metadata() -> OtfusionMetadata:
    return OtfusionMetadata(
        geo_min_x=GEO_MIN_X,
        geo_min_y=GEO_MIN_Y,
        geo_max_x=GEO_MAX_X,
        geo_max_y=GEO_MAX_Y,
        bev_width=BEV_WIDTH,
        bev_height=BEV_HEIGHT,
        padding=PADDING,
    )


def test_pixel_to_geo_known_detection(sample_metadata: OtfusionMetadata) -> None:
    # Known detection from the sample ottrk file:
    # pixel (287.7537676212576, 441.6960590287385) -> geo (449226.28994, 5699327.21984)
    geo_x, geo_y = pixel_to_geo(287.7537676212576, 441.6960590287385, sample_metadata)
    assert geo_x == approx(449226.28994160134, rel=1e-6)
    assert geo_y == approx(5699327.2198470775, rel=1e-6)


def test_pixel_to_geo_top_left_corner(sample_metadata: OtfusionMetadata) -> None:
    # Padding pixel maps to geo_min_x, geo_max_y (top-left in geo = min_x, max_y)
    geo_x, geo_y = pixel_to_geo(PADDING, PADDING, sample_metadata)
    assert geo_x == approx(GEO_MIN_X, rel=1e-9)
    assert geo_y == approx(GEO_MAX_Y, rel=1e-9)


def test_pixel_to_geo_bottom_right_corner(sample_metadata: OtfusionMetadata) -> None:
    # (bev_width - padding, bev_height - padding) maps to geo_max_x, geo_min_y
    geo_x, geo_y = pixel_to_geo(
        BEV_WIDTH - PADDING, BEV_HEIGHT - PADDING, sample_metadata
    )
    assert geo_x == approx(GEO_MAX_X, rel=1e-9)
    assert geo_y == approx(GEO_MIN_Y, rel=1e-9)
