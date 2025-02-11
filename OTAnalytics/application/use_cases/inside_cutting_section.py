from typing import Iterable

from OTAnalytics.application.use_cases.section_repository import GetCuttingSections
from OTAnalytics.application.use_cases.track_repository import GetAllTracks
from OTAnalytics.domain.section import (
    SectionId,
    SectionListObserver,
    SectionRepositoryEvent,
)
from OTAnalytics.domain.track import TrackId, TrackIdProvider
from OTAnalytics.domain.track_repository import TrackListObserver, TrackRepositoryEvent
from OTAnalytics.domain.types import EventType


class TrackIdsInsideCuttingSections(TrackIdProvider):
    def __init__(
        self, get_tracks: GetAllTracks, get_cutting_sections: GetCuttingSections
    ):
        self._get_tracks = get_tracks
        self._get_cutting_sections = get_cutting_sections

    def get_ids(self) -> set[TrackId]:
        track_dataset = self._get_tracks.as_dataset()
        cutting_sections = self._get_cutting_sections()
        if not cutting_sections:
            return set()

        results: set[TrackId] = set()
        for cutting_section in cutting_sections:
            offset = cutting_section.get_offset(EventType.SECTION_ENTER)
            # set of all tracks where at least one coordinate is contained
            # by at least one cutting section
            results.update(
                set(
                    track_id
                    for track_id, section_data in (
                        track_dataset.contained_by_sections(
                            [cutting_section], offset
                        ).items()
                    )
                    if contains_true(section_data)
                )
            )
        return results


class CachedTrackIdsInsideCuttingSections(
    TrackIdsInsideCuttingSections, TrackListObserver, SectionListObserver
):
    def __init__(
        self,
        get_tracks: GetAllTracks,
        get_cutting_sections: GetCuttingSections,
    ) -> None:
        super().__init__(get_tracks, get_cutting_sections)
        self._cached_ids: set[TrackId] = self.__get_empty_cache()

    def get_ids(self) -> set[TrackId]:
        if self._cached_ids == self.__get_empty_cache():
            self._cached_ids = super().get_ids()

        return self._cached_ids

    def notify_tracks(self, track_event: TrackRepositoryEvent) -> None:
        if track_event.removed:
            self._remove_track_ids(track_event.removed)

        if track_event.added:
            self._reset_cache()

    def notify_sections(self, sections: SectionRepositoryEvent) -> None:
        self._reset_cache()

    def _reset_cache(self) -> None:
        self._cached_ids = self.__get_empty_cache()

    def _remove_track_ids(self, remove_track_ids: Iterable[TrackId]) -> None:
        self._cached_ids = self._cached_ids.difference(set(remove_track_ids))

    def __get_empty_cache(self) -> set[TrackId]:
        return set()


def contains_true(section_data: list[tuple[SectionId, list[bool]]]) -> bool:
    for _, bool_list in section_data:
        if any(bool_list):
            return True
    return False
