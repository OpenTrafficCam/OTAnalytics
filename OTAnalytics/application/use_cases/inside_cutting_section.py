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
        if cutting_sections is None:
            return set()
        else:
            offset = cutting_sections[0].get_offset(EventType.SECTION_ENTER)
            # set of all tracks where at least one coordinate is contained
            # by at least one cutting section
            result = set(
                track_id
                for track_id, section_data in (
                    track_dataset.contained_by_sections(
                        cutting_sections, offset
                    ).items()
                )
                if contains_true(section_data)
            )
            return result


def contains_true(section_data: list[tuple[SectionId, list[bool]]]) -> bool:
    for _, bool_list in section_data:
        if any(bool_list):
            return True
    return False
