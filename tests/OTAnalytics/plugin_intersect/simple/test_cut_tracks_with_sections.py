from unittest.mock import Mock, call, patch

import pytest

from OTAnalytics.application.use_cases.section_repository import (
    GetSectionsById,
    RemoveSection,
)
from OTAnalytics.application.use_cases.track_repository import (
    AddAllTracks,
    GetTracksWithoutSingleDetections,
    RemoveTracks,
)
from OTAnalytics.domain.section import (
    Area,
    LineSection,
    SectionId,
    SectionRepositoryEvent,
    SectionType,
)
from OTAnalytics.domain.track import Track, TrackId
from OTAnalytics.plugin_intersect.simple.cut_tracks_with_sections import (
    SimpleCutTracksIntersectingSection,
)


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

        get_sections_by_id = Mock(spec=GetSectionsById)
        get_tracks = Mock(spec=GetTracksWithoutSingleDetections, return_value=[track])
        cut_tracks_dataset = Mock()
        track_dataset = Mock()
        track_dataset.cut_with_section.return_value = (cut_tracks_dataset, {track_id})
        get_tracks.as_dataset.return_value = track_dataset

        add_all_tracks = Mock(spec=AddAllTracks)
        remove_tracks = Mock(spec=RemoveTracks)
        remove_section = Mock(spec=RemoveSection)

        cut_tracks_intersecting_section = SimpleCutTracksIntersectingSection(
            get_sections_by_id,
            get_tracks,
            add_all_tracks,
            remove_tracks,
            remove_section,
        )
        cut_tracks_intersecting_section(cutting_section, False)
        cut_tracks_intersecting_section(cutting_section, True)

        assert get_tracks.as_dataset.call_count == 2

        assert add_all_tracks.call_args_list == [
            call(cut_tracks_dataset),
            call(cut_tracks_dataset),
        ]
        assert remove_tracks.call_args_list == [
            call({track_id}),
            call({track_id}),
        ]
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
                get_sections_by_id, Mock(), Mock(), Mock(), Mock()
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
            Mock(), Mock(), Mock(), Mock(), Mock()
        )
        cut_tracks_intersecting_section.register(observer)
        mock_subject_register.assert_called_once_with(observer)
