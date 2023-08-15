from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, call

import pytest

import OTAnalytics.plugin_parser.ottrk_dataformat as ottrk_format
from OTAnalytics.domain.track import (
    BuildTrackWithLessThanNDetectionsError,
    CalculateTrackClassificationByMaxConfidence,
    Detection,
    PythonDetection,
    PythonTrack,
    PythonTrackDataset,
    Track,
    TrackId,
    TrackListObserver,
    TrackObserver,
    TrackRepository,
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
        "track-id": TrackId(1),
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
        _input_file_path=valid_detection_dict[ottrk_format.INPUT_FILE_PATH],
        _interpolated_detection=valid_detection_dict[
            ottrk_format.INTERPOLATED_DETECTION
        ],
        _track_id=valid_detection_dict[ottrk_format.TRACK_ID],
    )


class TestTrackSubject:
    def test_notify_observer(self) -> None:
        changed_track = TrackId(1)
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
            (0, 1, 1, 1, 1, 1, -1),
            (0, 1, 1, 1, 1, 1, 0),
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
                _input_file_path=Path("path/to/file.otdet"),
                _interpolated_detection=False,
                _track_id=TrackId(track_id),
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
        assert det.input_file_path == valid_detection_dict[ottrk_format.INPUT_FILE_PATH]
        assert (
            det.interpolated_detection
            == valid_detection_dict[ottrk_format.INTERPOLATED_DETECTION]
        )
        assert det.track_id == valid_detection_dict["track-id"]


class TestTrack:
    @pytest.mark.parametrize("id", [0, -1, 0.5])
    def test_value_error_raised_with_invalid_arg(self, id: int) -> None:
        with pytest.raises(ValueError):
            TrackId(id)

    def test_raise_error_on_empty_detections(self) -> None:
        with pytest.raises(BuildTrackWithLessThanNDetectionsError):
            PythonTrack(_id=TrackId(1), _classification="car", _detections=[])

    def test_error_on_single_detection(self, valid_detection: Detection) -> None:
        with pytest.raises(BuildTrackWithLessThanNDetectionsError):
            PythonTrack(
                _id=TrackId(5), _classification="car", _detections=[valid_detection]
            )

    def test_instantiation_with_valid_args(self, valid_detection: Detection) -> None:
        track = PythonTrack(
            _id=TrackId(5),
            _classification="car",
            _detections=[
                valid_detection,
                valid_detection,
                valid_detection,
                valid_detection,
                valid_detection,
            ],
        )
        assert track.id == TrackId(5)
        assert track.classification == "car"
        assert track.detections == [
            valid_detection,
            valid_detection,
            valid_detection,
            valid_detection,
            valid_detection,
        ]


class TestCalculateTrackClassificationByMaxConfidence:
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
        track_classification_calculator = CalculateTrackClassificationByMaxConfidence()
        result = track_classification_calculator.calculate(detections)

        assert result == "car"
        assert detections[2].classification == "truck"


class TestPythonTrackDataset:
    def test_add(self) -> None:
        track_id = TrackId(1)
        track = Mock()
        track.id = track_id
        dataset = PythonTrackDataset()

        merged = dataset.add_all(PythonTrackDataset({track_id: track}))

        assert track not in dataset.as_list()
        assert track in merged.as_list()

    def test_add_nothing(self) -> None:
        dataset = PythonTrackDataset()

        merged = dataset.add_all(PythonTrackDataset())

        assert 0 == len(merged.as_list())

    def test_add_all(self) -> None:
        first_id = TrackId(1)
        second_id = TrackId(2)
        first_track = Mock()
        first_track.id = first_id
        second_track = Mock()
        second_track.id = second_id
        dataset = PythonTrackDataset()

        merged = dataset.add_all(
            PythonTrackDataset(
                {first_track.id: first_track, second_track.id: second_track}
            )
        )

        assert first_track in merged.as_list()
        assert second_track in merged.as_list()
        assert first_track not in dataset.as_list()
        assert second_track not in dataset.as_list()

    def test_get_by_id(self) -> None:
        first_track = Mock()
        first_track.id.return_value = TrackId(1)
        second_track = Mock()
        second_track.id.return_value = TrackId(2)
        dataset = PythonTrackDataset.from_list([first_track, second_track])

        returned = dataset.get_for(first_track.id)

        assert returned == first_track


class TestTrackRepository:
    def test_add(self) -> None:
        track_id = TrackId(1)
        track = Mock(spec=Track)
        track.id = track_id
        observer = Mock(spec=TrackListObserver)
        repository = TrackRepository()
        repository.register_tracks_observer(observer)

        repository.add_all(PythonTrackDataset.from_list([track]))

        assert track in repository.get_all()
        observer.notify_tracks.assert_called_with([track_id])

    def test_add_nothing(self) -> None:
        observer = Mock(spec=TrackListObserver)
        repository = TrackRepository()
        repository.register_tracks_observer(observer)

        repository.add_all(PythonTrackDataset())

        assert 0 == len(repository.get_all())
        observer.notify_tracks.assert_not_called()

    def test_add_all(self) -> None:
        first_id = TrackId(1)
        second_id = TrackId(2)
        first_track = Mock()
        first_track.id = first_id
        second_track = Mock()
        second_track.id = second_id
        observer = Mock(spec=TrackListObserver)
        repository = TrackRepository()
        repository.register_tracks_observer(observer)

        repository.add_all(PythonTrackDataset.from_list([first_track, second_track]))

        assert first_track in repository.get_all()
        assert second_track in repository.get_all()
        observer.notify_tracks.assert_called_with([first_id, second_id])

    def test_get_by_id(self) -> None:
        first_track = Mock()
        first_track.id.return_value = TrackId(1)
        second_track = Mock()
        repository = TrackRepository()
        repository.add_all(PythonTrackDataset.from_list([first_track, second_track]))

        returned = repository.get_for(first_track.id)

        assert returned == first_track

    def test_clear(self) -> None:
        first_id = TrackId(1)
        second_id = TrackId(2)
        first_track = Mock()
        first_track.id = first_id
        second_track = Mock()
        second_track.id = second_id
        observer = Mock(spec=TrackListObserver)
        repository = TrackRepository()
        repository.register_tracks_observer(observer)

        repository.add_all(PythonTrackDataset.from_list([first_track, second_track]))
        repository.clear()

        assert not list(repository.get_all())
        assert observer.notify_tracks.call_args_list == [
            call([first_id, second_id]),
            call([]),
        ]
