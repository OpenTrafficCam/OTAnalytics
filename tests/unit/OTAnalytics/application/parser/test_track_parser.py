from dataclasses import dataclass
from pathlib import Path
from unittest.mock import Mock

from OTAnalytics.application.parser.track_parser import TrackParser, TrackParseResult


class MockTrackParser(TrackParser):
    def __init__(self, mock_parse_result: Mock) -> None:
        self.__mock_parse_result = mock_parse_result

    def parse(self, file: Path) -> TrackParseResult:
        return self.__mock_parse_result


class TestTrackParser:
    def test_parse_with_existing_georeference_metadata(self) -> None:
        given = setup_with_existing_georeference_metadata()
        target = create_target(given)

        result = target.parse_files([Path("any.ottrk")])

        assert result.georeference_metadata is given.parse_result.georeference_metadata

    def test_parse_with_no_georeference_metadata(self) -> None:
        given = setup_with_no_georeference_metadata()
        target = create_target(given)

        result = target.parse_files([Path("any.ottrk")])

        assert result.georeference_metadata is None


@dataclass
class Given:
    parse_result: Mock


def setup_with_existing_georeference_metadata() -> Given:
    parse_result = Mock()
    parse_result.georeference_metadata = Mock()
    return Given(parse_result)


def setup_with_no_georeference_metadata() -> Given:
    parse_result = Mock()
    parse_result.georeference_metadata = None
    return Given(parse_result)


def create_target(given: Given) -> TrackParser:
    return MockTrackParser(given.parse_result)
