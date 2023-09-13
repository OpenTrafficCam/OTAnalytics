from datetime import datetime
from typing import Iterable
from unittest.mock import Mock, patch

import pytest

from OTAnalytics.application.analysis.intersect import TracksIntersectingSections
from OTAnalytics.application.use_cases.cut_tracks_with_sections import (
    CutTracksWithSection,
)
from OTAnalytics.application.use_cases.section_repository import (
    GetSectionsById,
    RemoveSection,
)
from OTAnalytics.application.use_cases.track_repository import (
    AddAllTracks,
    GetTracksFromIds,
    GetTracksWithoutSingleDetections,
    RemoveTracks,
)
from OTAnalytics.domain.geometry import Coordinate, RelativeOffsetCoordinate
from OTAnalytics.domain.section import Area, LineSection, SectionId, SectionType
from OTAnalytics.domain.track import (
    Detection,
    Track,
    TrackClassificationCalculator,
    TrackId,
)
from OTAnalytics.plugin_intersect.shapely.mapping import ShapelyMapper
from OTAnalytics.plugin_intersect.simple.cut_tracks_with_sections import (
    SimpleCutTrackSegmentBuilder,
    SimpleCutTracksIntersectingSection,
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
        assert result.classification == classification
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
    ) -> LineSection:
        section_id = SectionId(id_name)
        converted_coords = [Coordinate(x, y) for x, y in coordinates]

        return LineSection(section_id, section_id.id, {}, {}, converted_coords)

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

        observable_track_offset = Mock()
        observable_track_offset.get.return_value = RelativeOffsetCoordinate(0, 0)
        track_view_state = Mock()
        track_view_state.track_offset = observable_track_offset

        cut_tracks_with_section = SimpleCutTracksWithSection(
            get_tracks_from_ids,
            geometry_mapper,
            cut_track_segment_builder,
            track_view_state,
        )

        actual_cut_tracks = cut_tracks_with_section([TrackId("1")], cutting_section)
        assert len(list(actual_cut_tracks)) == len(expected)

        for expected_track_id_suffix, (actual_track, expected_track_coord) in enumerate(
            zip(actual_cut_tracks, expected), start=0
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


class TestSimpleCutTracksIntersectingSection:
    @pytest.fixture
    def cutting_section(self) -> LineSection:
        section = Mock(spec=LineSection)
        section.id = SectionId("#cut_1")
        section.name = "#cut_1"
        section.get_type.return_value = SectionType.CUTTING
        return section

    @pytest.fixture
    def line_section(self) -> LineSection:
        section = Mock(spec=LineSection)
        section.id = SectionId("LineSection")
        section.get_type.return_value = SectionType.LINE
        return section

    @pytest.fixture
    def area_section(self) -> Area:
        section = Mock(spec=Area)
        section.id = SectionId("Area")
        section.get_type.return_value = SectionType.AREA
        return section

    def test_cut(self, cutting_section: LineSection) -> None:
        track_id = TrackId("1")
        track = Mock(spec=Track)
        track.id = track_id

        cut_tracks = [Mock(), Mock()]

        get_sections_by_id = Mock(spec=GetSectionsById)
        get_tracks = Mock(spec=GetTracksWithoutSingleDetections, return_value=[track])
        tracks_intersecting_sections = Mock(
            spec=TracksIntersectingSections, return_value={track_id}
        )
        cut_tracks_with_section = Mock(
            spec=CutTracksWithSection, return_value=cut_tracks
        )
        add_all_tracks = Mock(spec=AddAllTracks)
        remove_tracks = Mock(spec=RemoveTracks)
        remove_section = Mock(spec=RemoveSection)

        cut_tracks_intersecting_section = SimpleCutTracksIntersectingSection(
            get_sections_by_id,
            get_tracks,
            tracks_intersecting_sections,
            cut_tracks_with_section,
            add_all_tracks,
            remove_tracks,
            remove_section,
        )
        cut_tracks_intersecting_section(cutting_section)

        tracks_intersecting_sections.assert_called_once_with([cutting_section])
        cut_tracks_with_section.assert_called_once_with({track_id}, cutting_section)
        add_all_tracks.assert_called_once_with(cut_tracks)
        remove_tracks.assert_called_once_with({track_id})
        remove_section.assert_called_once_with(cutting_section.id)

    def test_notify_sections(
        self,
        cutting_section: LineSection,
        line_section: LineSection,
        area_section: Area,
    ) -> None:
        section_ids = [line_section.id, area_section.id, cutting_section.id]
        sections = [line_section, area_section, cutting_section]
        get_sections_by_id = Mock(spec=GetSectionsById, return_value=sections)

        with patch.object(SimpleCutTracksIntersectingSection, "__call__") as call_mock:
            cut_tracks_intersecting_section = SimpleCutTracksIntersectingSection(
                get_sections_by_id, Mock(), Mock(), Mock(), Mock(), Mock(), Mock()
            )
            cut_tracks_intersecting_section.notify_sections(section_ids)

            get_sections_by_id.assert_called_once_with(section_ids)
            call_mock.assert_called_once_with(cutting_section)

    @patch(
        "OTAnalytics.plugin_intersect.simple.cut_tracks_with_sections.Subject.register"
    )
    def test_register(self, mock_subject_register: Mock) -> None:
        observer = Mock()
        cut_tracks_intersecting_section = SimpleCutTracksIntersectingSection(
            Mock(), Mock(), Mock(), Mock(), Mock(), Mock(), Mock()
        )
        cut_tracks_intersecting_section.register(observer)
        mock_subject_register.assert_called_once_with(observer)
