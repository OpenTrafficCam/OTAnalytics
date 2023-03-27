import bz2
from datetime import datetime
from pathlib import Path

import pytest
import ujson

import OTAnalytics.plugin_parser.ottrk_dataformat as ottrk_format
from OTAnalytics.domain import section
from OTAnalytics.domain.section import Area, Coordinate, LineSection, Section
from OTAnalytics.domain.track import (
    CalculateTrackClassificationByMaxConfidence,
    Detection,
    Track,
    TrackId,
)
from OTAnalytics.plugin_parser.otvision_parser import (
    InvalidSectionData,
    OtsectionParser,
    OttrkParser,
    _parse_bz2,
)


@pytest.fixture
def ottrk_sample(test_data_dir: Path) -> Path:
    return test_data_dir / "Sample_FR20_2020-01-01_00-00-00.ottrk"


@pytest.fixture
def sample_track_det_1() -> Detection:
    return Detection(
        classification="car",
        confidence=0.8448739051818848,
        x=153.6923828125,
        y=136.2128448486328,
        w=76.55817413330078,
        h=46.49921417236328,
        frame=1,
        occurrence=datetime.strptime(
            "2020-01-01 00:00:00.000000", ottrk_format.DATE_FORMAT
        ),
        input_file_path=Path(
            "test/data/Testvideo_Cars-Cyclist_FR20_2020-01-01_00-00-00.otdet"
        ),
        interpolated_detection=False,
        track_id=TrackId(1),
    )


@pytest.fixture
def sample_track_det_1_dict() -> dict:
    return {
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


@pytest.fixture
def sample_track_det_2() -> Detection:
    return Detection(
        classification="car",
        confidence=0.8319828510284424,
        x=155.19091796875,
        y=136.7307891845703,
        w=77.07390594482422,
        h=46.8974609375,
        frame=2,
        occurrence=datetime.strptime(
            "2020-01-01 00:00:00.050000", ottrk_format.DATE_FORMAT
        ),
        input_file_path=Path(
            "test/data/Testvideo_Cars-Cyclist_FR20_2020-01-01_00-00-00.otdet"
        ),
        interpolated_detection=False,
        track_id=TrackId(1),
    )


@pytest.fixture
def sample_track_det_2_dict() -> dict:
    return {
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


@pytest.fixture
def sample_track_det_3() -> Detection:
    return Detection(
        classification="car",
        confidence=0.829952597618103,
        x=158.3513641357422,
        y=137.06912231445312,
        w=75.2576904296875,
        h=49.759117126464844,
        frame=3,
        occurrence=datetime.strptime(
            "2020-01-01 00:00:00.100000", ottrk_format.DATE_FORMAT
        ),
        input_file_path=Path(
            "test/data/Testvideo_Cars-Cyclist_FR20_2020-01-01_00-00-00.otdet"
        ),
        interpolated_detection=False,
        track_id=TrackId(1),
    )


@pytest.fixture
def sample_track_det_3_dict() -> dict:
    return {
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


@pytest.fixture
def expected_sample_tracks(
    sample_track_det_1: Detection,
    sample_track_det_2: Detection,
    sample_track_det_3: Detection,
) -> list[Track]:
    return [
        Track(
            id=TrackId(1),
            classification="car",
            detections=[
                sample_track_det_1,
                sample_track_det_2,
                sample_track_det_3,
            ],
        )
    ]


@pytest.fixture
def example_json_bz2(test_data_tmp_dir: Path) -> tuple[Path, dict]:
    bz2_json_file = test_data_tmp_dir / "bz2_file.json"
    bz2_json_file.touch()
    content = {"first_name": "John", "last_name": "Doe"}
    with bz2.open(bz2_json_file, "wt", encoding="UTF-8") as out:
        ujson.dump(content, out)
    return bz2_json_file, content


@pytest.fixture
def example_json(test_data_tmp_dir: Path) -> tuple[Path, dict]:
    json_file = test_data_tmp_dir / "file.json"
    json_file.touch()
    content = {"first_name": "John", "last_name": "Doe"}
    with bz2.open(json_file, "wt", encoding="UTF-8") as out:
        ujson.dump(content, out)
    return json_file, content


class TestOttrkParser:
    ottrk_parser: OttrkParser = OttrkParser(
        CalculateTrackClassificationByMaxConfidence()
    )

    def test_parse_whole_ottrk(self, ottrk_path: Path) -> None:
        self.ottrk_parser.parse(ottrk_path)

    def test_parse_ottrk_sample(
        self, ottrk_sample: Path, expected_sample_tracks: list[Track]
    ) -> None:
        result_tracks = self.ottrk_parser.parse(ottrk_sample)

        assert result_tracks == expected_sample_tracks

    def test_parse_bz2(self, example_json_bz2: tuple[Path, dict]) -> None:
        example_json_bz2_path, expected_content = example_json_bz2
        result_content = _parse_bz2(example_json_bz2_path)
        assert result_content == expected_content

    def test_parse_bz2_uncompressed_file(self, example_json: tuple[Path, dict]) -> None:
        example_path, expected_content = example_json
        result_content = _parse_bz2(example_path)
        assert result_content == expected_content

    def test_parse_detections_output_has_same_order_as_input(
        self,
        sample_track_det_1: Detection,
        sample_track_det_2: Detection,
        sample_track_det_3: Detection,
        sample_track_det_1_dict: dict,
        sample_track_det_2_dict: dict,
        sample_track_det_3_dict: dict,
    ) -> None:
        result_sorted = self.ottrk_parser._parse_detections(
            [sample_track_det_1_dict, sample_track_det_2_dict, sample_track_det_3_dict]
        )
        result_unsorted = self.ottrk_parser._parse_detections(
            [sample_track_det_3_dict, sample_track_det_1_dict, sample_track_det_2_dict]
        )

        expected_sorted = {
            TrackId(1): [sample_track_det_1, sample_track_det_2, sample_track_det_3]
        }
        expected_unsorted = {
            TrackId(1): [sample_track_det_3, sample_track_det_1, sample_track_det_2]
        }

        assert expected_sorted == result_sorted
        assert expected_unsorted == result_unsorted

    def test_parse_tracks(
        self,
        sample_track_det_1: Detection,
        sample_track_det_2: Detection,
        sample_track_det_3: Detection,
        sample_track_det_1_dict: dict,
        sample_track_det_2_dict: dict,
        sample_track_det_3_dict: dict,
    ) -> None:
        result_sorted_tracks = self.ottrk_parser._parse_tracks(
            [sample_track_det_1_dict, sample_track_det_2_dict, sample_track_det_3_dict]
        )
        result_unsorted_tracks = self.ottrk_parser._parse_tracks(
            [sample_track_det_3_dict, sample_track_det_1_dict, sample_track_det_2_dict]
        )

        expected_sorted = [
            Track(
                id=TrackId(1),
                classification="car",
                detections=[sample_track_det_1, sample_track_det_2, sample_track_det_3],
            )
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


class TestOtsectionParser:
    def test_parse_section(self, test_data_tmp_dir: Path) -> None:
        first_coordinate = Coordinate(0, 0)
        second_coordinate = Coordinate(1, 1)
        third_coordinate = Coordinate(1, 0)
        line_section: Section = LineSection(
            id="some",
            start=first_coordinate,
            end=second_coordinate,
        )
        area_section: Section = Area(
            id="other",
            coordinates=[
                first_coordinate,
                second_coordinate,
                third_coordinate,
                first_coordinate,
            ],
        )
        json_file = test_data_tmp_dir / "section.json"
        json_file.touch()
        sections = [line_section, area_section]
        parser = OtsectionParser()
        parser.serialize(sections, json_file)

        content = parser.parse(json_file)

        assert content == sections

    def test_validate(self) -> None:
        parser = OtsectionParser()
        pytest.raises(
            InvalidSectionData, parser._parse_section, {section.TYPE: section.LINE}
        )

    def test_convert_section(self) -> None:
        some_section: Section = LineSection(
            id="some",
            start=Coordinate(0, 0),
            end=Coordinate(1, 1),
        )
        other_section: Section = LineSection(
            id="other",
            start=Coordinate(1, 0),
            end=Coordinate(0, 1),
        )
        sections = [some_section, other_section]
        parser = OtsectionParser()

        content = parser._convert(sections)

        assert content == {
            section.SECTIONS: [some_section.to_dict(), other_section.to_dict()]
        }
