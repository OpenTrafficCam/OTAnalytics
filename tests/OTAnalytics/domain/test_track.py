from datetime import datetime
from pathlib import Path
from typing import Optional
from unittest.mock import Mock

import pytest

import OTAnalytics.plugin_parser.ottrk_dataformat as ottrk_format
from OTAnalytics.domain.track import (
    BuildTrackWithSingleDetectionError,
    CalculateTrackClassificationByMaxConfidence,
    Detection,
    Track,
    TrackId,
    TrackObserver,
    TrackRepository,
    TrackSubject,
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
        "track-id": TrackId(1),
    }


@pytest.fixture
def valid_detection(valid_detection_dict: dict) -> Detection:
    return Detection(
        classification=valid_detection_dict[ottrk_format.CLASS],
        confidence=valid_detection_dict[ottrk_format.CONFIDENCE],
        x=valid_detection_dict[ottrk_format.X],
        y=valid_detection_dict[ottrk_format.Y],
        w=valid_detection_dict[ottrk_format.W],
        h=valid_detection_dict[ottrk_format.H],
        frame=valid_detection_dict[ottrk_format.FRAME],
        occurrence=valid_detection_dict[ottrk_format.OCCURRENCE],
        input_file_path=valid_detection_dict[ottrk_format.INPUT_FILE_PATH],
        interpolated_detection=valid_detection_dict[
            ottrk_format.INTERPOLATED_DETECTION
        ],
        track_id=valid_detection_dict[ottrk_format.TRACK_ID],
    )


class DataBuilder:
    def __init__(
        self,
        confidence: float,
        x: float,
        y: float,
        w: float,
        h: float,
        occurrence: datetime,
        input_file_path: Path,
        interpolated_detection: bool,
        track_id: TrackId,
        frame: Optional[int] = None,
        track_class: Optional[str] = None,
        detection_class: Optional[str] = None,
    ) -> None:
        self._track_class = track_class
        self._detections: list[Detection] = []
        self._detection_class = detection_class
        self._confidence = confidence
        self._x = x
        self._y = y
        self._w = w
        self._h = h
        self._frame = frame
        self._occurrence = occurrence
        self._input_file_path = input_file_path
        self._interpolated_detection = interpolated_detection
        self._track_id = track_id

    def build_track(self) -> Track:
        if self._track_class is None:
            raise ValueError("track ")

        return Track(self._track_id, self._track_class, self._detections)

    def build_detections(self) -> list[Detection]:
        return self._detections

    def append_detection(self) -> None:
        if self._detection_class is None:
            raise ValueError("classification not set")

        if self._frame is None:
            raise ValueError("frame not set")

        self._detections.append(
            Detection(
                classification=self._detection_class,
                confidence=self._confidence,
                x=self._x,
                y=self._y,
                w=self._w,
                h=self._h,
                frame=self._frame,
                occurrence=self._occurrence,
                input_file_path=self._input_file_path,
                interpolated_detection=self._interpolated_detection,
                track_id=self._track_id,
            )
        )

    def add_detection_class(self, classification: str) -> None:
        self._detection_class = classification

    def add_confidence(self, confidence: float) -> None:
        self._confidence = confidence

    def add_frame(self, frame: int) -> None:
        self._frame = frame

    def add_track_class(self, classification: str) -> None:
        self._track_class = classification


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
            Detection(
                classification="car",
                confidence=confidence,
                x=x,
                y=y,
                w=w,
                h=h,
                frame=frame,
                occurrence=datetime(2022, 1, 1, 1, 0, 0),
                input_file_path=Path("path/to/file.otdet"),
                interpolated_detection=False,
                track_id=TrackId(track_id),
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
        with pytest.raises(BuildTrackWithSingleDetectionError):
            Track(id=TrackId(1), classification="car", detections=[])

    def test_error_on_single_detection(self, valid_detection: Detection) -> None:
        with pytest.raises(BuildTrackWithSingleDetectionError):
            Track(id=TrackId(5), classification="car", detections=[valid_detection])

    def test_instantiation_with_valid_args(self, valid_detection: Detection) -> None:
        track = Track(
            id=TrackId(5),
            classification="car",
            detections=[valid_detection, valid_detection],
        )
        assert track.id == TrackId(5)
        assert track.classification == "car"
        assert track.detections == [valid_detection, valid_detection]


class TestCalculateTrackClassificationByMaxConfidence:
    def test_calculate(self) -> None:
        builder = DataBuilder(
            confidence=0.8,
            x=0.0,
            y=0.0,
            w=10,
            h=10,
            frame=1,
            occurrence=datetime(2022, 1, 1, 0, 0, 0, 0),
            input_file_path=Path("mypath_postfix.otdet"),
            interpolated_detection=False,
            track_id=TrackId(1),
            detection_class="car",
        )
        builder.append_detection()

        builder.add_confidence(0.7)
        builder.add_frame(2)
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


class TestTrackRepository:
    def test_add(self) -> None:
        track = Mock()
        repository = TrackRepository()

        repository.add(track)

        assert track in repository.get_all()

    def test_add_all(self) -> None:
        first_track = Mock()
        second_track = Mock()
        repository = TrackRepository()

        repository.add_all([first_track, second_track])

        assert first_track in repository.get_all()
        assert second_track in repository.get_all()

    def test_get_by_id(self) -> None:
        first_track = Mock()
        first_track.id.return_value = TrackId(1)
        second_track = Mock()
        repository = TrackRepository()
        repository.add_all([first_track, second_track])

        returned = repository.get_for(first_track.id)

        assert returned == first_track
