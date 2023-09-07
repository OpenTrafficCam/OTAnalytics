from datetime import datetime
from typing import Iterable
from unittest.mock import Mock

import pytest

from OTAnalytics.application.use_cases.track_repository import GetTracksFromIds
from OTAnalytics.domain.geometry import Coordinate
from OTAnalytics.domain.section import CuttingSection, SectionId
from OTAnalytics.domain.track import (
    Detection,
    Track,
    TrackClassificationCalculator,
    TrackId,
)
from OTAnalytics.plugin_intersect.shapely.mapping import ShapelyMapper
from OTAnalytics.plugin_intersect.simple.cut_tracks_with_sections import (
    SimpleCutTrackSegmentBuilder,
    SimpleCutTracksWithSection,
)
from tests.conftest import TrackBuilder as TrackBuilderForTesting


def create_mock_detection(occurrence: datetime) -> Detection:
    return Detection(
        "car", 0.7, 0, 0, 1, 1, 1, occurrence, False, TrackId("Default"), "my_video.mp4"
    )


@pytest.fixture
def detections() -> list[Detection]:
    first = create_mock_detection(datetime.min)
    second = create_mock_detection(datetime(2000, 1, 1))
    third = create_mock_detection(datetime(2000, 1, 2))
    fourth = create_mock_detection(datetime(2000, 1, 3))
    fifth = create_mock_detection(datetime.max)
    return [first, second, third, fourth, fifth]


class TestSimpleCutTrackSegmentBuilder:
    def test_build(self, detections: list[Detection]) -> None:
        track_id_name = "1"
        classification = "car"
        class_calculator = Mock(spec=TrackClassificationCalculator)
        class_calculator.calculate.return_value = classification
        track_builder = SimpleCutTrackSegmentBuilder(class_calculator)

        assert track_builder._track_id is None
        assert track_builder._detections == []

        track_builder.add_id(track_id_name)
        for detection in detections:
            track_builder.add_detection(detection)
        result = track_builder.build()
        assert result.id == TrackId(track_id_name)
        assert result.classification == "car"
        for result_detection, expected_detection in zip(result.detections, detections):
            assert result_detection.classification == expected_detection.classification
            assert result_detection.confidence == expected_detection.confidence
            assert result_detection.x == expected_detection.x
            assert result_detection.y == expected_detection.y
            assert result_detection.w == expected_detection.w
            assert result_detection.h == expected_detection.h
            assert result_detection.frame == expected_detection.frame
            assert result_detection.occurrence == expected_detection.occurrence
            assert (
                result_detection.interpolated_detection
                == expected_detection.interpolated_detection
            )
            assert result_detection.track_id == TrackId(track_id_name)
            assert result_detection.video_name == expected_detection.video_name

        # Assert track builder is reset after build
        assert track_builder._track_id is None
        assert track_builder._detections == []


class TestSimpleCutTracksWithSection:
    @staticmethod
    def _create_cutting_section(
        id_name: str, coordinates: Iterable[tuple[float, float]]
    ) -> CuttingSection:
        section_id = SectionId(id_name)
        converted_coords = [Coordinate(x, y) for x, y in coordinates]

        return CuttingSection(section_id, section_id.id, {}, {}, converted_coords)

    @staticmethod
    def _create_track(
        track_builder: TrackBuilderForTesting,
        id_name: str,
        coordinates: Iterable[tuple[float, float]],
    ) -> Track:
        track_builder.add_track_id(id_name)
        for second, (x, y) in enumerate(coordinates, start=1):
            track_builder.add_xy_bbox(x, y)
            track_builder.add_second(second)
            track_builder.append_detection()
        return track_builder.build_track()

    @pytest.mark.parametrize(
        "track_coords,section_coords,expected",
        [
            (
                [(0, 1), (1, 1), (2, 1)],
                [(1.5, 2), (1.5, 0)],
                [[(0, 1), (1, 1)], [(2, 1)]],
            ),
            (
                [(0, 1), (1, 1), (2, 1)],
                [(5, 2), (5, 0)],
                [[(0, 1), (1, 1), (2, 1)]],
            ),
            (
                [(0, 1), (1, 1), (2, 1), (2, 2), (1, 2), (0, 2)],
                [(1.5, 3), (1.5, 0)],
                [[(0, 1), (1, 1)], [(2, 1), (2, 2)], [(1, 2), (0, 2)]],
            ),
        ],
    )
    def test_cut_tracks(
        self,
        track_coords: list[tuple[float, float]],
        section_coords: list[tuple[float, float]],
        expected: list[list[tuple[float, float]]],
        track_builder: TrackBuilderForTesting,
    ) -> None:
        track = self._create_track(track_builder, "1", track_coords)
        cutting_section = self._create_cutting_section("#cut_1", section_coords)

        get_tracks_from_ids = Mock(spec=GetTracksFromIds, return_value=[track])
        geometry_mapper = ShapelyMapper()
        class_calculator = Mock(spec=TrackClassificationCalculator, return_value="car")
        cut_track_segment_builder = SimpleCutTrackSegmentBuilder(class_calculator)

        cut_tracks_with_section = SimpleCutTracksWithSection(
            get_tracks_from_ids, geometry_mapper, cut_track_segment_builder
        )

        actual_cut_tracks = cut_tracks_with_section([TrackId("1")], cutting_section)
        assert len(list(actual_cut_tracks)) == len(expected)

        for expected_track_id_suffix, (actual_track, expected_track_coord) in enumerate(
            zip(actual_cut_tracks, expected), start=1
        ):
            assert len(actual_track.detections) == len(expected_track_coord)
            expected_track_id = TrackId(f"1_{expected_track_id_suffix}")
            assert actual_track.id == expected_track_id

            for actual_detection, (expected_x, expected_y) in zip(
                actual_track.detections, expected_track_coord
            ):
                assert actual_detection.x == expected_x
                assert actual_detection.y == expected_y
                assert expected_track_id == actual_detection.track_id
