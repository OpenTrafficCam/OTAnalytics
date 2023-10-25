from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, call

import pytest

import OTAnalytics.plugin_parser.ottrk_dataformat as ottrk_format
from OTAnalytics.domain.event import VIDEO_NAME
from OTAnalytics.domain.track import (
    ByMaxConfidence,
    Detection,
    PythonDetection,
    PythonTrack,
    PythonTrackDataset,
    Track,
    TrackDataset,
    TrackFileRepository,
    TrackHasNoDetectionError,
    TrackId,
    TrackListObserver,
    TrackObserver,
    TrackRepository,
    TrackRepositoryEvent,
    TrackSubject,
)
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


class TestTrackSubject:
    def test_notify_observer(self) -> None:
        changed_track = TrackId("1")
        observer = Mock(spec=TrackObserver)
        subject = TrackSubject()
        subject.register(observer)

        subject.notify(changed_track)

        observer.notify_track.assert_called_with(changed_track)


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


class TestTrackRepository:
    @pytest.fixture
    def track_1(self) -> Mock:
        track = Mock(spec=Track)
        track.id = TrackId("1")
        return track

    @pytest.fixture
    def track_2(self) -> Mock:
        track = Mock(spec=Track)
        track.id = TrackId("2")
        return track

    def test_add_all(self, track_1: Mock, track_2: Mock) -> None:
        merged_tracks = [track_1, track_2]
        merged_dataset = Mock(spec=TrackDataset)
        merged_dataset.as_list.return_value = merged_tracks
        dataset = Mock(spec=TrackDataset)
        dataset.add_all.return_value = merged_dataset
        observer = Mock(spec=TrackListObserver)
        repository = TrackRepository(dataset)
        repository.register_tracks_observer(observer)
        new_tracks = PythonTrackDataset.from_list([track_1, track_2])

        repository.add_all(new_tracks)
        all_tracks = repository.get_all()

        assert all_tracks.as_list() is merged_tracks
        dataset.add_all.assert_called_with(new_tracks)
        observer.notify_tracks.assert_called_with(
            TrackRepositoryEvent([track_1.id, track_2.id], [])
        )

    def test_add_nothing(self) -> None:
        observer = Mock(spec=TrackListObserver)
        repository = TrackRepository()
        repository.register_tracks_observer(observer)

        repository.add_all(PythonTrackDataset())

        assert 0 == len(repository.get_all().as_list())
        observer.notify_tracks.assert_not_called()

    def test_get_by_id(self, track_1: Mock) -> None:
        dataset = Mock(spec=TrackDataset)
        dataset.get_for.return_value = track_1
        repository = TrackRepository(dataset)

        returned = repository.get_for(track_1.id)

        assert track_1 == returned
        dataset.get_for.assert_called_with(track_1.id)

    def test_clear(self, track_1: Track, track_2: Track) -> None:
        cleared_dataset = Mock(spec=TrackDataset)
        dataset = Mock(spec=TrackDataset)
        dataset.get_all_ids.return_value = [track_1.id, track_2.id]
        dataset.clear.return_value = cleared_dataset
        observer = Mock(spec=TrackListObserver)
        repository = TrackRepository(dataset)
        repository.register_tracks_observer(observer)

        repository.clear()

        assert repository._dataset == cleared_dataset
        assert observer.notify_tracks.call_args_list == [
            call(TrackRepositoryEvent([], [track_1.id, track_2.id]))
        ]

    def test_get_all_ids(self, track_1: Mock, track_2: Mock) -> None:
        ids: set[TrackId] = set()
        dataset = Mock(spec=TrackDataset)
        dataset.get_all_ids.return_value = ids
        repository = TrackRepository(dataset)

        actual_ids = repository.get_all_ids()

        assert actual_ids is ids

    def test_remove(self, track_1: Track, track_2: Track) -> None:
        dataset = Mock(spec=TrackDataset)
        dataset.remove.return_value = dataset
        repository = TrackRepository(dataset)

        observer = Mock(spec=TrackListObserver)
        repository.register_tracks_observer(observer)

        repository.remove(track_1.id)
        assert len(dataset.remove.call_args_list) == 1
        assert call(track_1.id) in dataset.remove.call_args_list
        repository.remove(track_2.id)
        assert call(track_2.id) in dataset.remove.call_args_list

        assert observer.notify_tracks.call_args_list == [
            call(TrackRepositoryEvent([], [track_1.id])),
            call(TrackRepositoryEvent([], [track_2.id])),
        ]

    def test_remove_multiple(self, track_1: Track, track_2: Track) -> None:
        dataset = Mock(spec=TrackDataset)
        dataset.remove.return_value = dataset
        repository = TrackRepository(dataset)

        observer = Mock(spec=TrackListObserver)
        repository.register_tracks_observer(observer)

        repository.remove_multiple({track_1.id, track_2.id})
        assert len(dataset.remove.call_args_list) == 2
        assert call(track_1.id) in dataset.remove.call_args_list
        assert call(track_2.id) in dataset.remove.call_args_list


class TestTrackFileRepository:
    @pytest.fixture
    def mock_file(self) -> Mock:
        return Mock(spec=Path)

    @pytest.fixture
    def mock_other_file(self) -> Mock:
        return Mock(spec=Path)

    def test_add(self, mock_file: Mock, mock_other_file: Mock) -> None:
        repository = TrackFileRepository()
        assert repository._files == set()
        repository.add(mock_file)
        assert repository._files == {mock_file}
        repository.add(mock_file)
        assert repository._files == {mock_file}
        repository.add(mock_other_file)
        assert repository._files == {mock_file, mock_other_file}

    def test_add_all(self, mock_file: Mock, mock_other_file: Mock) -> None:
        repository = TrackFileRepository()
        repository.add_all([mock_file, mock_other_file])
        assert repository._files == {mock_file, mock_other_file}
