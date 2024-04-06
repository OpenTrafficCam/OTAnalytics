from datetime import datetime
from unittest.mock import MagicMock, Mock

import pytest

from OTAnalytics.application.parser.config_parser import OtConfig
from OTAnalytics.application.state import ConfigurationFile
from OTAnalytics.application.use_cases.load_otconfig import (
    LoadOtconfig,
    UnableToLoadOtconfigFile,
)
from OTAnalytics.application.use_cases.section_repository import SectionAlreadyExists


class TestLoadOtconfig:
    @pytest.fixture
    def otconfig(self) -> OtConfig:
        project = Mock()
        project.name = "my project"
        project.start_date = datetime(2021, 1, 1)

        otconfig = Mock()
        otconfig.project = project
        otconfig.videos = Mock()
        otconfig.sections = Mock()
        otconfig.flows = Mock()
        return otconfig

    def test_load(self, otconfig: OtConfig) -> None:
        clear_repositories = Mock()
        config_parser = Mock()
        config_parser.parse.return_value = otconfig

        update_project = Mock()
        add_videos = Mock()
        add_sections = Mock()
        add_flows = Mock()
        deserialization_result = Mock()
        deserializer = Mock()
        deserializer.return_value = deserialization_result

        load_otconfig = LoadOtconfig(
            clear_repositories,
            config_parser,
            update_project,
            add_videos,
            add_sections,
            add_flows,
            deserializer,
        )
        observer = Mock()
        load_otconfig.register(observer)

        file = Mock()
        load_otconfig.load(file)

        update_project.assert_called_once_with(
            otconfig.project.name, otconfig.project.start_date
        )
        add_videos.add.assert_called_once_with(otconfig.videos)
        add_sections.add.assert_called_once_with(otconfig.sections)
        add_flows.add.assert_called_once_with(otconfig.flows)
        observer.assert_called_once_with(
            ConfigurationFile(file, deserialization_result)
        )
        clear_repositories.assert_called_once()

    def test_load_error(self, otconfig: OtConfig) -> None:
        clear_repositories = Mock()
        config_parser = Mock()
        config_parser.parse.return_value = otconfig

        add_sections = MagicMock()
        add_sections.add.side_effect = SectionAlreadyExists

        load_otconfig = LoadOtconfig(
            clear_repositories,
            config_parser,
            Mock(),
            Mock(),
            add_sections,
            Mock(),
            Mock(),
        )
        observer = Mock()
        load_otconfig.register(observer)
        file = Mock()
        with pytest.raises(UnableToLoadOtconfigFile):
            load_otconfig.load(file)

        assert clear_repositories.call_count == 2
        config_parser.parse.assert_called_once_with(file)
        observer.assert_not_called()
