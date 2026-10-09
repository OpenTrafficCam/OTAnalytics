from dataclasses import dataclass

import OTAnalytics.plugin_parser.ottrk_dataformat as ottrk_format
from OTAnalytics.plugin_parser.georeference_parsing import (
    GeoreferenceMetadataParsingMixin,
)
from tests.unit.OTAnalytics.plugin_parser.conftest import (
    GEOREF_METADATA,
    SAMPLE_GEOREFERENCE_METADATA_DICT,
)


class TestGeoreferenceParsing:
    def test_returns_metadata_when_georeference_block_present(self) -> None:
        target = create_target()
        result = target.parse_georeference_metadata(SAMPLE_GEOREFERENCE_METADATA_DICT)
        assert result == GEOREF_METADATA

    def test_returns_none_when_georeference_block_absent(self) -> None:
        target = create_target()
        result = target.parse_georeference_metadata({"video": {}})
        assert result is None


def create_target() -> GeoreferenceMetadataParsingMixin:
    return GeoreferenceMetadataParsingMixin()


GEO_COORDINATES_CRS = "EPSG:25833"


@dataclass
class Given:
    metadata: dict


def create_given() -> Given:
    return Given(metadata={})


def setup_with_geo_coordinates_crs(given: Given) -> Given:
    given.metadata[ottrk_format.GEO_COORDINATES] = {
        ottrk_format.CRS: GEO_COORDINATES_CRS
    }
    return given


class TestParseGeoCoordinatesCrs:
    def test_reads_crs_of_geo_coordinates(self) -> None:
        given = setup_with_geo_coordinates_crs(create_given())

        actual = create_target().parse_geo_coordinates_crs(given.metadata)

        assert actual == GEO_COORDINATES_CRS

    def test_missing_block_yields_none(self) -> None:
        given = create_given()

        actual = create_target().parse_geo_coordinates_crs(given.metadata)

        assert actual is None
