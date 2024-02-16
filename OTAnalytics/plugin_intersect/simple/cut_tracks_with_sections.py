from typing import Iterable

from OTAnalytics.application.use_cases.cut_tracks_with_sections import (
    CutTracksDto,
    CutTracksIntersectingSection,
)
from OTAnalytics.application.use_cases.section_repository import (
    GetSectionsById,
    RemoveSection,
)
from OTAnalytics.application.use_cases.track_repository import (
    AddAllTracks,
    GetAllTracks,
    RemoveTracks,
)
from OTAnalytics.domain.observer import OBSERVER, Subject
from OTAnalytics.domain.section import (
    Section,
    SectionId,
    SectionRepositoryEvent,
    SectionType,
)
from OTAnalytics.domain.types import EventType


class SimpleCutTracksIntersectingSection(CutTracksIntersectingSection):
    """Implementation of `CutTracksIntersectingSection`

    Args:
        get_sections_by_id (GetSectionsById): get sections by id.
        get_tracks (GetAllTracks): get all tracks.
        add_all_tracks (AddAllTracks): used to add all tracks to the track
            repository.
        remove_tracks (RemoveTracks): used to remove original tracks that have been
            cut.
        remove_section (RemoveSection): used to remove the cutting section.
    """

    def __init__(
        self,
        get_sections_by_id: GetSectionsById,
        get_tracks: GetAllTracks,
        add_all_tracks: AddAllTracks,
        remove_tracks: RemoveTracks,
        remove_section: RemoveSection,
    ) -> None:
        self._subject: Subject[CutTracksDto] = Subject[CutTracksDto]()

        self._get_sections_by_id = get_sections_by_id
        self._get_tracks = get_tracks
        self._add_all_tracks = add_all_tracks
        self._remove_tracks = remove_tracks
        self._remove_section = remove_section

    def __call__(
        self, cutting_section: Section, preserve_cutting_section: bool = False
    ) -> None:
        track_dataset = self._get_tracks.as_dataset()
        cut_tracks_dataset, ids_of_cut_tracks = track_dataset.cut_with_section(
            cutting_section, cutting_section.get_offset(EventType.SECTION_ENTER)
        )
        self._remove_tracks(ids_of_cut_tracks)
        self._add_all_tracks(cut_tracks_dataset)
        if not preserve_cutting_section:
            self._remove_section(cutting_section.id)
        self._subject.notify(
            CutTracksDto(cutting_section.name, list(ids_of_cut_tracks))
        )

    def register(self, observer: OBSERVER[CutTracksDto]) -> None:
        self._subject.register(observer)

    def notify_sections(self, section_event: SectionRepositoryEvent) -> None:
        self.__do(section_event.added)

    def __do(self, sections: Iterable[SectionId]) -> None:
        for section in self._get_sections_by_id(sections):
            if section.get_type() == SectionType.CUTTING:
                self.__call__(section)

    def notify_section_changed(self, section_id: SectionId) -> None:
        self.__do([section_id])
