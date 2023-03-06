from datetime import datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

import OTAnalytics.plugin_parser.ottrk_dataformat as ottrk_format
from OTAnalytics.domain.track import Detection, Track


@pytest.fixture
def valid_det_dict() -> dict:
    return {
        ottrk_format.CLASS: "car",
        ottrk_format.CONFIDENCE: 0.5,
        ottrk_format.X: 0.0,
        ottrk_format.Y: 0.0,
        ottrk_format.W: 0.0,
        ottrk_format.H: 0.0,
        ottrk_format.FRAME: 1,
        ottrk_format.OCCURENCE: datetime(2022, 1, 1, 1, 0, 0),
        ottrk_format.INPUT_FILE_PATH: Path("path/to/file.otdet"),
        ottrk_format.INTERPOLATED_DETECTION: False,
        ottrk_format.TRACK_ID: 1,
    }


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
                track_id=track_id,
            )

    def test_instantiation_with_valid_args(self, valid_det_dict: dict) -> None:
        det = Detection(**valid_det_dict)
        assert det.classification == valid_det_dict[ottrk_format.CLASS]
        assert det.confidence == valid_det_dict[ottrk_format.CONFIDENCE]
        assert det.x == valid_det_dict[ottrk_format.X]
        assert det.y == valid_det_dict[ottrk_format.Y]
        assert det.w == valid_det_dict[ottrk_format.W]
        assert det.h == valid_det_dict[ottrk_format.H]
        assert det.frame == valid_det_dict[ottrk_format.FRAME]
        assert det.occurrence == valid_det_dict[ottrk_format.OCCURENCE]
        assert det.input_file_path == valid_det_dict[ottrk_format.INPUT_FILE_PATH]
        assert (
            det.interpolated_detection
            == valid_det_dict[ottrk_format.INTERPOLATED_DETECTION]
        )
        assert det.track_id == valid_det_dict[ottrk_format.TRACK_ID]


class TestTrack:
    @pytest.mark.parametrize("id", [0, -1, 0.5])
    def test_value_error_raised_with_invalid_arg(
        self, valid_det_dict: dict, id: int
    ) -> None:
        detection = Detection(**valid_det_dict)
        with pytest.raises(ValidationError):
            Track(id=id, detections=[detection])

    def test_raise_error_on_empty_detections(self) -> None:
        with pytest.raises(ValidationError):
            Track(id=1, detections=[])

    def test_instantiation_with_valid_args(self, valid_det_dict: dict) -> None:
        detection = Detection(**valid_det_dict)
        track = Track(id=5, detections=[detection])
        assert track.id == 5
        assert track.detections == [detection]
