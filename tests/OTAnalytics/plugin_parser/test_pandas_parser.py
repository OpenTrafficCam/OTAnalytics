from unittest.mock import Mock

import pytest

from OTAnalytics.domain.track_dataset.track_dataset import TRACK_GEOMETRY_FACTORY
from OTAnalytics.domain.track_repository import TrackRepository
from OTAnalytics.plugin_datastore.track_geometry_store.shapely_store import (
    ShapelyTrackGeometryDataset,
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
from tests.utils.assertions import assert_equal_track_properties
from tests.utils.builders.track_builder import (
    TrackBuilder,
    track_builder_with_sample_data,
)


@pytest.fixture
def track_geometry_factory() -> TRACK_GEOMETRY_FACTORY:
    return ShapelyTrackGeometryDataset.from_track_dataset


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
        parser: DetectionParser,
        track_geometry_factory: TRACK_GEOMETRY_FACTORY,
    ) -> None:
        input_file = "tests/data/tracks.ottrk"
        track_builder = track_builder_with_sample_data(input_file)
        detections: list[dict] = track_builder.build_serialized_detections()

        metadata_video = track_builder.get_metadata()[ottrk_dataformat.VIDEO]
        result_sorted_input = parser.parse_tracks(
            detections, metadata_video, input_file
        ).as_list()
        unsorted_detections = [detections[-1], detections[0]] + detections[1:-1]
        result_unsorted_input = parser.parse_tracks(
            unsorted_detections, metadata_video, input_file
        ).as_list()

        expected_sorted = PandasTrackDataset.from_list(
            [track_builder.build_track()],
            track_geometry_factory,
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
        track_length_limit: TrackLengthLimit,
        track_geometry_factory: TRACK_GEOMETRY_FACTORY,
    ) -> None:
        input_file = "tests/data/tracks.ottrk"
        track_builder = track_builder_with_sample_data(input_file)
        parser = PandasDetectionParser(
            PandasByMaxConfidence(), track_geometry_factory, track_length_limit
        )
        detections: list[dict] = track_builder.build_serialized_detections()

        metadata_video = track_builder.get_metadata()[ottrk_dataformat.VIDEO]
        result_sorted_input = parser.parse_tracks(
            detections, metadata_video, input_file
        ).as_list()

        assert len(result_sorted_input) == 0

    def test_can_parse_tracks_with_empty_detections(
        self,
        parser: DetectionParser,
        track_geometry_factory: TRACK_GEOMETRY_FACTORY,
    ) -> None:
        """
        #Bugfix https://openproject.platomo.de/projects/001-opentrafficcam-live/work_packages/5291

        @bug by randy-seng
        """  # noqa
        track_builder = TrackBuilder()
        actual = parser.parse_tracks(
            detections=[],
            metadata_video=track_builder.get_metadata()[ottrk_dataformat.VIDEO],
            input_file=track_builder.input_file,
        )
        assert actual.empty
        assert isinstance(actual, PandasTrackDataset)
