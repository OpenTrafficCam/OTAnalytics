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
        track_files = Mock()
        sections = Mock()
        flows = Mock()
        get_sections = Mock()
        get_flows = Mock()
        get_current_project = Mock()
        get_videos = Mock()
        get_track_files = Mock()
        config_parser = Mock()
        get_remark = Mock()
        remark = Mock()
        get_remark.get.return_value = remark
        get_sections.return_value = sections
        get_flows.get.return_value = flows
        get_current_project.get.return_value = current_project
        get_videos.get.return_value = videos
        get_track_files.return_value = track_files
        config_parser.convert.return_value = current_data

        use_case = OtconfigHasChanged(
            config_parser,
            get_sections,
            get_flows,
            get_current_project,
            get_videos,
            get_track_files,
            get_remark,
        )
        config_file = ConfigurationFile(Mock(), previous_data)

        assert use_case.has_changed(config_file) is expected
        config_parser.convert.assert_called_once_with(
            current_project,
            videos,
            track_files,
            sections,
            flows,
            config_file.file,
            remark,
        )
        get_current_project.get.assert_called_once()
        get_videos.get.assert_called_once()
        get_track_files.assert_called_once()
        get_sections.assert_called_once()
        get_flows.get.assert_called_once()
        get_remark.get.assert_called_once()


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
        flow_parser = Mock()

        get_sections.return_value = sections
        get_flows.get.return_value = flows
        flow_parser.convert.return_value = current_data

        use_case = OtflowHasChanged(flow_parser, get_sections, get_flows)
        config_file = ConfigurationFile(Mock(), previous_data)

        assert use_case.has_changed(config_file) is expected
        flow_parser.convert.assert_called_once_with(sections, flows)


class TestConfigHasChanged:
    def test_has_changed_otconfig(self) -> None:
        config_file = ConfigurationFile(Path("path/to/my.otconfig"), Mock())

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
        otconfig_has_changed.has_changed.assert_called_once_with(config_file)
        otflow_has_changed.has_changed.assert_not_called()

    def test_has_changed_otflow(self) -> None:
        config_file = ConfigurationFile(Path("path/to/my.otflow"), Mock())

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
        otflow_has_changed.has_changed.assert_called_once_with(config_file)
        otconfig_has_changed.has_changed.assert_not_called()

    def test_has_changed_raise_invalid_config_file_error(self) -> None:
        config_file = ConfigurationFile(Path("path/to/my.txt"), Mock())

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
