from pathlib import Path
from unittest.mock import Mock

import pytest

from OTAnalytics.application.use_cases.save_otflow import (
    NoExistingFileToSave,
    NoSectionsToSave,
    QuickSaveOTFlow,
    SaveOTFlow,
)


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


class TestQuickSaveOTFlow:

    def test_save(self) -> None:
        last_saved_otflow_file = Path("path/to/my_flows.otflow")
        save_otflow = Mock()
        state = self._create_otflow_file_save_state(last_saved_otflow_file)

        quick_save = QuickSaveOTFlow(state, save_otflow)
        quick_save.save()

        state.last_saved.get.assert_called_once()
        save_otflow.save.assert_called_once_with(last_saved_otflow_file)

    def _create_otflow_file_save_state(self, otflow_file: Path | None) -> Mock:
        observable_property = Mock()
        observable_property.get.return_value = otflow_file
        state = Mock()
        state.last_saved = observable_property
        return state

    def test_save_no_flow_file(self) -> None:
        save_otflow = Mock()
        state = self._create_otflow_file_save_state(None)

        quick_save = QuickSaveOTFlow(state, save_otflow)
        with pytest.raises(NoExistingFileToSave):
            quick_save.save()

        state.last_saved.get.assert_called_once()
        save_otflow.save.assert_not_called()
