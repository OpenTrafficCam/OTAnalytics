import bz2
import json
from datetime import datetime
from pathlib import Path

import pytest

import OTAnalytics.plugin_parser.ottrk_dataformat as ottrk_format
from OTAnalytics.domain.track import Detection, Track
from OTAnalytics.plugin_parser.otvision_parser import OttrkParser


@pytest.fixture
def ottrk_sample(test_data_dir: Path) -> Path:
    return test_data_dir / "Sample_FR20_2020-01-01_00-00-00.ottrk"


@pytest.fixture
def sample_track_det_1() -> tuple[Detection, dict]:
    det_dict = {
        "class": "car",
        "confidence": 0.8448739051818848,
        "x": 153.6923828125,
        "y": 136.2128448486328,
        "w": 76.55817413330078,
        "h": 46.49921417236328,
        "frame": 1,
        "occurrence": "2020-01-01 00:00:00.000000",
        "input_file_path": "test/data/Testvideo_Cars-Cyclist_FR20_2020-01-01_00-00-00.otdet",  # noqa
        "interpolated-detection": False,
        "first": True,
        "finished": False,
        "track-id": 1,
    }
    return (
        Detection(
            classification=det_dict[ottrk_format.CLASS],
            confidence=det_dict[ottrk_format.CONFIDENCE],
            x=det_dict[ottrk_format.X],
            y=det_dict[ottrk_format.Y],
            w=det_dict[ottrk_format.W],
            h=det_dict[ottrk_format.H],
            frame=det_dict[ottrk_format.FRAME],
            occurrence=datetime.strptime(
                str(det_dict[ottrk_format.OCCURENCE]), ottrk_format.DATE_FORMAT
            ),
            input_file_path=Path(str(det_dict[ottrk_format.INPUT_FILE_PATH])),
            interpolated_detection=det_dict[ottrk_format.INTERPOLATED_DETECTION],
            track_id=det_dict[ottrk_format.TRACK_ID],
        ),
        det_dict,
    )


@pytest.fixture
def sample_track_det_2() -> tuple[Detection, dict]:
    det_dict = {
        "class": "car",
        "confidence": 0.8319828510284424,
        "x": 155.19091796875,
        "y": 136.7307891845703,
        "w": 77.07390594482422,
        "h": 46.8974609375,
        "frame": 2,
        "occurrence": "2020-01-01 00:00:00.050000",
        "input_file_path": "test/data/Testvideo_Cars-Cyclist_FR20_2020-01-01_00-00-00.otdet",  # noqa
        "interpolated-detection": False,
        "first": False,
        "finished": False,
        "track-id": 1,
    }
    return (
        Detection(
            classification=det_dict[ottrk_format.CLASS],
            confidence=det_dict[ottrk_format.CONFIDENCE],
            x=det_dict[ottrk_format.X],
            y=det_dict[ottrk_format.Y],
            w=det_dict[ottrk_format.W],
            h=det_dict[ottrk_format.H],
            frame=det_dict[ottrk_format.FRAME],
            occurrence=datetime.strptime(
                str(det_dict[ottrk_format.OCCURENCE]), ottrk_format.DATE_FORMAT
            ),
            input_file_path=Path(str(det_dict[ottrk_format.INPUT_FILE_PATH])),
            interpolated_detection=det_dict[ottrk_format.INTERPOLATED_DETECTION],
            track_id=det_dict[ottrk_format.TRACK_ID],
        ),
        det_dict,
    )


@pytest.fixture
def sample_track_det_3() -> tuple[Detection, dict]:
    det_dict = {
        "class": "car",
        "confidence": 0.829952597618103,
        "x": 158.3513641357422,
        "y": 137.06912231445312,
        "w": 75.2576904296875,
        "h": 49.759117126464844,
        "frame": 3,
        "occurrence": "2020-01-01 00:00:00.100000",
        "input_file_path": "test/data/Testvideo_Cars-Cyclist_FR20_2020-01-01_00-00-00.otdet",  # noqa
        "interpolated-detection": False,
        "first": False,
        "finished": False,
        "track-id": 1,
    }
    return (
        Detection(
            classification=det_dict[ottrk_format.CLASS],
            confidence=det_dict[ottrk_format.CONFIDENCE],
            x=det_dict[ottrk_format.X],
            y=det_dict[ottrk_format.Y],
            w=det_dict[ottrk_format.W],
            h=det_dict[ottrk_format.H],
            frame=det_dict[ottrk_format.FRAME],
            occurrence=datetime.strptime(
                str(det_dict[ottrk_format.OCCURENCE]), ottrk_format.DATE_FORMAT
            ),
            input_file_path=Path(str(det_dict[ottrk_format.INPUT_FILE_PATH])),
            interpolated_detection=det_dict[ottrk_format.INTERPOLATED_DETECTION],
            track_id=det_dict[ottrk_format.TRACK_ID],
        ),
        det_dict,
    )


@pytest.fixture
def expected_sample_tracks(
    sample_track_det_1: tuple[Detection, dict],
    sample_track_det_2: tuple[Detection, dict],
    sample_track_det_3: tuple[Detection, dict],
) -> list[Track]:
    return [
        Track(
            id=1,
            detections=[
                sample_track_det_1[0],
                sample_track_det_2[0],
                sample_track_det_3[0],
            ],
        )
    ]


@pytest.fixture
def example_json_bz2(test_data_tmp_dir: Path) -> tuple[Path, dict]:
    bz2_json_file = test_data_tmp_dir / "bz2_file.json"
    bz2_json_file.touch()
    content = {"first_name": "John", "last_name": "Doe"}
    with bz2.open(bz2_json_file, "wt", encoding="UTF-8") as out:
        json.dump(content, out)
    return bz2_json_file, content


@pytest.fixture
def example_json(test_data_tmp_dir: Path) -> tuple[Path, dict]:
    json_file = test_data_tmp_dir / "file.json"
    json_file.touch()
    content = {"first_name": "John", "last_name": "Doe"}
    with bz2.open(json_file, "wt", encoding="UTF-8") as out:
        json.dump(content, out)
    return json_file, content


class TestOttrkParser:
    ottrk_parser: OttrkParser = OttrkParser()

    def test_parse_whole_ottrk(self, ottrk_path: Path) -> None:
        self.ottrk_parser.parse(ottrk_path)

    def test_parse_ottrk_sample(
        self, ottrk_sample: Path, expected_sample_tracks: list[Track]
    ) -> None:
        result_tracks = self.ottrk_parser.parse(ottrk_sample)

        assert result_tracks == expected_sample_tracks

    def test_parse_bz2(self, example_json_bz2: tuple[Path, dict]) -> None:
        example_json_bz2_path, expected_content = example_json_bz2
        result_content = self.ottrk_parser._parse_bz2(example_json_bz2_path)
        assert result_content == expected_content

    def test_parse_bz2_uncompressed_file(self, example_json: tuple[Path, dict]) -> None:
        example_path, expected_content = example_json
        result_content = self.ottrk_parser._parse_bz2(example_path)
        assert result_content == expected_content

    def test_parse_detections_output_has_same_order_as_input(
        self,
        sample_track_det_1: tuple[Detection, dict],
        sample_track_det_2: tuple[Detection, dict],
        sample_track_det_3: tuple[Detection, dict],
    ) -> None:
        expected_det_1, det_dict_1 = sample_track_det_1
        expected_det_2, det_dict_2 = sample_track_det_2
        expected_det_3, det_dict_3 = sample_track_det_3

        result_sorted_dets = self.ottrk_parser._parse_detections(
            [det_dict_1, det_dict_2, det_dict_3]
        )
        result_unsorted_dets = self.ottrk_parser._parse_detections(
            [det_dict_3, det_dict_1, det_dict_2]
        )

        expected_sorted = {1: [expected_det_1, expected_det_2, expected_det_3]}
        expected_unsorted = {1: [expected_det_3, expected_det_1, expected_det_2]}

        assert expected_sorted == result_sorted_dets
        assert expected_unsorted == result_unsorted_dets

    def test_parse_tracks(
        self,
        sample_track_det_1: tuple[Detection, dict],
        sample_track_det_2: tuple[Detection, dict],
        sample_track_det_3: tuple[Detection, dict],
    ) -> None:
        expected_det_1, det_dict_1 = sample_track_det_1
        expected_det_2, det_dict_2 = sample_track_det_2
        expected_det_3, det_dict_3 = sample_track_det_3

        result_sorted_tracks = self.ottrk_parser._parse_tracks(
            [det_dict_1, det_dict_2, det_dict_3]
        )
        result_unsorted_tracks = self.ottrk_parser._parse_tracks(
            [det_dict_3, det_dict_1, det_dict_2]
        )

        expected_sorted = [
            Track(id=1, detections=[expected_det_1, expected_det_2, expected_det_3])
        ]

        assert expected_sorted == result_sorted_tracks
        assert expected_sorted == result_unsorted_tracks

    def assert_detection_equal(self, d1: Detection, d2: Detection) -> None:
        assert d1.classification == d2.classification
        assert d1.confidence == d2.confidence
        assert d1.x == d2.x
        assert d1.y == d2.y
        assert d1.w == d2.w
        assert d1.h == d2.h
        assert d1.frame == d2.frame
        assert d1.occurrence == d2.occurrence
        assert d1.input_file_path == d2.input_file_path
        assert d1.interpolated_detection == d2.interpolated_detection
        assert d1.track_id == d2.track_id
