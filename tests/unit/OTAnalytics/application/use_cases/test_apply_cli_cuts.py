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
        track_repository_size = Mock()
        track_repository_size.get.return_value = 2

        apply_cli_cuts = ApplyCliCuts(cut_tracks, track_repository_size)

        apply_cli_cuts.apply(sections, preserve_cutting_sections=True)
        apply_cli_cuts.apply(sections, preserve_cutting_sections=False)

        assert cut_tracks.call_args_list == [
            call(cli_cutting_section, preserve_cutting_section=True),
            call(normal_cutting_section, preserve_cutting_section=True),
            call(cli_cutting_section, preserve_cutting_section=False),
            call(normal_cutting_section, preserve_cutting_section=False),
        ]
        assert track_repository_size.get.call_count == 4

    def test_apply_empty_repository(self, cli_cutting_section: Section) -> None:
        cut_tracks = Mock()
        track_repository_size = Mock()
        track_repository_size.get.return_value = 0

        apply_cli_cuts = ApplyCliCuts(cut_tracks, track_repository_size)

        apply_cli_cuts.apply([cli_cutting_section], preserve_cutting_sections=True)

        cut_tracks.assert_not_called()
        assert track_repository_size.get.call_count == 2
