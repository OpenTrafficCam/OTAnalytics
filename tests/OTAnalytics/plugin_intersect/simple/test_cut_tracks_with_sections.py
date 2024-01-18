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
from OTAnalytics.domain.section import (
    Area,
    LineSection,
    SectionId,
    SectionRepositoryEvent,
    SectionType,
)
from OTAnalytics.domain.track import Track, TrackClassificationCalculator, TrackId
from OTAnalytics.domain.types import EventType
from OTAnalytics.plugin_datastore.python_track_store import SimpleCutTrackSegmentBuilder
from OTAnalytics.plugin_intersect.shapely.mapping import ShapelyMapper
from OTAnalytics.plugin_intersect.simple.cut_tracks_with_sections import (
    SimpleCutTracksIntersectingSection,
    SimpleCutTracksWithSection,
)
from tests.conftest import TrackBuilder as TrackBuilderForTesting


class TestSimpleCutTracksWithSection:
    @staticmethod
    def _create_cutting_section(
        id_name: str,
        coordinates: Iterable[tuple[float, float]],
        offset: RelativeOffsetCoordinate,
    ) -> LineSection:
        section_id = SectionId(id_name)
        converted_coords = [Coordinate(x, y) for x, y in coordinates]

        return LineSection(
            section_id,
            section_id.id,
            {EventType.SECTION_ENTER: offset},
            {},
            converted_coords,
        )

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
        "track_coords,section_coords,section_offset,expected",
        [
            (
                [(0, 1), (1, 1), (2, 1)],
                [(1.5, 2), (1.5, 0)],
                RelativeOffsetCoordinate(0, 0),
                [[(0, 1), (1, 1)], [(2, 1)]],
            ),
            (
                [(0, 1), (1, 1), (2, 1)],
                [(5, 2), (5, 0)],
                RelativeOffsetCoordinate(0, 0),
                [[(0, 1), (1, 1), (2, 1)]],
            ),
            (
                [(0, 1), (1, 1), (2, 1), (2, 2), (1, 2), (0, 2)],
                [(1.5, 3), (1.5, 0)],
                RelativeOffsetCoordinate(0, 0),
                [[(0, 1), (1, 1)], [(2, 1), (2, 2)], [(1, 2), (0, 2)]],
            ),
            (
                [(0, 1), (1, 1), (2, 1)],
                [(1.5, 2), (1.5, 0)],
                RelativeOffsetCoordinate(1, 1),
                [[(0, 1), (1, 1), (2, 1)]],
            ),
            (
                [(0, 10), (10, 10), (20, 10)],
                [(15, 20), (15, 0)],
                RelativeOffsetCoordinate(0.499, 0.0),
                [[(0, 10), (10, 10)], [(20, 10)]],
            ),
        ],
    )
    def test_cut_tracks(
        self,
        track_coords: list[tuple[float, float]],
        section_coords: list[tuple[float, float]],
        section_offset: RelativeOffsetCoordinate,
        expected: list[list[tuple[float, float]]],
        track_builder: TrackBuilderForTesting,
    ) -> None:
        track = self._create_track(track_builder, "1", track_coords)
        cutting_section = self._create_cutting_section(
            "#cut_1",
            section_coords,
            section_offset,
        )

        get_tracks_from_ids = Mock(spec=GetTracksFromIds, return_value=[track])
        geometry_mapper = ShapelyMapper()
        class_calculator = Mock(spec=TrackClassificationCalculator, return_value="car")
        cut_track_segment_builder = SimpleCutTrackSegmentBuilder(class_calculator)

        cut_tracks_with_section = SimpleCutTracksWithSection(
            get_tracks_from_ids,
            geometry_mapper,
            cut_track_segment_builder,
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
        intersections = {cutting_section.id: {track_id}}
        tracks_intersecting_sections = Mock(
            spec=TracksIntersectingSections, return_value=intersections
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
            cut_tracks_intersecting_section.notify_sections(
                SectionRepositoryEvent.create_added(section_ids)
            )

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
