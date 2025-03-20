from typing import Iterable

from OTAnalytics.application.config import CLI_CUTTING_SECTION_MARKER
from OTAnalytics.application.logger import logger
from OTAnalytics.application.use_cases.cut_tracks_with_sections import (
    CutTracksIntersectingSection,
)
from OTAnalytics.application.use_cases.track_repository import TrackRepositorySize
from OTAnalytics.domain.section import Section, SectionType


class ApplyCliCuts:
    def __init__(
        self,
        cut_tracks: CutTracksIntersectingSection,
        track_repository_size: TrackRepositorySize,
    ) -> None:
        self._cut_tracks = cut_tracks
        self._track_repository_size = track_repository_size

    def apply(
        self, sections: Iterable[Section], preserve_cutting_sections: bool = False
    ) -> None:
        cutting_sections = sorted(
            [
                section
                for section in sections
                if section.get_type() == SectionType.CUTTING
                or section.name.startswith(CLI_CUTTING_SECTION_MARKER)
            ],
            key=lambda section: section.id.id,
        )
        logger().info(f"Track repository has size: {self._track_repository_size.get()}")
        logger().info("Cut tracks with cutting sections...")
        if self._track_repository_size.get() == 0:
            logger().info("No tracks to cut")
            return
        for cutting_section in cutting_sections:
            logger().info(
                f"Cut tracks with cutting section '{cutting_section.name}'..."
            )
            self._cut_tracks(
                cutting_section, preserve_cutting_section=preserve_cutting_sections
            )
        logger().info("Finished cutting all tracks")
