from OTAnalytics.application.use_cases.section_repository import GetCuttingSections
from OTAnalytics.application.use_cases.track_repository import GetAllTracks
from OTAnalytics.domain.section import SectionId
from OTAnalytics.domain.track import TrackId
from OTAnalytics.domain.types import EventType


class TrackIdsInsideCuttingSections:
    def __init__(
        self, get_tracks: GetAllTracks, get_cutting_sections: GetCuttingSections
    ):
        self._get_tracks = get_tracks
        self._get_cutting_sections = get_cutting_sections

    def __call__(self) -> set[TrackId]:
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


def contains_true(section_data: list[tuple[SectionId, list[bool]]]) -> bool:
    for _, bool_list in section_data:
        if any(bool_list):
            return True
    return False
