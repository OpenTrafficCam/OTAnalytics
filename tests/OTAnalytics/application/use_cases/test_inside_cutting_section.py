from unittest.mock import Mock, patch

import pytest

from OTAnalytics.application.use_cases.inside_cutting_section import (
    CachedTrackIdsInsideCuttingSections,
)
from OTAnalytics.application.use_cases.section_repository import GetCuttingSections
from OTAnalytics.application.use_cases.track_repository import GetAllTracks
from OTAnalytics.domain.section import SectionId, SectionRepositoryEvent
from OTAnalytics.domain.track import TrackId
from OTAnalytics.domain.track_repository import TrackRepositoryEvent


@pytest.fixture
def get_tracks() -> Mock:
    return Mock(spec=GetAllTracks)


@pytest.fixture
def get_cutting_sections() -> Mock:
    return Mock(spec=GetCuttingSections)


@pytest.fixture
def track_ids() -> set[TrackId]:
    return {TrackId("0"), TrackId("8"), TrackId("15")}


@pytest.fixture
def add_track_event() -> TrackRepositoryEvent:
    return TrackRepositoryEvent.create_added([TrackId("1")])


@pytest.fixture
def remove_track_event() -> TrackRepositoryEvent:
    return TrackRepositoryEvent.create_removed([TrackId("2")])


@pytest.fixture
def add_section_event() -> SectionRepositoryEvent:
    return SectionRepositoryEvent.create_added([SectionId("1")])


@pytest.fixture
def remove_section_event() -> SectionRepositoryEvent:
    return SectionRepositoryEvent.create_removed([SectionId("2")])


@pytest.fixture
def cached_track_ids_inside_cutting_sections() -> CachedTrackIdsInsideCuttingSections:
    get_all_tracks = Mock(spec=GetAllTracks)
    get_cutting_sections = Mock(spec=GetCuttingSections)
    cached_track_ids_inside_cutting_sections = CachedTrackIdsInsideCuttingSections(
        get_all_tracks, get_cutting_sections
    )
    cached_track_ids_inside_cutting_sections._cached_ids = {
        TrackId("1"),
        TrackId("2"),
    }
    return cached_track_ids_inside_cutting_sections


def assert__reset_cache_called_once_when_notify_tracks_with(
    cached: CachedTrackIdsInsideCuttingSections,
    event: SectionRepositoryEvent,
) -> None:
    with patch.object(cached, "_reset_cache") as mock_reset_cache:
        cached.notify_sections(event)
        mock_reset_cache.assert_called_once()


class TestCachedTrackIdsInsideCuttingSections:
    def test__init__(self, get_tracks: Mock, get_cutting_sections: Mock) -> None:
        cached = CachedTrackIdsInsideCuttingSections(get_tracks, get_cutting_sections)
        assert cached._cached_ids == set()

    def test_get_ids(
        self,
        cached_track_ids_inside_cutting_sections: CachedTrackIdsInsideCuttingSections,
        track_ids: set[TrackId],
    ) -> None:
        cached_track_ids_inside_cutting_sections._cached_ids = track_ids
        assert cached_track_ids_inside_cutting_sections.get_ids() == track_ids

    def test_notify_added_tracks_clear_cache(
        self,
        cached_track_ids_inside_cutting_sections: CachedTrackIdsInsideCuttingSections,
        add_track_event: TrackRepositoryEvent,
    ) -> None:
        cached_track_ids_inside_cutting_sections.notify_tracks(add_track_event)
        with patch.object(
            cached_track_ids_inside_cutting_sections, "_reset_cache"
        ) as mock_reset_cache:
            cached_track_ids_inside_cutting_sections.notify_tracks(add_track_event)
            mock_reset_cache.assert_called_once()

    def test_notify_removed_tracks_updates_cache(
        self,
        cached_track_ids_inside_cutting_sections: CachedTrackIdsInsideCuttingSections,
        remove_track_event: TrackRepositoryEvent,
    ) -> None:
        cached_track_ids_inside_cutting_sections.notify_tracks(remove_track_event)
        assert cached_track_ids_inside_cutting_sections._cached_ids == {TrackId("1")}

    def test_notify_add_sections_clear_cache(
        self,
        cached_track_ids_inside_cutting_sections: CachedTrackIdsInsideCuttingSections,
        add_section_event: SectionRepositoryEvent,
    ) -> None:
        cached_track_ids_inside_cutting_sections.notify_sections(add_section_event)
        assert__reset_cache_called_once_when_notify_tracks_with(
            cached_track_ids_inside_cutting_sections, add_section_event
        )

    def test_notify_remove_sections_clear_cache(
        self,
        cached_track_ids_inside_cutting_sections: CachedTrackIdsInsideCuttingSections,
        remove_section_event: SectionRepositoryEvent,
    ) -> None:
        cached_track_ids_inside_cutting_sections.notify_sections(remove_section_event)
        assert__reset_cache_called_once_when_notify_tracks_with(
            cached_track_ids_inside_cutting_sections, remove_section_event
        )

    def test__reset_cache(
        self, get_tracks: Mock, get_cutting_sections: Mock, track_ids: set[TrackId]
    ) -> None:
        cached = CachedTrackIdsInsideCuttingSections(get_tracks, get_cutting_sections)
        cached._cached_ids = track_ids
        cached._reset_cache()
        assert cached._cached_ids == set()
