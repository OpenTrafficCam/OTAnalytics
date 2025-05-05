from datetime import datetime
from pathlib import Path
from typing import cast
from unittest.mock import Mock, call

import pytest

from OTAnalytics.domain.event import VIDEO_NAME
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate
from OTAnalytics.domain.section import LineSection
from OTAnalytics.domain.track import (
    INPUT_FILE,
    TRACK_CLASSIFICATION,
    TRACK_ID,
    Detection,
    Track,
    TrackClassificationCalculator,
    TrackHasNoDetectionError,
    TrackId,
)
from OTAnalytics.domain.track_dataset.track_dataset import (
    END_FRAME,
    END_OCCURRENCE,
    END_VIDEO_NAME,
    END_X,
    END_Y,
    START_FRAME,
    START_OCCURRENCE,
    START_VIDEO_NAME,
    START_X,
    START_Y,
    TRACK_GEOMETRY_FACTORY,
    TrackDoesNotExistError,
    TrackGeometryDataset,
)
from OTAnalytics.plugin_datastore.python_track_store import (
    ByMaxConfidence,
    PythonDetection,
    PythonTrack,
    PythonTrackDataset,
    PythonTrackSegment,
    PythonTrackSegmentDataset,
    SimpleCutTrackPartBuilder,
    create_segment_for,
)
from OTAnalytics.plugin_datastore.track_geometry_store.shapely_store import (
    ShapelyTrackGeometryDataset,
)
from OTAnalytics.plugin_parser import ottrk_dataformat as ottrk_format
from tests.utils.assertions import (
    assert_track_geometry_dataset_add_all_called_correctly,
)
from tests.utils.builders.track_builder import TrackBuilder, create_track
from tests.utils.builders.track_dataset_provider import create_mock_geometry_dataset
from tests.utils.builders.track_segment_builder import TrackSegmentDatasetBuilder


@pytest.fixture
def valid_detection_dict() -> dict:
    return {
        ottrk_format.CLASS: "car",
        ottrk_format.CONFIDENCE: 0.5,
        ottrk_format.X: 0.0,
        ottrk_format.Y: 0.0,
        ottrk_format.W: 0.0,
        ottrk_format.H: 0.0,
        ottrk_format.FRAME: 1,
        ottrk_format.OCCURRENCE: datetime(2022, 1, 1, 1, 0, 0),
        ottrk_format.INPUT_FILE_PATH: Path("path/to/file.otdet"),
        ottrk_format.INTERPOLATED_DETECTION: False,
        "track-id": TrackId("1"),
        "video_name": "file.mp4",
        "input_file": "file.ottrk",
    }


@pytest.fixture
def valid_detection(valid_detection_dict: dict) -> Detection:
    return PythonDetection(
        _classification=valid_detection_dict[ottrk_format.CLASS],
        _confidence=valid_detection_dict[ottrk_format.CONFIDENCE],
        _x=valid_detection_dict[ottrk_format.X],
        _y=valid_detection_dict[ottrk_format.Y],
        _w=valid_detection_dict[ottrk_format.W],
        _h=valid_detection_dict[ottrk_format.H],
        _frame=valid_detection_dict[ottrk_format.FRAME],
        _occurrence=valid_detection_dict[ottrk_format.OCCURRENCE],
        _interpolated_detection=valid_detection_dict[
            ottrk_format.INTERPOLATED_DETECTION
        ],
        _track_id=valid_detection_dict[ottrk_format.TRACK_ID],
        _video_name=valid_detection_dict[VIDEO_NAME],
        _input_file=valid_detection_dict[INPUT_FILE],
    )


class TestByMaxConfidence:
    def test_calculate(self) -> None:
        builder = TrackBuilder(
            confidence=0.8,
            w=10,
            h=10,
        )
        builder.append_detection()

        builder.add_confidence(0.8)
        builder.add_frame(2)
        builder.append_detection()

        builder.add_detection_class("truck")
        builder.add_confidence(0.8)
        builder.add_frame(3)
        builder.append_detection()

        builder.add_detection_class("truck")
        builder.add_confidence(0.4)
        builder.add_frame(2)
        builder.append_detection()

        detections = builder.build_detections()
        track_classification_calculator = ByMaxConfidence()
        result = track_classification_calculator.calculate(detections)

        assert result == "car"
        assert detections[2].classification == "truck"


class TestDetection:
    @pytest.mark.parametrize(
        "confidence,x,y,w,h,frame,track_id",
        [
            (-1, 1, 1, 1, 1, 1, 1),
            (2, 1, 1, 1, 1, 1, 1),
            (0, -0.0001, 1, 1, 1, 1, 1),
            (0, -1, -0.0001, 1, 1, 1, 1),
            (0, 2, 1, 1, -0.0001, 1, 1),
            (0, 2, 1, 1, 1, 0, 1),
        ],
    )
    def test_value_error_raised_with_invalid_arg(
        self,
        confidence: float,
        x: float,
        y: float,
        w: float,
        h: float,
        frame: int,
        track_id: int,
    ) -> None:
        with pytest.raises(ValueError):
            PythonDetection(
                _classification="car",
                _confidence=confidence,
                _x=x,
                _y=y,
                _w=w,
                _h=h,
                _frame=frame,
                _occurrence=datetime(2022, 1, 1, 1, 0, 0),
                _interpolated_detection=False,
                _track_id=TrackId(str(track_id)),
                _video_name="file.mp4",
                _input_file="file.ottrk",
            )

    def test_instantiation_with_valid_args(
        self, valid_detection: Detection, valid_detection_dict: dict
    ) -> None:
        det = valid_detection
        assert det.classification == valid_detection_dict[ottrk_format.CLASS]
        assert det.confidence == valid_detection_dict[ottrk_format.CONFIDENCE]
        assert det.x == valid_detection_dict[ottrk_format.X]
        assert det.y == valid_detection_dict[ottrk_format.Y]
        assert det.w == valid_detection_dict[ottrk_format.W]
        assert det.h == valid_detection_dict[ottrk_format.H]
        assert det.frame == valid_detection_dict[ottrk_format.FRAME]
        assert det.occurrence == valid_detection_dict[ottrk_format.OCCURRENCE]
        assert det.video_name == valid_detection_dict[VIDEO_NAME]
        assert det.input_file == valid_detection_dict[INPUT_FILE]
        assert (
            det.interpolated_detection
            == valid_detection_dict[ottrk_format.INTERPOLATED_DETECTION]
        )
        assert det.track_id == valid_detection_dict["track-id"]


class TestTrack:
    def test_raise_error_on_empty_detections(self) -> None:
        track_id = TrackId("1")
        with pytest.raises(TrackHasNoDetectionError):
            PythonTrack(
                _original_id=track_id,
                _id=track_id,
                _classification="car",
                _detections=[],
            )

    def test_no_error_on_single_detection(self, valid_detection: Detection) -> None:
        track_id = TrackId("5")
        track = PythonTrack(
            _original_id=track_id,
            _id=track_id,
            _classification="car",
            _detections=[valid_detection],
        )
        assert track.detections == [valid_detection]

    def test_instantiation_with_valid_args(self, valid_detection: Detection) -> None:
        track_id = TrackId("5")

        track = PythonTrack(
            _original_id=track_id,
            _id=track_id,
            _classification="car",
            _detections=[
                valid_detection,
                valid_detection,
                valid_detection,
                valid_detection,
                valid_detection,
            ],
        )
        assert track.id == TrackId("5")
        assert track.classification == "car"
        assert track.detections == [
            valid_detection,
            valid_detection,
            valid_detection,
            valid_detection,
            valid_detection,
        ]

    def test_start_and_end_time(self) -> None:
        start_time = datetime(2022, 1, 1, 13)
        end_time = datetime(2022, 1, 1, 14)

        start_detection = Mock(spec=Detection)
        start_detection.occurrence = start_time
        second_detection = Mock(spec=Detection)
        second_detection.occurrence = datetime(2022, 1, 1, 13, 15)
        third_detection = Mock(spec=Detection)
        third_detection.occurrence = datetime(2022, 1, 1, 13, 30)
        fourth_detection = Mock(spec=Detection)
        fourth_detection.occurrence = datetime(2022, 1, 1, 13, 45)

        end_detection = Mock(spec=Detection)
        end_detection.occurrence = end_time
        track_id = TrackId("1")
        track = PythonTrack(
            track_id,
            track_id,
            "car",
            [
                start_detection,
                second_detection,
                third_detection,
                fourth_detection,
                end_detection,
            ],
        )

        assert track.start == start_time
        assert track.end == end_time

    def test_first_and_last_detection(self, valid_detection: Detection) -> None:
        first = Mock(spec=Detection)
        first.occurrence = datetime.min
        last = Mock(spec=Detection)
        last.occurrence = datetime.max
        detections: list[Detection] = [
            first,
            valid_detection,
            valid_detection,
            valid_detection,
            last,
        ]
        track_id = TrackId("1")
        track = PythonTrack(track_id, track_id, "car", detections)
        assert track.first_detection == first
        assert track.last_detection == last


class TestPythonTrackSegment:
    def test_as_dict(self, car_track: Track) -> None:
        start = car_track.first_detection
        end = car_track.detections[1]
        segment = create_segment_for(track=car_track, start=start, end=end)

        actual = segment.as_dict()

        assert actual == {
            TRACK_ID: car_track.id.id,
            TRACK_CLASSIFICATION: car_track.classification,
            START_X: start.x,
            START_Y: start.y,
            START_OCCURRENCE: start.occurrence,
            START_FRAME: start.frame,
            START_VIDEO_NAME: start.video_name,
            END_X: end.x,
            END_Y: end.y,
            END_OCCURRENCE: end.occurrence,
            END_FRAME: end.frame,
            END_VIDEO_NAME: end.video_name,
        }


class TestPythonTrackSegmentDataset:
    def test_apply_with_segments(self) -> None:
        consumer = Mock()
        segment_1 = Mock(spec=PythonTrackSegment)
        segment_2 = Mock(spec=PythonTrackSegment)
        segment_1_dict = {"dummy-key": "segment-1"}
        segment_2_dict = {"dummy-key": "segment-2"}
        segment_1.as_dict.return_value = segment_1_dict
        segment_2.as_dict.return_value = segment_2_dict
        segments: list[PythonTrackSegment] = [segment_1, segment_2]
        dataset = PythonTrackSegmentDataset(segments=segments)

        dataset.apply(consumer=consumer)

        consumer.assert_has_calls([call(segment_1_dict), call(segment_2_dict)])

    def test_apply_without_segments(self) -> None:
        consumer = Mock()
        dataset = PythonTrackSegmentDataset(segments=[])

        dataset.apply(consumer=consumer)

        consumer.assert_not_called()


class TestPythonTrackDataset:
    @staticmethod
    def create_track_dataset(size: int) -> PythonTrackDataset:
        dataset: dict[TrackId, Track] = {}
        for i in range(0, size):
            track_id = TrackId(str(i))
            track = Mock()
            track.id = track_id
            dataset[track_id] = track

        return PythonTrackDataset(
            ShapelyTrackGeometryDataset.from_track_dataset, dataset
        )

    def test_add_all_to_empty(self, car_track: Track, pedestrian_track: Track) -> None:
        tracks = [car_track, pedestrian_track]
        dataset = PythonTrackDataset(ShapelyTrackGeometryDataset.from_track_dataset)
        result_dataset = cast(PythonTrackDataset, dataset.add_all(tracks))

        assert list(result_dataset) == tracks
        assert result_dataset._geometry_datasets == {}

    def test_add_all_merge_tracks(
        self, car_track: Track, car_track_continuing: Track, pedestrian_track: Track
    ) -> None:
        (
            geometry_dataset_no_offset,
            updated_geometry_dataset_no_offset,
        ) = create_mock_geometry_dataset()
        (
            geometry_dataset_with_offset,
            updated_geometry_dataset_with_offset,
        ) = create_mock_geometry_dataset()
        geometry_datasets = {
            RelativeOffsetCoordinate(0, 0): cast(
                TrackGeometryDataset, geometry_dataset_no_offset
            ),
            RelativeOffsetCoordinate(0.5, 0.5): cast(
                TrackGeometryDataset, geometry_dataset_with_offset
            ),
        }
        dataset = PythonTrackDataset(
            ShapelyTrackGeometryDataset.from_track_dataset,
            {car_track.id: car_track},
            geometry_datasets,
        )
        dataset_merged_track = cast(
            PythonTrackDataset,
            dataset.add_all([car_track_continuing, pedestrian_track]),
        )
        expected_merged_track = PythonTrack(
            car_track.id,
            car_track.id,
            car_track_continuing.classification,
            car_track.detections + car_track_continuing.detections,
        )
        assert list(dataset_merged_track) == [
            expected_merged_track,
            pedestrian_track,
        ]
        assert_track_geometry_dataset_add_all_called_correctly(
            geometry_dataset_no_offset.add_all,
            [expected_merged_track, pedestrian_track],
        )
        assert_track_geometry_dataset_add_all_called_correctly(
            geometry_dataset_with_offset.add_all,
            [expected_merged_track, pedestrian_track],
        )
        assert dataset_merged_track._geometry_datasets == {
            RelativeOffsetCoordinate(0, 0): updated_geometry_dataset_no_offset,
            RelativeOffsetCoordinate(0.5, 0.5): updated_geometry_dataset_with_offset,
        }

    def test_add_nothing(self, car_track: Track) -> None:
        dataset = PythonTrackDataset(ShapelyTrackGeometryDataset.from_track_dataset)
        result_dataset = dataset.add_all([car_track]).add_all(
            PythonTrackDataset(ShapelyTrackGeometryDataset.from_track_dataset)
        )

        assert list(result_dataset) == [car_track]

    def test_get_for(self, car_track: Track, pedestrian_track: Track) -> None:
        dataset = PythonTrackDataset(ShapelyTrackGeometryDataset.from_track_dataset)
        result_dataset = dataset.add_all([car_track, pedestrian_track])

        result = result_dataset.get_for(car_track.id)
        assert result == car_track

    def test_get_for_missing_id(self, car_track: Track) -> None:
        dataset = PythonTrackDataset.from_list(
            [car_track],
            ShapelyTrackGeometryDataset.from_track_dataset,
        )
        returned = dataset.get_for(TrackId("Foobar"))
        assert returned is None

    def test_get_for_missing_id_on_empty_dataset(self) -> None:
        dataset = PythonTrackDataset(ShapelyTrackGeometryDataset.from_track_dataset)
        returned = dataset.get_for(TrackId("1"))
        assert returned is None

    def test_clear(self, car_track: Track, pedestrian_track: Track) -> None:
        dataset = PythonTrackDataset(ShapelyTrackGeometryDataset.from_track_dataset)
        result_dataset = dataset.add_all([car_track, pedestrian_track])

        result = result_dataset.clear()
        assert list(result) == []

    def test_remove(self, car_track: Track, pedestrian_track: Track) -> None:
        geometry_dataset, updated_geometry_dataset = create_mock_geometry_dataset()
        dataset = PythonTrackDataset(
            ShapelyTrackGeometryDataset.from_track_dataset,
            {car_track.id: car_track, pedestrian_track.id: pedestrian_track},
            {RelativeOffsetCoordinate(0, 0): geometry_dataset},
        )
        result = cast(PythonTrackDataset, dataset.remove(pedestrian_track.id))
        assert list(result) == [car_track]
        assert result._geometry_datasets == {
            RelativeOffsetCoordinate(0, 0): updated_geometry_dataset
        }
        geometry_dataset.remove.assert_called_once_with([pedestrian_track.id.id])

    def test_remove_multiple(self, car_track: Track, pedestrian_track: Track) -> None:
        geometry_dataset, updated_geometry_dataset = create_mock_geometry_dataset()
        dataset = PythonTrackDataset(
            ShapelyTrackGeometryDataset.from_track_dataset,
            {car_track.id: car_track, pedestrian_track.id: pedestrian_track},
            {RelativeOffsetCoordinate(0, 0): geometry_dataset},
        )
        assert list(dataset) == [car_track, pedestrian_track]
        result = cast(
            PythonTrackDataset,
            dataset.remove_multiple({car_track.id, pedestrian_track.id}),
        )
        assert list(result) == []
        assert result._geometry_datasets == {
            RelativeOffsetCoordinate(0, 0): updated_geometry_dataset
        }
        assert set(geometry_dataset.remove.call_args_list[0][0][0]) == {
            car_track.id.id,
            pedestrian_track.id.id,
        }

    @pytest.mark.parametrize(
        "num_tracks,batches,expected_batches", [(10, 1, 1), (10, 4, 4), (3, 4, 3)]
    )
    def test_split(self, num_tracks: int, batches: int, expected_batches: int) -> None:
        dataset = self.create_track_dataset(num_tracks)
        assert len(dataset) == num_tracks
        split_datasets = dataset.split(batches)

        assert len(split_datasets) == expected_batches
        assert num_tracks == sum([len(_dataset) for _dataset in split_datasets])

        it = iter(dataset)
        for idx, _dataset in enumerate(split_datasets):
            for track in _dataset:
                expected_track = next(it)
                assert track == expected_track

    def test_split_with_existing_geometries(
        self, car_track: Track, pedestrian_track: Track
    ) -> None:
        first_batch_geometries_no_offset = Mock()
        second_batch_geometries_no_offset = Mock()
        geometry_dataset_no_offset, _ = create_mock_geometry_dataset(
            [first_batch_geometries_no_offset, second_batch_geometries_no_offset]
        )
        first_batch_geometries_with_offset = Mock()
        second_batch_geometries_with_offset = Mock()
        geometry_dataset_with_offset, _ = create_mock_geometry_dataset(
            [first_batch_geometries_with_offset, second_batch_geometries_with_offset]
        )

        geometry_datasets = {
            RelativeOffsetCoordinate(0, 0): cast(
                TrackGeometryDataset, geometry_dataset_no_offset
            ),
            RelativeOffsetCoordinate(0.5, 0.5): cast(
                TrackGeometryDataset, geometry_dataset_with_offset
            ),
        }
        dataset = PythonTrackDataset(
            ShapelyTrackGeometryDataset.from_track_dataset,
            {car_track.id: car_track, pedestrian_track.id: pedestrian_track},
            geometry_datasets,
        )
        result = cast(list[PythonTrackDataset], dataset.split(batches=2))

        assert result[0]._geometry_datasets == {
            RelativeOffsetCoordinate(0, 0): first_batch_geometries_no_offset,
            RelativeOffsetCoordinate(0.5, 0.5): first_batch_geometries_with_offset,
        }
        assert result[1]._geometry_datasets == {
            RelativeOffsetCoordinate(0, 0): second_batch_geometries_no_offset,
            RelativeOffsetCoordinate(0.5, 0.5): second_batch_geometries_with_offset,
        }
        assert geometry_dataset_no_offset.get_for.call_args_list == [
            call([car_track.id.id]),
            call([pedestrian_track.id.id]),
        ]
        assert geometry_dataset_with_offset.get_for.call_args_list == [
            call([car_track.id.id]),
            call([pedestrian_track.id.id]),
        ]

    def test_filter_by_minimum_detection_length(
        self, car_track: Track, pedestrian_track: Track
    ) -> None:
        dataset = PythonTrackDataset(
            ShapelyTrackGeometryDataset.from_track_dataset
        ).add_all([car_track, pedestrian_track])

        filtered_dataset = dataset.filter_by_min_detection_length(3)

        assert list(filtered_dataset) == [pedestrian_track]

    def test_get_first_segments(
        self,
        car_track: Track,
        pedestrian_track: Track,
        python_track_segment_dataset_builder: TrackSegmentDatasetBuilder,
    ) -> None:
        python_track_segment_dataset_builder.add_first_segments(
            [car_track, pedestrian_track]
        )
        segments = python_track_segment_dataset_builder.build()
        dataset = PythonTrackDataset.from_list(
            [car_track, pedestrian_track],
            ShapelyTrackGeometryDataset.from_track_dataset,
        )

        actual = dataset.get_first_segments()

        assert actual == segments

    def test_get_last_segments(
        self,
        car_track: Track,
        pedestrian_track: Track,
        python_track_segment_dataset_builder: TrackSegmentDatasetBuilder,
    ) -> None:
        python_track_segment_dataset_builder.add_last_segments(
            [car_track, pedestrian_track]
        )
        segments = python_track_segment_dataset_builder.build()

        dataset = PythonTrackDataset.from_list(
            [car_track, pedestrian_track],
            ShapelyTrackGeometryDataset.from_track_dataset,
        )

        actual = dataset.get_last_segments()

        assert actual == segments

    def test_first_occurrence(self, car_track: Track, pedestrian_track: Track) -> None:
        dataset = PythonTrackDataset.from_list(
            [pedestrian_track, car_track],
            ShapelyTrackGeometryDataset.from_track_dataset,
        )
        assert dataset.first_occurrence == car_track.first_detection.occurrence
        assert dataset.first_occurrence == pedestrian_track.first_detection.occurrence

    def test_last_occurrence(self, car_track: Track, pedestrian_track: Track) -> None:
        dataset = PythonTrackDataset.from_list(
            [pedestrian_track, car_track],
            ShapelyTrackGeometryDataset.from_track_dataset,
        )
        assert dataset.last_occurrence == pedestrian_track.last_detection.occurrence

    def test_first_occurrence_on_empty_dataset(self) -> None:
        dataset = PythonTrackDataset(ShapelyTrackGeometryDataset.from_track_dataset)
        assert dataset.first_occurrence is None

    def test_last_occurrence_on_empty_dataset(self) -> None:
        dataset = PythonTrackDataset(ShapelyTrackGeometryDataset.from_track_dataset)
        assert dataset.last_occurrence is None

    def test_classifications(self, car_track: Track, pedestrian_track: Track) -> None:
        dataset = PythonTrackDataset.from_list(
            [car_track, pedestrian_track],
            ShapelyTrackGeometryDataset.from_track_dataset,
        )
        assert dataset.classifications == frozenset(
            [car_track.classification, pedestrian_track.classification]
        )

    def test_classifications_on_empty_dataset(self) -> None:
        dataset = PythonTrackDataset(ShapelyTrackGeometryDataset.from_track_dataset)
        assert dataset.classifications == frozenset()

    def test_cut_with_section(
        self,
        cutting_section_test_case: tuple[
            LineSection, list[Track], list[Track], set[TrackId]
        ],
    ) -> None:
        (
            cutting_section,
            input_tracks,
            expected_tracks,
            expected_original_track_ids,
        ) = cutting_section_test_case
        expected_dataset = PythonTrackDataset.from_list(
            expected_tracks,
            ShapelyTrackGeometryDataset.from_track_dataset,
        )

        dataset = PythonTrackDataset.from_list(
            input_tracks,
            ShapelyTrackGeometryDataset.from_track_dataset,
        )
        cut_track_dataset, original_track_ids = dataset.cut_with_section(
            cutting_section, RelativeOffsetCoordinate(0, 0)
        )
        actual_tracks = sorted(cut_track_dataset, key=lambda _track: _track.id)
        expected_tracks = sorted(expected_dataset, key=lambda _track: _track.id)
        for actual, expected in zip(actual_tracks, expected_tracks):
            assert actual == expected
        assert original_track_ids == expected_original_track_ids

    def test_cut_with_section_no_tracks(self) -> None:
        dataset = PythonTrackDataset.from_list(
            [],
            ShapelyTrackGeometryDataset.from_track_dataset,
        )
        cut_track_dataset, original_track_ids = dataset.cut_with_section(
            Mock(), RelativeOffsetCoordinate(0, 0)
        )
        assert cut_track_dataset == dataset
        assert original_track_ids == set()

    def test_track_ids(
        self,
        car_track: Track,
        pedestrian_track: Track,
    ) -> None:
        dataset = PythonTrackDataset(ShapelyTrackGeometryDataset.from_track_dataset)
        assert dataset.track_ids == frozenset()
        updated_dataset = dataset.add_all([car_track, pedestrian_track])
        assert updated_dataset.track_ids == frozenset(
            [car_track.id, pedestrian_track.id]
        )

    def test_empty(self, car_track: Track) -> None:
        empty_dataset = PythonTrackDataset(
            ShapelyTrackGeometryDataset.from_track_dataset
        )
        assert empty_dataset.empty
        filled_dataset = empty_dataset.add_all([car_track])
        assert not filled_dataset.empty

    def test_get_max_confidences_for(
        self,
        car_track: Track,
        pedestrian_track: Track,
        track_geometry_factory: TRACK_GEOMETRY_FACTORY,
    ) -> None:
        empty_dataset = PythonTrackDataset(track_geometry_factory)
        with pytest.raises(TrackDoesNotExistError):
            empty_dataset.get_max_confidences_for([car_track.id.id])
        filled_dataset = empty_dataset.add_all([car_track, pedestrian_track])

        car_id = car_track.id.id
        pedestrian_id = pedestrian_track.id.id

        result = filled_dataset.get_max_confidences_for([car_id, pedestrian_id])
        assert result == {car_id: 0.8, pedestrian_id: 0.9}


class TestSimpleCutTrackSegmentBuilder:
    def test_build(self) -> None:
        classification = "car"
        my_track = create_track("1", [(0, 0), (1, 0), (2, 0), (3, 0)], 0)

        class_calculator = Mock(spec=TrackClassificationCalculator)
        class_calculator.calculate.return_value = classification
        track_builder = SimpleCutTrackPartBuilder(class_calculator)

        assert track_builder._track_id is None
        assert track_builder._detections == []

        track_builder.add_id(my_track.id.id)
        for detection in my_track.detections:
            track_builder.add_detection(detection)
        result = track_builder.build()
        assert result == my_track

        # Assert track builder is reset after build
        assert track_builder._track_id is None
        assert track_builder._detections == []
