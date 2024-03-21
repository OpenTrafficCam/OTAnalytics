from pathlib import Path
from unittest.mock import Mock

import pytest

from OTAnalytics.application.state import ConfigurationFile
from OTAnalytics.application.use_cases.quick_save_configuration import (
    NoExistingFileToSave,
    QuickSaveConfiguration,
    UnsupportedConfiguration,
)


class TestQuickSaveConfiguration:
    def test_save_otflow(self) -> None:
        config_file = ConfigurationFile(Path("path/to/my.otflow"), Mock())

        save_otflow = Mock()
        save_otconfig = Mock()
        state = _create_otflow_file_save_state(config_file)

        quick_save = QuickSaveConfiguration(state, save_otflow, save_otconfig)
        quick_save.save()

        state.last_saved_config.get.assert_called_once()
        save_otflow.save.assert_called_once_with(config_file.file)
        save_otconfig.save.assert_not_called()

    def test_save_otconfig(self) -> None:
        config_file = ConfigurationFile(Path("path/to/my.otconfig"), Mock())

        save_otflow = Mock()
        save_otconfig = Mock()
        state = _create_otflow_file_save_state(config_file)

        quick_save = QuickSaveConfiguration(state, save_otflow, save_otconfig)
        quick_save.save()

        state.last_saved_config.get.assert_called_once()
        save_otconfig.assert_called_once_with(config_file.file)
        save_otflow.save.assert_not_called()

    def test_save_not_supported_format(self) -> None:
        config_file = ConfigurationFile(
            Path("path/to/not-supported-format.txt"), Mock()
        )
        save_otflow = Mock()
        save_otconfig = Mock()
        state = _create_otflow_file_save_state(config_file)

        quick_save = QuickSaveConfiguration(state, save_otflow, save_otconfig)
        with pytest.raises(UnsupportedConfiguration):
            quick_save.save()

        state.last_saved_config.get.assert_called_once()
        save_otconfig.assert_not_called()
        save_otflow.save.assert_not_called()

    def test_save_no_configuration_file(self) -> None:
        save_otflow = Mock()
        save_otconfig = Mock()
        state = _create_otflow_file_save_state(None)

        quick_save = QuickSaveConfiguration(state, save_otflow, save_otconfig)
        with pytest.raises(NoExistingFileToSave):
            quick_save.save()

        state.last_saved_config.get.assert_called_once()
        save_otflow.save.assert_not_called()
        save_otconfig.assert_not_called()


def _create_otflow_file_save_state(config_file: ConfigurationFile | None) -> Mock:
    observable_property = Mock()
    observable_property.get.return_value = config_file
    state = Mock()
    state.last_saved_config = observable_property
    return state
