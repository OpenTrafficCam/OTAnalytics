from pathlib import Path

from OTAnalytics.application.parser.config_parser import ConfigParser
from OTAnalytics.application.parser.deserializer import Deserializer
from OTAnalytics.application.parser.flow_parser import FlowParser
from OTAnalytics.application.state import FileState
from OTAnalytics.application.use_cases.flow_repository import GetAllFlows
from OTAnalytics.application.use_cases.get_current_project import GetCurrentProject
from OTAnalytics.application.use_cases.section_repository import GetAllSections
from OTAnalytics.application.use_cases.video_repository import GetAllVideos


class OtconfigHasChanged:
    def __init__(
        self,
        config_parser: ConfigParser,
        get_sections: GetAllSections,
        get_flows: GetAllFlows,
        get_current_project: GetCurrentProject,
        get_videos: GetAllVideos,
        deserialize: Deserializer,
    ):
        self._config_parser = config_parser
        self._get_sections = get_sections
        self._get_flows = get_flows
        self._get_current_project = get_current_project
        self._get_videos = get_videos
        self._deserialize = deserialize

    def has_changed(self, file: Path) -> bool:
        prev_content = self._deserialize(file)
        current_content = self._config_parser.convert(
            self._get_current_project.get(),
            self._get_videos.get(),
            self._get_sections(),
            self._get_flows.get(),
            file,
        )
        return prev_content != current_content


class OtflowHasChanged:
    def __init__(
        self,
        flow_parser: FlowParser,
        get_sections: GetAllSections,
        get_flows: GetAllFlows,
        deserialize: Deserializer,
    ):
        self._flow_parser = flow_parser
        self._get_sections = get_sections
        self._get_flows = get_flows
        self._deserialize = deserialize

    def has_changed(self, file: Path) -> bool:
        prev_content = self._deserialize(file)
        current_content = self._flow_parser.convert(
            self._get_sections(), self._get_flows.get()
        )
        return prev_content != current_content


class ConfigHasChanged:
    def __init__(
        self,
        otconfig_has_changed: OtconfigHasChanged,
        otflow_has_changed: OtflowHasChanged,
        file_state: FileState,
    ):
        self._otconfig_has_changed = otconfig_has_changed
        self._otflow_has_changed = otflow_has_changed
        self._file_state = file_state

    def has_changed(self) -> bool:
        if not (config_file := self._file_state.last_saved_config.get()):
            raise NoExistingConfigFound("No existing config file found")

        if config_file.is_otflow:
            return self._otflow_has_changed.has_changed(config_file.file)

        if config_file.is_otconfig:
            return self._otconfig_has_changed.has_changed(config_file.file)

        raise InvalidConfigFile(f"Config file '{config_file.file}' is invalid")


class NoExistingConfigFound(Exception):
    pass


class InvalidConfigFile(Exception):
    pass
