from unittest.mock import Mock

import pytest

from OTAnalytics.application.use_cases.save_otflow import NoSectionsToSave, SaveOTFlow


class TestSaveOTFlow:
    def test_save(self) -> None:
        sections = Mock()
        flows = Mock()

        get_sections = Mock()
        get_sections.return_value = sections
        get_flows = Mock()
        get_flows.get.return_value = flows

        flow_parser = Mock()
        some_file = Mock()

        save_otflow = SaveOTFlow(flow_parser, get_sections, get_flows)
        save_otflow.save(some_file)

        flow_parser.serialize.assert_called_once_with(
            sections=sections, flows=flows, file=some_file
        )

    def test_save_no_sections(self) -> None:
        get_sections = Mock()
        get_sections.return_value = []
        get_flows = Mock()

        flow_parser = Mock()
        some_file = Mock()

        save_otflow = SaveOTFlow(flow_parser, get_sections, get_flows)

        with pytest.raises(NoSectionsToSave):
            save_otflow.save(some_file)

        flow_parser.serialize.assert_not_called()
        get_sections.assert_called_once()
        get_flows.get.assert_not_called()
