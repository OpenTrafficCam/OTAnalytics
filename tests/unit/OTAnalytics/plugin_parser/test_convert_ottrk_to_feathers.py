"""Tests for the convert_ottrk_to_feathers module."""

from unittest.mock import Mock

import OTAnalytics.plugin_parser.ottrk_dataformat as ottrk_format
from OTAnalytics.application.parser.track_parser import (
    DetectionMetadata,
    TrackParseResult,
)
from OTAnalytics.domain.georeference import GeoreferenceMetadata
from OTAnalytics.domain.video import VideoMetadata
from OTAnalytics.plugin_parser.convert_ottrk_to_feathers import create_metadata_dict

GIVEN_METADATA = GeoreferenceMetadata(
    geo_min_x=449199.0,
    geo_min_y=5699274.0,
    geo_max_x=449294.0,
    geo_max_y=5699370.0,
    birds_eye_view_width=983,
    birds_eye_view_height=983,
    padding=20,
    crs="EPSG:25833",
)


def _make_parse_result(
    georeference_metadata: GeoreferenceMetadata | None,
) -> TrackParseResult:
    tracks = Mock()
    tracks.georeference_metadata = georeference_metadata
    return TrackParseResult(
        tracks=tracks,
        detection_metadata=DetectionMetadata(frozenset(["car"])),
        video_metadata=Mock(spec=VideoMetadata),
    )


class TestCreateMetadataDict:
    def test_includes_georeference_metadata_when_present(self) -> None:
        parse_result = _make_parse_result(GIVEN_METADATA)

        result = create_metadata_dict(parse_result)

        assert ottrk_format.GEOREFERENCE in result
        geo = result[ottrk_format.GEOREFERENCE]
        bounds = geo[ottrk_format.GEO_BOUNDS]
        bev_size = geo[ottrk_format.BIRDS_EYE_VIEW_SIZE]
        assert bounds[ottrk_format.GEO_BOUNDS_MIN_X] == GIVEN_METADATA.geo_min_x
        assert bounds[ottrk_format.GEO_BOUNDS_MIN_Y] == GIVEN_METADATA.geo_min_y
        assert bounds[ottrk_format.GEO_BOUNDS_MAX_X] == GIVEN_METADATA.geo_max_x
        assert bounds[ottrk_format.GEO_BOUNDS_MAX_Y] == GIVEN_METADATA.geo_max_y
        assert (
            bev_size[ottrk_format.BIRDS_EYE_VIEW_WIDTH]
            == GIVEN_METADATA.birds_eye_view_width
        )
        assert (
            bev_size[ottrk_format.BIRDS_EYE_VIEW_HEIGHT]
            == GIVEN_METADATA.birds_eye_view_height
        )
        assert geo[ottrk_format.BEV_PADDING] == GIVEN_METADATA.padding
        assert geo[ottrk_format.CRS] == GIVEN_METADATA.crs

    def test_omits_georeference_metadata_when_none(self) -> None:
        parse_result = _make_parse_result(None)

        result = create_metadata_dict(parse_result)

        assert ottrk_format.GEOREFERENCE not in result
