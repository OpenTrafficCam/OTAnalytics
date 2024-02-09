from datetime import datetime
from pathlib import Path
from typing import cast
from unittest.mock import Mock, call

import pytest

from OTAnalytics.domain.event import VIDEO_NAME, Event
from OTAnalytics.domain.geometry import (
    ImageCoordinate,
    RelativeOffsetCoordinate,
    calculate_direction_vector,
)
from OTAnalytics.domain.section import LineSection
from OTAnalytics.domain.track import (
    Detection,
    Track,
    TrackClassificationCalculator,
    TrackHasNoDetectionError,
    TrackId,
)
from OTAnalytics.domain.track_dataset import TrackGeometryDataset
from OTAnalytics.domain.types import EventType
from OTAnalytics.plugin_datastore.python_track_store import (
    ByMaxConfidence,
    PythonDetection,
    PythonTrack,
    PythonTrackDataset,
    SimpleCutTrackSegmentBuilder,
)
from OTAnalytics.plugin_datastore.track_store import extract_hostname
from OTAnalytics.plugin_parser import ottrk_dataformat as ottrk_format
from tests.conftest import TrackBuilder, create_track
from tests.OTAnalytics.plugin_datastore.conftest import (
    assert_track_geometry_dataset_add_all_called_correctly,
    create_mock_geometry_dataset,
)


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
        assert (
            det.interpolated_detection
            == valid_detection_dict[ottrk_format.INTERPOLATED_DETECTION]
        )
        assert det.track_id == valid_detection_dict["track-id"]


class TestTrack:
    def test_raise_error_on_empty_detections(self) -> None:
        with pytest.raises(TrackHasNoDetectionError):
            PythonTrack(
                _id=TrackId("1"),
                _classification="car",
                _detections=[],
            )

    def test_no_error_on_single_detection(self, valid_detection: Detection) -> None:
        track = PythonTrack(
            _id=TrackId("5"),
            _classification="car",
            _detections=[valid_detection],
        )
        assert track.detections == [valid_detection]

    def test_instantiation_with_valid_args(self, valid_detection: Detection) -> None:
        track = PythonTrack(
            _id=TrackId("5"),
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
        track = PythonTrack(
            TrackId("1"),
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
        track = PythonTrack(TrackId("1"), "car", detections)
        assert track.first_detection == first
        assert track.last_detection == last


class TestPythonTrackDataset:
    @staticmethod
    def create_track_dataset(size: int) -> PythonTrackDataset:
        dataset: dict[TrackId, Track] = {}
        for i in range(0, size):
            track_id = TrackId(str(i))
            track = Mock()
            track.id = track_id
            dataset[track_id] = track

        return PythonTrackDataset(dataset)

    def test_add_all_to_empty(self, first_track: Track, second_track: Track) -> None:
        tracks = [first_track, second_track]
        dataset = PythonTrackDataset()
        result_dataset = cast(PythonTrackDataset, dataset.add_all(tracks))

        assert list(result_dataset) == tracks
        assert result_dataset._geometry_datasets == {}

    def test_add_all_merge_tracks(
        self, first_track: Track, first_track_continuing: Track, second_track: Track
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
        dataset = PythonTrackDataset({first_track.id: first_track}, geometry_datasets)
        dataset_merged_track = cast(
            PythonTrackDataset, dataset.add_all([first_track_continuing, second_track])
        )
        expected_merged_track = PythonTrack(
            first_track.id,
            first_track_continuing.classification,
            first_track.detections + first_track_continuing.detections,
        )
        assert list(dataset_merged_track) == [
            expected_merged_track,
            second_track,
        ]
        assert_track_geometry_dataset_add_all_called_correctly(
            geometry_dataset_no_offset.add_all, [expected_merged_track, second_track]
        )
        assert_track_geometry_dataset_add_all_called_correctly(
            geometry_dataset_with_offset.add_all, [expected_merged_track, second_track]
        )
        assert dataset_merged_track._geometry_datasets == {
            RelativeOffsetCoordinate(0, 0): updated_geometry_dataset_no_offset,
            RelativeOffsetCoordinate(0.5, 0.5): updated_geometry_dataset_with_offset,
        }

    def test_add_nothing(self, first_track: Track) -> None:
        dataset = PythonTrackDataset()
        result_dataset = dataset.add_all([first_track]).add_all(PythonTrackDataset())

        assert list(result_dataset) == [first_track]

    def test_get_for(self, first_track: Track, second_track: Track) -> None:
        dataset = PythonTrackDataset()
        result_dataset = dataset.add_all([first_track, second_track])

        result = result_dataset.get_for(first_track.id)
        assert result == first_track

    def test_get_for_missing_id(self, first_track: Track) -> None:
        dataset = PythonTrackDataset.from_list([first_track])
        returned = dataset.get_for(TrackId("Foobar"))
        assert returned is None

    def test_get_for_missing_id_on_empty_dataset(self) -> None:
        dataset = PythonTrackDataset()
        returned = dataset.get_for(TrackId("1"))
        assert returned is None

    def test_clear(self, first_track: Track, second_track: Track) -> None:
        dataset = PythonTrackDataset()
        result_dataset = dataset.add_all([first_track, second_track])

        result = result_dataset.clear()
        assert list(result) == []

    def test_remove(self, first_track: Track, second_track: Track) -> None:
        geometry_dataset, updated_geometry_dataset = create_mock_geometry_dataset()
        dataset = PythonTrackDataset(
            {first_track.id: first_track, second_track.id: second_track},
            {RelativeOffsetCoordinate(0, 0): geometry_dataset},
        )
        result = cast(PythonTrackDataset, dataset.remove(second_track.id))
        assert list(result) == [first_track]
        assert result._geometry_datasets == {
            RelativeOffsetCoordinate(0, 0): updated_geometry_dataset
        }
        geometry_dataset.remove.assert_called_once_with({second_track.id})

    def test_remove_multiple(self, first_track: Track, second_track: Track) -> None:
        geometry_dataset, updated_geometry_dataset = create_mock_geometry_dataset()
        dataset = PythonTrackDataset(
            {first_track.id: first_track, second_track.id: second_track},
            {RelativeOffsetCoordinate(0, 0): geometry_dataset},
        )
        assert list(dataset) == [first_track, second_track]
        result = cast(
            PythonTrackDataset,
            dataset.remove_multiple({first_track.id, second_track.id}),
        )
        assert list(result) == []
        assert result._geometry_datasets == {
            RelativeOffsetCoordinate(0, 0): updated_geometry_dataset
        }
        geometry_dataset.remove.assert_called_once_with(
            {first_track.id, second_track.id}
        )

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
        self, first_track: Track, second_track: Track
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
            {first_track.id: first_track, second_track.id: second_track},
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
            call([first_track.id.id]),
            call([second_track.id.id]),
        ]
        assert geometry_dataset_with_offset.get_for.call_args_list == [
            call([first_track.id.id]),
            call([second_track.id.id]),
        ]

    def test_filter_by_minimum_detection_length(
        self, first_track: Track, second_track: Track
    ) -> None:
        dataset = PythonTrackDataset().add_all([first_track, second_track])

        filtered_dataset = dataset.filter_by_min_detection_length(3)

        assert list(filtered_dataset) == [second_track]

    def test_apply_to_first_segments(
        self,
        first_track: Track,
        second_track: Track,
    ) -> None:
        mock_consumer = Mock()
        dataset = PythonTrackDataset.from_list([first_track, second_track])

        dataset.apply_to_first_segments(mock_consumer)

        mock_consumer.assert_any_call(self.__create_enter_scene_event(first_track))
        mock_consumer.assert_any_call(self.__create_enter_scene_event(second_track))

    def test_apply_to_last_segments(
        self,
        first_track: Track,
        second_track: Track,
    ) -> None:
        mock_consumer = Mock()
        dataset = PythonTrackDataset.from_list([first_track, second_track])

        dataset.apply_to_last_segments(mock_consumer)

        mock_consumer.assert_any_call(self.__create_leave_scene_event(first_track))
        mock_consumer.assert_any_call(self.__create_leave_scene_event(second_track))

    def __create_enter_scene_event(self, track: Track) -> Event:
        return Event(
            road_user_id=track.id.id,
            road_user_type=track.classification,
            hostname=extract_hostname(track.first_detection.video_name),
            occurrence=track.first_detection.occurrence,
            frame_number=track.first_detection.frame,
            section_id=None,
            event_coordinate=ImageCoordinate(
                track.first_detection.x, track.first_detection.y
            ),
            event_type=EventType.ENTER_SCENE,
            direction_vector=calculate_direction_vector(
                track.first_detection.x,
                track.first_detection.y,
                track.detections[1].x,
                track.detections[1].y,
            ),
            video_name=track.first_detection.video_name,
        )

    def __create_leave_scene_event(self, track: Track) -> Event:
        return Event(
            road_user_id=track.id.id,
            road_user_type=track.classification,
            hostname=extract_hostname(track.last_detection.video_name),
            occurrence=track.last_detection.occurrence,
            frame_number=track.last_detection.frame,
            section_id=None,
            event_coordinate=ImageCoordinate(
                track.last_detection.x, track.last_detection.y
            ),
            event_type=EventType.LEAVE_SCENE,
            direction_vector=calculate_direction_vector(
                track.detections[-2].x,
                track.detections[-2].y,
                track.last_detection.x,
                track.last_detection.y,
            ),
            video_name=track.last_detection.video_name,
        )

    def test_first_occurrence(self, first_track: Track, second_track: Track) -> None:
        dataset = PythonTrackDataset.from_list([second_track, first_track])
        assert dataset.first_occurrence == first_track.first_detection.occurrence
        assert dataset.first_occurrence == second_track.first_detection.occurrence

    def test_last_occurrence(self, first_track: Track, second_track: Track) -> None:
        dataset = PythonTrackDataset.from_list([second_track, first_track])
        assert dataset.last_occurrence == second_track.last_detection.occurrence

    def test_first_occurrence_on_empty_dataset(self) -> None:
        dataset = PythonTrackDataset()
        assert dataset.first_occurrence is None

    def test_last_occurrence_on_empty_dataset(self) -> None:
        dataset = PythonTrackDataset()
        assert dataset.last_occurrence is None

    def test_classifications(self, first_track: Track, second_track: Track) -> None:
        dataset = PythonTrackDataset.from_list([first_track, second_track])
        assert dataset.classifications == frozenset(
            [first_track.classification, second_track.classification]
        )

    def test_classifications_on_empty_dataset(self) -> None:
        dataset = PythonTrackDataset()
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
        expected_dataset = PythonTrackDataset.from_list(expected_tracks)

        dataset = PythonTrackDataset.from_list(input_tracks)
        cut_track_dataset, original_track_ids = dataset.cut_with_section(
            cutting_section, RelativeOffsetCoordinate(0, 0)
        )
        actual_tracks = sorted(cut_track_dataset, key=lambda _track: _track.id)
        expected_tracks = sorted(expected_dataset, key=lambda _track: _track.id)
        for actual, expected in zip(actual_tracks, expected_tracks):
            assert actual == expected
        assert original_track_ids == expected_original_track_ids

    def test_cut_with_section_no_tracks(self) -> None:
        dataset = PythonTrackDataset.from_list([])
        cut_track_dataset, original_track_ids = dataset.cut_with_section(
            Mock(), RelativeOffsetCoordinate(0, 0)
        )
        assert cut_track_dataset == dataset
        assert original_track_ids == set()

    def test_track_ids(
        self,
        first_track: Track,
        second_track: Track,
    ) -> None:
        dataset = PythonTrackDataset()
        assert dataset.track_ids == frozenset()
        updated_dataset = dataset.add_all([first_track, second_track])
        assert updated_dataset.track_ids == frozenset([first_track.id, second_track.id])


class TestSimpleCutTrackSegmentBuilder:
    def test_build(self) -> None:
        classification = "car"
        my_track = create_track("1", [(0, 0), (1, 0), (2, 0), (3, 0)], 0)

        class_calculator = Mock(spec=TrackClassificationCalculator)
        class_calculator.calculate.return_value = classification
        track_builder = SimpleCutTrackSegmentBuilder(class_calculator)

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
