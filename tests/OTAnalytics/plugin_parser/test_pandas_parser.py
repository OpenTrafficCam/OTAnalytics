from unittest.mock import Mock

import pytest

from OTAnalytics.domain.track import TRACK_GEOMETRY_FACTORY
from OTAnalytics.domain.track_repository import TrackRepository
from OTAnalytics.plugin_datastore.track_geometry_store.pygeos_store import (
    PygeosTrackGeometryDataset,
)
from OTAnalytics.plugin_datastore.track_store import (
    PandasByMaxConfidence,
    PandasTrackDataset,
)
from OTAnalytics.plugin_parser import ottrk_dataformat
from OTAnalytics.plugin_parser.otvision_parser import (
    DEFAULT_TRACK_LENGTH_LIMIT,
    DetectionParser,
    TrackLengthLimit,
)
from OTAnalytics.plugin_parser.pandas_parser import PandasDetectionParser
from tests.conftest import TrackBuilder, assert_equal_track_properties


@pytest.fixture
def track_builder_setup_with_sample_data(track_builder: TrackBuilder) -> TrackBuilder:
    return append_sample_data(track_builder, frame_offset=0, microsecond_offset=0)


@pytest.fixture
def track_geometry_factory() -> TRACK_GEOMETRY_FACTORY:
    return PygeosTrackGeometryDataset.from_track_dataset


def append_sample_data(
    track_builder: TrackBuilder,
    frame_offset: int = 0,
    microsecond_offset: int = 0,
) -> TrackBuilder:
    track_builder.add_frame(frame_offset + 1)
    track_builder.add_microsecond(microsecond_offset + 1)
    track_builder.append_detection()

    track_builder.add_frame(frame_offset + 2)
    track_builder.add_microsecond(microsecond_offset + 2)
    track_builder.append_detection()

    track_builder.add_frame(frame_offset + 3)
    track_builder.add_microsecond(microsecond_offset + 3)
    track_builder.append_detection()

    track_builder.add_frame(frame_offset + 4)
    track_builder.add_microsecond(microsecond_offset + 4)
    track_builder.append_detection()

    track_builder.add_frame(frame_offset + 5)
    track_builder.add_microsecond(microsecond_offset + 5)
    track_builder.append_detection()

    return track_builder


@pytest.fixture
def mocked_track_repository() -> Mock:
    repository = Mock(spec=TrackRepository)
    repository.get_for.return_value = None
    return repository


class TestPandasDetectionParser:
    @pytest.fixture
    def parser(self, track_geometry_factory: TRACK_GEOMETRY_FACTORY) -> DetectionParser:
        return PandasDetectionParser(
            PandasByMaxConfidence(),
            track_geometry_factory,
            track_length_limit=DEFAULT_TRACK_LENGTH_LIMIT,
        )

    def test_parse_tracks(
        self,
        track_builder_setup_with_sample_data: TrackBuilder,
        parser: DetectionParser,
        track_geometry_factory: TRACK_GEOMETRY_FACTORY,
    ) -> None:
        detections: list[
            dict
        ] = track_builder_setup_with_sample_data.build_serialized_detections()

        metadata_video = track_builder_setup_with_sample_data.get_metadata()[
            ottrk_dataformat.VIDEO
        ]
        result_sorted_input = parser.parse_tracks(detections, metadata_video).as_list()
        unsorted_detections = [detections[-1], detections[0]] + detections[1:-1]
        result_unsorted_input = parser.parse_tracks(
            unsorted_detections, metadata_video
        ).as_list()

        expected_sorted = PandasTrackDataset.from_list(
            [track_builder_setup_with_sample_data.build_track()], track_geometry_factory
        ).as_list()

        for sorted, expected in zip(result_sorted_input, expected_sorted):
            assert_equal_track_properties(sorted, expected)
        for unsorted, expected in zip(result_unsorted_input, expected_sorted):
            assert_equal_track_properties(unsorted, expected)

    @pytest.mark.parametrize(
        "track_length_limit",
        [
            TrackLengthLimit(20, 12000),
            TrackLengthLimit(0, 4),
        ],
    )
    def test_parse_tracks_consider_minimum_length(
        self,
        mocked_track_repository: Mock,
        track_builder_setup_with_sample_data: TrackBuilder,
        track_length_limit: TrackLengthLimit,
        track_geometry_factory: TRACK_GEOMETRY_FACTORY,
    ) -> None:
        parser = PandasDetectionParser(
            PandasByMaxConfidence(), track_geometry_factory, track_length_limit
        )
        detections: list[
            dict
        ] = track_builder_setup_with_sample_data.build_serialized_detections()

        metadata_video = track_builder_setup_with_sample_data.get_metadata()[
            ottrk_dataformat.VIDEO
        ]
        result_sorted_input = parser.parse_tracks(detections, metadata_video).as_list()

        assert len(result_sorted_input) == 0
