from unittest.mock import Mock, call

import pytest

from OTAnalytics.application.config import (
    CLI_CUTTING_SECTION_MARKER,
    CUTTING_SECTION_MARKER,
)
from OTAnalytics.application.use_cases.apply_cli_cuts import ApplyCliCuts
from OTAnalytics.domain.section import Section, SectionId, SectionType


@pytest.fixture
def cli_cutting_section() -> Section:
    section_id = SectionId(f"{CLI_CUTTING_SECTION_MARKER}_cli_section")
    my_section = Mock()
    my_section.name = section_id.id
    my_section.get_type.return_value = SectionType.LINE
    my_section.id = section_id
    return my_section


@pytest.fixture
def normal_cutting_section() -> Section:
    section_id = SectionId(f"{CUTTING_SECTION_MARKER}_normal_section")
    my_section = Mock()
    my_section.name = section_id.id
    my_section.get_type.return_value = SectionType.CUTTING
    my_section.id = section_id
    return my_section


class TestApplyCliCuts:
    def test_apply(
        self, cli_cutting_section: Section, normal_cutting_section: Section
    ) -> None:
        sections = [normal_cutting_section, cli_cutting_section]
        cut_tracks = Mock()

        apply_cli_cuts = ApplyCliCuts(cut_tracks)

        apply_cli_cuts.apply(sections, preserve_cutting_sections=True)

        assert cut_tracks.call_args_list == [
            call(cli_cutting_section, preserve_cutting_section=True),
            call(normal_cutting_section, preserve_cutting_section=True),
        ]
