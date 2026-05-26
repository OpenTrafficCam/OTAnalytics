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
