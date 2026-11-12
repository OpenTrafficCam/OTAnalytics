from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator
from unittest.mock import Mock

import pytest

from OTAnalytics.application.parser.track_parser import (
    DetectionMetadata,
    TrackParser,
    TrackParseResult,
)
from OTAnalytics.domain.georeference import GeoreferenceMetadata
from OTAnalytics.domain.otc_classes import OtcClasses
from OTAnalytics.domain.track import Track
from OTAnalytics.domain.track_dataset.track_dataset import (
    IncompatibleGeoreferenceMetadataError,
)
from OTAnalytics.domain.video import VideoMetadata
from OTAnalytics.plugin_datastore.polars_track_store import (
    POLARS_TRACK_GEOMETRY_FACTORY,
    PolarsTrackDataset,
)
from OTAnalytics.plugin_datastore.track_geometry_store.polars_geometry_store import (
    PolarsTrackGeometryDataset,
)
from tests.utils.builders.track_builder import create_track

GEOREF_METADATA = GeoreferenceMetadata(
    geo_min_x=449199.0,
    geo_min_y=5699274.0,
    geo_max_x=449294.0,
    geo_max_y=5699370.0,
    birds_eye_view_width=983,
    birds_eye_view_height=983,
    padding=20,
    crs="EPSG:25833",
)

ALTERNATE_GEOREF_METADATA = GeoreferenceMetadata(
    geo_min_x=1.0,
    geo_min_y=1.0,
    geo_max_x=101.0,
    geo_max_y=101.0,
    birds_eye_view_width=983,
    birds_eye_view_height=983,
    padding=20,
    crs="EPSG:25833",
)


class StubTrackParser(TrackParser):
    def __init__(self, parse_results: list[TrackParseResult]) -> None:
        self.__parse_results_iter: Iterator[TrackParseResult] = iter(parse_results)

    def parse(self, file: Path) -> TrackParseResult:
        return next(self.__parse_results_iter)


class TestTrackParserParseFilesValidation:
    def test_parse_files_with_consistent_metadata_succeeds(self) -> None:
        given = setup_default(
            file_results=[
                result_with_metadata(GEOREF_METADATA, track_id="1"),
                result_with_metadata(GEOREF_METADATA, track_id="2"),
            ]
        )
        target = create_target(given)

        result = target.parse_files(given.files)

        assert result.tracks.georeference_metadata == GEOREF_METADATA

    def test_parse_files_with_mismatched_metadata_raises(self) -> None:
        given = setup_default(
            file_results=[
                result_with_metadata(GEOREF_METADATA, track_id="1"),
                result_with_metadata(ALTERNATE_GEOREF_METADATA, track_id="2"),
            ]
        )
        target = create_target(given)

        with pytest.raises(IncompatibleGeoreferenceMetadataError):
            target.parse_files(given.files)

    def test_parse_files_with_partial_metadata_raises(self) -> None:
        given = setup_default(
            file_results=[
                result_with_metadata(GEOREF_METADATA, track_id="1"),
                result_without_metadata(track_id="2"),
            ]
        )
        target = create_target(given)

        with pytest.raises(IncompatibleGeoreferenceMetadataError):
            target.parse_files(given.files)

    def test_parse_files_with_no_metadata_anywhere_yields_none(self) -> None:
        given = setup_default(
            file_results=[
                result_without_metadata(track_id="1"),
                result_without_metadata(track_id="2"),
            ]
        )
        target = create_target(given)

        result = target.parse_files(given.files)

        assert result.tracks.georeference_metadata is None


@dataclass
class Given:
    file_results: list[TrackParseResult]
    files: list[Path] = field(default_factory=list)


def setup_default(file_results: list[TrackParseResult]) -> Given:
    files = [Path(f"file_{index}.ottrk") for index in range(len(file_results))]
    return Given(file_results=file_results, files=files)


def create_target(given: Given) -> TrackParser:
    return StubTrackParser(given.file_results)


def _track_geometry_factory() -> POLARS_TRACK_GEOMETRY_FACTORY:
    return PolarsTrackGeometryDataset.from_track_dataset


def _build_dataset(
    track_id: str, metadata: GeoreferenceMetadata | None
) -> PolarsTrackDataset:
    track: Track = create_track(track_id, [(1.0, 1.0), (2.0, 2.0)], 1, OtcClasses.CAR)
    dataset = PolarsTrackDataset.from_list([track], _track_geometry_factory())
    if metadata is not None:
        dataset = dataset.with_georeference_metadata(metadata)
    return dataset


def result_with_metadata(
    metadata: GeoreferenceMetadata, track_id: str = "1"
) -> TrackParseResult:
    return TrackParseResult(
        tracks=_build_dataset(track_id, metadata),
        detection_metadata=DetectionMetadata(frozenset(["car"])),
        video_metadata=Mock(spec=VideoMetadata),
    )


def result_without_metadata(track_id: str = "1") -> TrackParseResult:
    return TrackParseResult(
        tracks=_build_dataset(track_id, None),
        detection_metadata=DetectionMetadata(frozenset(["car"])),
        video_metadata=Mock(spec=VideoMetadata),
    )
