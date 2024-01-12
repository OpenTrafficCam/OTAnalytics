from datetime import datetime
from pathlib import Path
from unittest.mock import Mock

import pytest

from OTAnalytics.domain.event import VIDEO_NAME
from OTAnalytics.domain.track import Detection, Track, TrackHasNoDetectionError, TrackId
from OTAnalytics.plugin_datastore.python_track_store import (
    ByMaxConfidence,
    PythonDetection,
    PythonTrack,
    PythonTrackDataset,
)
from OTAnalytics.plugin_parser import ottrk_dataformat as ottrk_format
from tests.conftest import TrackBuilder


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
    @pytest.fixture
    def first_track(self) -> Track:
        track_builder = TrackBuilder()
        _class = "car"

        track_builder.add_track_id("1")
        track_builder.add_track_class(_class)
        track_builder.add_second(1)
        track_builder.add_frame(1)
        track_builder.add_detection_class(_class)
        track_builder.append_detection()

        track_builder.add_track_class(_class)
        track_builder.add_second(2)
        track_builder.add_frame(2)
        track_builder.add_detection_class(_class)
        track_builder.append_detection()

        return track_builder.build_track()

    @pytest.fixture
    def first_track_continuing(self) -> Track:
        track_builder = TrackBuilder()
        _class = "truck"
        track_builder.add_track_id("1")
        track_builder.add_track_class(_class)
        track_builder.add_second(3)
        track_builder.add_frame(3)
        track_builder.add_detection_class(_class)
        track_builder.append_detection()

        track_builder.add_track_class(_class)
        track_builder.add_second(4)
        track_builder.add_frame(4)
        track_builder.add_detection_class(_class)
        track_builder.append_detection()

        track_builder.add_track_class(_class)
        track_builder.add_second(5)
        track_builder.add_frame(5)
        track_builder.add_detection_class(_class)
        track_builder.append_detection()

        return track_builder.build_track()

    @pytest.fixture
    def second_track(self) -> Track:
        track_builder = TrackBuilder()
        _class = "pedestrian"
        track_builder.add_track_id("2")
        track_builder.add_track_class(_class)
        track_builder.add_second(1)
        track_builder.add_frame(1)
        track_builder.add_detection_class(_class)
        track_builder.append_detection()

        track_builder.add_track_class(_class)
        track_builder.add_second(2)
        track_builder.add_frame(2)
        track_builder.add_detection_class(_class)
        track_builder.append_detection()

        track_builder.add_track_class(_class)
        track_builder.add_second(3)
        track_builder.add_frame(3)
        track_builder.add_detection_class(_class)
        track_builder.append_detection()

        return track_builder.build_track()

    @staticmethod
    def create_track_dataset(size: int) -> PythonTrackDataset:
        dataset: dict[TrackId, Track] = {}
        for i in range(0, size):
            track_id = TrackId(str(i))
            track = Mock()
            track.id = track_id
            dataset[track_id] = track

        return PythonTrackDataset(dataset)

    def test_add_all(self, first_track: Track, second_track: Track) -> None:
        tracks = [first_track, second_track]
        dataset = PythonTrackDataset()
        result_dataset = dataset.add_all(tracks)

        assert list(result_dataset) == tracks

    def test_add_all_merge_tracks(
        self, first_track: Track, first_track_continuing: Track
    ) -> None:
        dataset = PythonTrackDataset()
        dataset_with_first_track = dataset.add_all([first_track])
        assert list(dataset_with_first_track) == [first_track]

        dataset_merged_track = dataset_with_first_track.add_all(
            [first_track_continuing]
        )

        assert list(dataset_merged_track) == [
            PythonTrack(
                first_track.id,
                first_track_continuing.classification,
                first_track.detections + first_track_continuing.detections,
            )
        ]

    def test_add_nothing(self, first_track: Track) -> None:
        dataset = PythonTrackDataset()
        result_dataset = dataset.add_all([first_track]).add_all(PythonTrackDataset())

        assert list(result_dataset) == [first_track]

    def test_get_for(self, first_track: Track, second_track: Track) -> None:
        dataset = PythonTrackDataset()
        result_dataset = dataset.add_all([first_track, second_track])

        result = result_dataset.get_for(first_track.id)
        assert result == first_track

    def test_get_all_ids(self, first_track: Track, second_track: Track) -> None:
        dataset = PythonTrackDataset()
        result_dataset = dataset.add_all([first_track, second_track])

        result = result_dataset.get_all_ids()
        assert set(result) == {first_track.id, second_track.id}

    def test_clear(self, first_track: Track, second_track: Track) -> None:
        dataset = PythonTrackDataset()
        result_dataset = dataset.add_all([first_track, second_track])

        result = result_dataset.clear()
        assert list(result) == []

    def test_remove(self, first_track: Track, second_track: Track) -> None:
        dataset = PythonTrackDataset()
        result_dataset = dataset.add_all([first_track, second_track])

        result = result_dataset.remove(second_track.id)
        assert list(result) == [first_track]

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

    def test_filter_by_minimum_detection_length(
        self, first_track: Track, second_track: Track
    ) -> None:
        dataset = PythonTrackDataset().add_all([first_track, second_track])

        filtered_dataset = dataset.filter_by_min_detection_length(3)

        assert list(filtered_dataset) == [second_track]
