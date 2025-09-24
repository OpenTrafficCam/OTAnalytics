from OTAnalytics.application.use_cases.section_repository import GetCuttingSections
from OTAnalytics.application.use_cases.track_repository import GetAllTracks
from OTAnalytics.domain.section import SectionListObserver, SectionRepositoryEvent
from OTAnalytics.domain.track_dataset.track_dataset import EmptyTrackIdSet, TrackIdSet
from OTAnalytics.domain.track_id_provider import TrackIdProvider
from OTAnalytics.domain.track_repository import TrackListObserver, TrackRepositoryEvent


class TrackIdsInsideCuttingSections(TrackIdProvider):
    def __init__(
        self, get_tracks: GetAllTracks, get_cutting_sections: GetCuttingSections
    ):
        self._get_tracks = get_tracks
        self._get_cutting_sections = get_cutting_sections

    def get_ids(self) -> TrackIdSet:
        track_dataset = self._get_tracks.as_dataset()
        cutting_sections = self._get_cutting_sections()
        if not cutting_sections:
            return EmptyTrackIdSet()

        return track_dataset.ids_inside(cutting_sections)


class CachedTrackIdsInsideCuttingSections(
    TrackIdsInsideCuttingSections, TrackListObserver, SectionListObserver
):
    def __init__(
        self,
        get_tracks: GetAllTracks,
        get_cutting_sections: GetCuttingSections,
    ) -> None:
        super().__init__(get_tracks, get_cutting_sections)
        self._cached_ids: TrackIdSet = self.__get_empty_cache()

    def get_ids(self) -> TrackIdSet:
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

    def _remove_track_ids(self, remove_track_ids: TrackIdSet) -> None:
        self._cached_ids = self._cached_ids.difference(remove_track_ids)

    def __get_empty_cache(self) -> TrackIdSet:
        return EmptyTrackIdSet()
