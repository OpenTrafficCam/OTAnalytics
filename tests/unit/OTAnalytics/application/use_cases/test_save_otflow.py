from pathlib import Path
from unittest.mock import Mock

import pytest

from OTAnalytics.application.state import ConfigurationFile
from OTAnalytics.application.use_cases.save_otflow import NoSectionsToSave, SaveOtflow


def _create_otflow_file_save_state(otflow_file: Path | None) -> Mock:
    observable_property = Mock()
    observable_property.get.return_value = otflow_file
    state = Mock()
    state.last_saved_config = observable_property
    return state


class TestSaveOtflow:
    def test_save(self) -> None:
        sections = Mock()
        flows = Mock()

        get_sections = Mock()
        get_sections.return_value = sections
        get_flows = Mock()
        get_flows.get.return_value = flows

        converted_data = Mock()
        flow_parser = Mock()
        flow_parser.convert.return_value = converted_data
        some_file = Mock()
        state = Mock()

        save_otflow = SaveOtflow(flow_parser, get_sections, get_flows, state)
        save_otflow.save(some_file)

        flow_parser.serialize.assert_called_once_with(
            sections=sections, flows=flows, file=some_file
        )
        flow_parser.convert.assert_called_once_with(sections, flows)
        state.last_saved_config.set.assert_called_once_with(
            ConfigurationFile(some_file, converted_data)
        )

    def test_save_no_sections(self) -> None:
        get_sections = Mock()
        get_sections.return_value = []
        get_flows = Mock()

        flow_parser = Mock()
        some_file = Mock()

        state = Mock()
        save_otflow = SaveOtflow(flow_parser, get_sections, get_flows, state)

        with pytest.raises(NoSectionsToSave):
            save_otflow.save(some_file)

        flow_parser.serialize.assert_not_called()
        get_sections.assert_called_once()
        get_flows.get.assert_not_called()
        state.last_saved_config.set.assert_not_called()
