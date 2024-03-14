from pathlib import Path
from unittest.mock import Mock

import pytest

from OTAnalytics.application.state import ConfigurationFile
from OTAnalytics.application.use_cases.config_has_changed import (
    ConfigHasChanged,
    InvalidConfigFile,
    NoExistingConfigFound,
    OtconfigHasChanged,
    OtflowHasChanged,
)


class TestOtconfigHasChanged:
    @pytest.mark.parametrize(
        "previous_data,current_data, expected",
        [
            (
                {"first-section": "I am first"},
                {
                    "first-section": "I am first",
                    "second-section": "I am second",
                },
                True,
            ),
            (
                {"first-section": "I am first"},
                {"first-section": "I am first"},
                False,
            ),
        ],
    )
    def test_has_changed(
        self,
        previous_data: dict,
        current_data: dict,
        expected: bool,
    ) -> None:
        current_project = Mock()
        videos = Mock()
        sections = Mock()
        flows = Mock()
        get_sections = Mock()
        get_flows = Mock()
        get_current_project = Mock()
        get_videos = Mock()
        config_parser = Mock()
        deserialize = Mock()

        get_sections.return_value = sections
        get_flows.get.return_value = flows
        get_current_project.get.return_value = current_project
        get_videos.get.return_value = videos
        deserialize.return_value = previous_data
        config_parser.convert.return_value = current_data

        use_case = OtconfigHasChanged(
            config_parser,
            get_sections,
            get_flows,
            get_current_project,
            get_videos,
            deserialize,
        )
        otconfig_file = Mock()

        assert use_case.has_changed(otconfig_file) is expected
        deserialize.assert_called_once_with(otconfig_file)
        config_parser.convert.assert_called_once_with(
            current_project,
            videos,
            sections,
            flows,
            otconfig_file,
        )
        get_current_project.get.assert_called_once()
        get_videos.get.assert_called_once()
        get_sections.assert_called_once()
        get_flows.get.assert_called_once()


class TestOtflowHasChanged:
    @pytest.mark.parametrize(
        "previous_data,current_data, expected",
        [
            (
                {"first-section": "I am first"},
                {
                    "first-section": "I am first",
                    "second-section": "I am second",
                },
                True,
            ),
            (
                {"first-section": "I am first"},
                {"first-section": "I am first"},
                False,
            ),
        ],
    )
    def test_has_changed(
        self,
        previous_data: dict,
        current_data: dict,
        expected: bool,
    ) -> None:
        sections = Mock()
        flows = Mock()
        get_sections = Mock()
        get_flows = Mock()
        deserialize = Mock()
        flow_parser = Mock()

        get_sections.return_value = sections
        get_flows.get.return_value = flows
        deserialize.return_value = previous_data
        flow_parser.convert.return_value = current_data

        use_case = OtflowHasChanged(flow_parser, get_sections, get_flows, deserialize)
        otflow_file = Mock()

        assert use_case.has_changed(otflow_file) is expected
        deserialize.assert_called_once_with(otflow_file)
        flow_parser.convert.assert_called_once_with(sections, flows)


class TestConfigHasChanged:
    def test_has_changed_otconfig(self) -> None:
        otconfig_file = Path("path/to/my.otconfig")
        config_file = ConfigurationFile(otconfig_file, Mock())

        otconfig_has_changed = Mock()
        otflow_has_changed = Mock()
        file_state = Mock()
        last_saved_config = Mock()

        last_saved_config.get.return_value = config_file
        file_state.last_saved_config = last_saved_config
        otconfig_has_changed.has_changed.return_value = True

        use_case = ConfigHasChanged(
            otconfig_has_changed, otflow_has_changed, file_state
        )

        assert use_case.has_changed() is True
        last_saved_config.get.assert_called_once()
        otconfig_has_changed.has_changed.assert_called_once_with(otconfig_file)
        otflow_has_changed.has_changed.assert_not_called()

    def test_has_changed_otflow(self) -> None:
        otflow_file = Path("path/to/my.otflow")
        config_file = ConfigurationFile(otflow_file, Mock())

        otconfig_has_changed = Mock()
        otflow_has_changed = Mock()
        file_state = Mock()
        last_saved_config = Mock()

        last_saved_config.get.return_value = config_file
        file_state.last_saved_config = last_saved_config
        otflow_has_changed.has_changed.return_value = True

        use_case = ConfigHasChanged(
            otconfig_has_changed, otflow_has_changed, file_state
        )

        assert use_case.has_changed() is True
        last_saved_config.get.assert_called_once()
        otflow_has_changed.has_changed.assert_called_once_with(otflow_file)
        otconfig_has_changed.has_changed.assert_not_called()

    def test_has_changed_raise_invalid_config_file_error(self) -> None:
        some_file = Path("path/to/my.txt")
        config_file = ConfigurationFile(some_file, Mock())

        otconfig_has_changed = Mock()
        otflow_has_changed = Mock()
        file_state = Mock()
        last_saved_config = Mock()

        last_saved_config.get.return_value = config_file
        file_state.last_saved_config = last_saved_config

        use_case = ConfigHasChanged(
            otconfig_has_changed, otflow_has_changed, file_state
        )

        with pytest.raises(InvalidConfigFile):
            use_case.has_changed()
        otflow_has_changed.has_changed.assert_not_called()
        otconfig_has_changed.has_changed.assert_not_called()

    def test_has_changed_raise_no_existing_config_found(self) -> None:
        otconfig_has_changed = Mock()
        otflow_has_changed = Mock()
        file_state = Mock()
        last_saved_config = Mock()

        last_saved_config.get.return_value = None
        file_state.last_saved_config = last_saved_config

        use_case = ConfigHasChanged(
            otconfig_has_changed, otflow_has_changed, file_state
        )

        with pytest.raises(NoExistingConfigFound):
            use_case.has_changed()
        otflow_has_changed.has_changed.assert_not_called()
        otconfig_has_changed.has_changed.assert_not_called()
