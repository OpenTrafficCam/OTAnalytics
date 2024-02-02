from typing import Iterable

from OTAnalytics.application.config import CLI_CUTTING_SECTION_MARKER
from OTAnalytics.application.logger import logger
from OTAnalytics.application.use_cases.cut_tracks_with_sections import (
    CutTracksIntersectingSection,
)
from OTAnalytics.domain.section import Section, SectionType


class ApplyCliCuts:
    def __init__(self, cut_tracks: CutTracksIntersectingSection) -> None:
        self._cut_tracks = cut_tracks

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
        logger().info("Cut tracks with cutting sections...")
        for cutting_section in cutting_sections:
            logger().info(
                f"Cut tracks with cutting section '{cutting_section.name}'..."
            )
            self._cut_tracks(
                cutting_section, preserve_cutting_section=preserve_cutting_sections
            )
        logger().info("Finished cutting all tracks")
