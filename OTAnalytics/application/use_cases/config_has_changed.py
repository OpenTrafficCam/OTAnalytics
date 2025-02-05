from OTAnalytics.application.parser.config_parser import ConfigParser
from OTAnalytics.application.parser.flow_parser import FlowParser
from OTAnalytics.application.state import ConfigurationFile, FileState
from OTAnalytics.application.use_cases.flow_repository import GetAllFlows
from OTAnalytics.application.use_cases.get_current_project import GetCurrentProject
from OTAnalytics.application.use_cases.get_current_remark import GetCurrentRemark
from OTAnalytics.application.use_cases.section_repository import GetAllSections
from OTAnalytics.application.use_cases.track_repository import GetAllTrackFiles
from OTAnalytics.application.use_cases.video_repository import GetAllVideos


class OtconfigHasChanged:
    def __init__(
        self,
        config_parser: ConfigParser,
        get_sections: GetAllSections,
        get_flows: GetAllFlows,
        get_current_project: GetCurrentProject,
        get_videos: GetAllVideos,
        get_track_files: GetAllTrackFiles,
        get_remark: GetCurrentRemark,
    ):
        self._config_parser = config_parser
        self._get_sections = get_sections
        self._get_flows = get_flows
        self._get_current_project = get_current_project
        self._get_videos = get_videos
        self._get_track_files = get_track_files
        self._get_remark = get_remark

    def has_changed(self, prev_config: ConfigurationFile) -> bool:
        """
        Check if the OTConfig file has changed or not based on its content.

        Args:
            prev_config (ConfigurationFile): The path to the OTConfig file.

        Returns:
            bool: True if the OTConfig file has changed, False otherwise.
        """
        current_content = self._config_parser.convert(
            self._get_current_project.get(),
            self._get_videos.get(),
            self._get_track_files(),
            self._get_sections(),
            self._get_flows.get(),
            prev_config.file,
            self._get_remark.get(),
        )
        return prev_config.content != current_content


class OtflowHasChanged:
    def __init__(
        self,
        flow_parser: FlowParser,
        get_sections: GetAllSections,
        get_flows: GetAllFlows,
    ):
        self._flow_parser = flow_parser
        self._get_sections = get_sections
        self._get_flows = get_flows

    def has_changed(self, prev_config: ConfigurationFile) -> bool:
        """
        Method checking if the OTFlow file has changed or not based on its content.

        Args:
            prev_config (ConfigurationFile): The previous OTFlow config.

        Returns:
            bool: True if the OTFlow file has changed, False otherwise.
        """
        current_content = self._flow_parser.convert(
            self._get_sections(), self._get_flows.get()
        )
        return prev_config.content != current_content


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
        """
        Method checking if any of the OTConfig or OTFlow files have changed or not.

        Returns:
            bool: True if either an OTConfig or an OTFlow file has changed,
                False otherwise.

        Raises:
            NoExistingConfigFound: When no existing OTConfig or OTFlow file is found.
            InvalidConfigFile: When a file is encountered that does not have an
                OTConfig or OTFlow filetype.
        """
        if not (config_file := self._file_state.last_saved_config.get()):
            raise NoExistingConfigFound("No existing config file found")

        if config_file.is_otflow:
            return self._otflow_has_changed.has_changed(config_file)

        if config_file.is_otconfig:
            return self._otconfig_has_changed.has_changed(config_file)

        raise InvalidConfigFile(f"Config file '{config_file.file}' is invalid")


class NoExistingConfigFound(Exception):
    pass


class InvalidConfigFile(Exception):
    pass
