from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator
from unittest.mock import Mock

import pytest

from OTAnalytics.application.state import TracksMetadata, VideosMetadata
from OTAnalytics.domain.track import Track, TrackClassificationCalculator, TrackId
from OTAnalytics.domain.track_dataset.track_dataset import TrackDataset
from OTAnalytics.domain.track_repository import TrackRepository
from OTAnalytics.domain.video import VideoMetadata
from OTAnalytics.plugin_datastore.python_track_store import (
    ByMaxConfidence,
    PythonTrackDataset,
)
from OTAnalytics.plugin_datastore.track_geometry_store.shapely_store import (
    ShapelyTrackGeometryDataset,
)
from OTAnalytics.plugin_datastore.track_store import (
    PandasByMaxConfidence,
    PandasTrackDataset,
)
from OTAnalytics.plugin_parser import ottrk_dataformat
from OTAnalytics.plugin_parser.json_parser import write_json_bz2
from OTAnalytics.plugin_parser.otvision_parser import (
    DEFAULT_TRACK_LENGTH_LIMIT,
    OttrkFormatFixer,
    OttrkParser,
    PythonDetectionParser,
    TrackLengthLimit,
)
from OTAnalytics.plugin_parser.streaming_parser import (
    PythonStreamDetectionParser,
    StreamDetectionParser,
    StreamOttrkParser,
)
from OTAnalytics.plugin_progress.tqdm_progressbar import TqdmBuilder
from tests.utils.assertions import assert_equal_track_properties
from tests.utils.builders.track_builder import (
    TrackBuilder,
    append_sample_data,
    track_builder_with_sample_data,
)


@pytest.fixture
def track_builder_setup_with_sample_data() -> TrackBuilder:
    return track_builder_with_sample_data()


@pytest.fixture
def mocked_track_repository() -> Mock:
    repository = Mock(spec=TrackRepository)
    repository.get_for.return_value = None
    return repository


@pytest.fixture
def mocked_track_file_repository() -> Mock:
    repository = Mock(spec=TrackRepository)
    repository.get_all.return_value = set()
    return repository


def assert_track_stream_equals_dataset(
    bulk_res: TrackDataset, stream_res: Iterator[TrackDataset]
) -> None:
    stream_tracks = [track for dataset in stream_res for track in dataset.as_list()]
    assert_track_list_equals_dataset(bulk_res, stream_tracks)


def assert_track_list_equals_dataset(
    bulk_res: TrackDataset, tracks: list[Track]
) -> None:
    assert bulk_res.track_ids == {track.id for track in tracks}
    print("Size", len(bulk_res.track_ids), len(tracks))

    for actual_track in tracks:
        if expected_track := bulk_res.get_for(actual_track.id):
            assert_equal_track_properties(actual_track, expected_track)
        else:
            raise AssertionError(
                f"Track with id {actual_track.id} not found in expected dataset"
            )


class TestStreamOttrkParser:
    @pytest.fixture
    def bulk_ottrk_parser(
        self, mocked_track_repository: Mock, mocked_track_file_repository: Mock
    ) -> OttrkParser:
        calculator = ByMaxConfidence()
        detection_parser = PythonDetectionParser(
            calculator,
            mocked_track_repository,
            ShapelyTrackGeometryDataset.from_track_dataset,
            track_length_limit=DEFAULT_TRACK_LENGTH_LIMIT,
        )
        return OttrkParser(detection_parser)

    @pytest.fixture
    def videos_metadata(self) -> VideosMetadata:
        return VideosMetadata()

    @pytest.fixture
    def tracks_metadata(
        self, mocked_track_repository: TrackRepository
    ) -> TracksMetadata:
        return TracksMetadata(
            mocked_track_repository,
            frozenset(
                {
                    "person",
                    "bus",
                    "boat",
                    "truck",
                    "car",
                    "motorcycle",
                    "bicycle",
                    "train",
                }
            ),
            frozenset(),
        )

    @pytest.fixture
    def stream_ottrk_parser(
        self,
        tracks_metadata: TracksMetadata,
        videos_metadata: VideosMetadata,
    ) -> StreamOttrkParser:
        calculator = ByMaxConfidence()
        stream_detection_parser = PythonStreamDetectionParser(
            track_classification_calculator=calculator,
            track_length_limit=DEFAULT_TRACK_LENGTH_LIMIT,
        )
        return StreamOttrkParser(
            detection_parser=stream_detection_parser,
            format_fixer=OttrkFormatFixer(),
            registered_tracks_metadata=[tracks_metadata],
            registered_videos_metadata=[videos_metadata],
            progressbar=TqdmBuilder(),
            track_dataset_factory=lambda tracks: PandasTrackDataset.from_list(
                tracks,
                ShapelyTrackGeometryDataset.from_track_dataset,
                PandasByMaxConfidence(),
            ),
            chunk_size=4,
        )

    def ids_of(self, tracks: list[Track]) -> list[TrackId]:
        return [t.id for t in tracks]

    def test_parse_chunks(
        self,
        stream_ottrk_parser: StreamOttrkParser,
        bulk_ottrk_parser: OttrkParser,
        ottrk_path: Path,
    ) -> None:
        # compare result of streaming parser with original bulk parser

        bulk_res = bulk_ottrk_parser.parse(ottrk_path)
        stream = stream_ottrk_parser.parse({ottrk_path})

        expected = bulk_res.tracks.as_list()
        first_chunk = next(stream).as_list()
        second_chunk = next(stream).as_list()

        assert len(first_chunk) == 4
        assert len(second_chunk) == 2
        assert len(expected) == 6
        assert set(self.ids_of(expected)) == set(
            self.ids_of(first_chunk + second_chunk)
        )

        assert (
            set(self.ids_of(first_chunk)).intersection(set(self.ids_of(second_chunk)))
            == set()
        )

    def test_parse_whole_ottrk(
        self,
        stream_ottrk_parser: StreamOttrkParser,
        bulk_ottrk_parser: OttrkParser,
        ottrk_path: Path,
    ) -> None:
        # compare result of streaming parser with original bulk parser

        bulk_res = bulk_ottrk_parser.parse(ottrk_path)
        stream_res = stream_ottrk_parser.parse({ottrk_path})

        assert_track_stream_equals_dataset(bulk_res.tracks, stream_res)

    @pytest.mark.parametrize(
        "version,track_id", [("1.0", "legacy#legacy#1"), ("1.1", "1#1#1")]
    )
    def test_parse_ottrk_sample(
        self,
        test_data_tmp_dir: Path,
        stream_ottrk_parser: StreamOttrkParser,
        tracks_metadata: TracksMetadata,
        videos_metadata: VideosMetadata,
        version: str,
        track_id: str,
    ) -> None:
        ottrk_file = test_data_tmp_dir / "sample_file.ottrk"
        track_builder = track_builder_with_sample_data(input_file=str(ottrk_file))
        track_builder.set_ottrk_version(version)
        ottrk_data = track_builder.build_ottrk()
        write_json_bz2(ottrk_data, ottrk_file)
        parse_result = stream_ottrk_parser.parse({ottrk_file})

        example_track_builder = TrackBuilder()
        example_track_builder.add_input_file(str(ottrk_file))
        example_track_builder.add_track_id(track_id)
        append_sample_data(example_track_builder)
        expected_track = example_track_builder.build_track()
        expected_detection_classes = frozenset(
            ["person", "bus", "boat", "truck", "car", "motorcycle", "bicycle", "train"]
        )

        expected_dataset = PythonTrackDataset.from_list(
            [expected_track],
            ShapelyTrackGeometryDataset.from_track_dataset,
        )
        assert_track_stream_equals_dataset(expected_dataset, parse_result)

        assert tracks_metadata.detection_classifications == expected_detection_classes

        assert list(videos_metadata._metadata_by_date.values())[0] == VideoMetadata(
            path="myhostname_file.mp4",
            recorded_start_date=datetime(
                year=2020,
                month=1,
                day=1,
                hour=0,
                minute=0,
                tzinfo=timezone.utc,
            ),
            expected_duration=None,
            recorded_fps=20.0,
            actual_fps=None,
            number_of_frames=60,
        )
        ottrk_file.unlink()

    # todo test first / last chunk


class TestStreamDetectionParser:
    @pytest.fixture
    def mocked_classificator(self) -> TrackClassificationCalculator:
        return Mock(spec=TrackClassificationCalculator)

    @pytest.fixture
    def parser(
        self,
        mocked_track_repository: Mock,
        mocked_classificator: TrackClassificationCalculator,
    ) -> StreamDetectionParser:
        return PythonStreamDetectionParser(
            track_classification_calculator=mocked_classificator,
            track_length_limit=DEFAULT_TRACK_LENGTH_LIMIT,
        )

    def test_parse_detections_output_has_same_order_as_input(
        self,
        track_builder_setup_with_sample_data: TrackBuilder,
        parser: StreamDetectionParser,
    ) -> None:
        input_file = track_builder_setup_with_sample_data.input_file
        detections: list[dict] = (
            track_builder_setup_with_sample_data.build_serialized_detections()
        )
        metadata_video = track_builder_setup_with_sample_data.get_metadata()[
            ottrk_dataformat.VIDEO
        ]

        result_sorted_input = list(
            parser.parse_tracks(
                input_file,
                detections,
                metadata_video,
                TrackId,
            )
        )
        unsorted_detections = [detections[-1], detections[0]] + detections[1:-1]
        result_unsorted_input = list(
            parser.parse_tracks(
                input_file,
                unsorted_detections,
                metadata_video,
                TrackId,
            )
        )

        expected_sorted = {
            TrackId("1"): track_builder_setup_with_sample_data.build_detections()
        }

        assert expected_sorted == {
            track.id: track.detections for track in result_sorted_input
        }
        assert expected_sorted != {
            track.id: track.detections for track in result_unsorted_input
        }

    def test_parse_tracks(
        self,
        track_builder_setup_with_sample_data: TrackBuilder,
        mocked_classificator: Mock,
        parser: StreamDetectionParser,
    ) -> None:
        input_file = track_builder_setup_with_sample_data.input_file
        mocked_classificator.calculate.return_value = "car"
        detections: list[dict] = (
            track_builder_setup_with_sample_data.build_serialized_detections()
        )
        metadata_video = track_builder_setup_with_sample_data.get_metadata()[
            ottrk_dataformat.VIDEO
        ]

        result_sorted_input = list(
            parser.parse_tracks(input_file, detections, metadata_video)
        )

        # streaming parser must assume detections are provided in order!
        # unsorted_detections = [detections[-1], detections[0]] + detections[1:-1]
        # result_unsorted_input = list(
        #    parser.parse_tracks(input_file, unsorted_detections, metadata_video)
        # )

        expected_sorted = PythonTrackDataset.from_list(
            [track_builder_setup_with_sample_data.build_track()],
            ShapelyTrackGeometryDataset.from_track_dataset,
        )
        assert_track_list_equals_dataset(expected_sorted, result_sorted_input)

    @pytest.mark.parametrize(
        "track_length_limit",
        [
            TrackLengthLimit(20, 12000),
            TrackLengthLimit(0, 4),
        ],
    )
    def test_parse_tracks_consider_minimum_length(
        self,
        track_builder_setup_with_sample_data: TrackBuilder,
        track_length_limit: TrackLengthLimit,
    ) -> None:
        input_file = track_builder_setup_with_sample_data.input_file
        parser = PythonStreamDetectionParser(
            track_classification_calculator=ByMaxConfidence(),
            track_length_limit=track_length_limit,
        )

        detections: list[dict] = (
            track_builder_setup_with_sample_data.build_serialized_detections()
        )

        metadata_video = track_builder_setup_with_sample_data.get_metadata()[
            ottrk_dataformat.VIDEO
        ]
        result_sorted_input = list(
            parser.parse_tracks(input_file, detections, metadata_video)
        )

        assert len(result_sorted_input) == 0
