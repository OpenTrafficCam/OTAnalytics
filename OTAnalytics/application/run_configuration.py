from pathlib import Path
from typing import Callable, Sequence

from OTAnalytics.application.config import (
    DEFAULT_COUNTING_INTERVAL_IN_MINUTES,
    DEFAULT_EVENTLIST_FILE_TYPE,
    DEFAULT_NUM_PROCESSES,
)
from OTAnalytics.application.datastore import FlowParser
from OTAnalytics.application.logger import DEFAULT_LOG_FILE
from OTAnalytics.application.parser.cli_parser import CliArguments
from OTAnalytics.application.parser.config_parser import OtConfig
from OTAnalytics.application.project import Project
from OTAnalytics.domain.flow import Flow
from OTAnalytics.domain.section import Section
from OTAnalytics.domain.video import Video


class RunConfiguration:
    def __init__(
        self,
        flow_parser: FlowParser,
        cli_args: CliArguments,
        otconfig: OtConfig | None = None,
    ) -> None:
        self._flow_parser = flow_parser
        self._cli_args = cli_args
        self._otconfig = otconfig
        self._set_sections_and_flows()

    def _set_sections_and_flows(self) -> None:
        if self._otconfig:
            self._sections = self._otconfig.sections
            self._flows = self._otconfig.flows
        elif otflow_file := self._cli_args.otflow_file:
            sections, flows = self._flow_parser.parse(Path(otflow_file))
            self._sections = sections
            self._flows = flows
        else:
            self._sections = []
            self._flows = []

    @property
    def start_cli(self) -> bool:
        return self._cli_args.start_cli

    @property
    def debug(self) -> bool:
        return self._cli_args.debug

    @property
    def config_file(self) -> Path | None:
        if config_file := self._cli_args.config_file:
            return Path(config_file)
        return None

    @property
    def track_files(self) -> set[Path]:
        if self._cli_args.track_files:
            return {Path(track) for track in self._cli_args.track_files}
        if self._otconfig:
            return self._otconfig.analysis.track_files
        return set()

    @property
    def otflow(self) -> Path | None:
        if self._cli_args.otflow_file:
            return Path(self._cli_args.otflow_file)
        return None

    @property
    def save_name(self) -> Path:
        save_dir = self._get_save_dir()
        save_stem = self._get_save_stem()
        save_suffix = self.save_suffix

        return save_dir / f"{save_stem}{save_suffix}"

    def _get_save_dir(self) -> Path:
        save_name = self._get_save_name()
        if not save_name:
            if self.config_file:
                return self.config_file.parent

            if self.otflow:
                return self.otflow.parent
        if self.config_file:
            return self.config_file.parent
        # Save name is either absolute or relative path.
        return Path(save_name).expanduser().parent

    def _get_save_name(self) -> str:
        if cli_save_name := self._cli_args.save_name:
            return cli_save_name
        if self._otconfig:
            return self._otconfig.analysis.export_config.save_name
        return ""

    def _get_save_stem(self) -> str:
        save_name = self._get_save_name()
        if save_name:
            return Path(save_name).stem
        if self.config_file:
            return self.config_file.stem
        if self.otflow:
            return self.otflow.stem
        return ""

    @property
    def save_suffix(self) -> str:
        if self._cli_args.save_suffix:
            return f"_{self._cli_args.save_suffix}"
        if self._otconfig:
            if suffix := self._otconfig.analysis.export_config.save_suffix:
                return f"_{suffix}"
        return ""

    @property
    def event_formats(self) -> set[str]:
        if self._cli_args.event_formats:
            return {self._cli_args.event_formats}
        if self._otconfig:
            if event_formats := self._otconfig.analysis.export_config.event_formats:
                return event_formats
        return {DEFAULT_EVENTLIST_FILE_TYPE}

    @property
    def count_intervals(self) -> set[int]:
        if self._cli_args.count_interval:
            return {self._cli_args.count_interval}
        if self._otconfig:
            return self._otconfig.analysis.export_config.count_intervals
        return {DEFAULT_COUNTING_INTERVAL_IN_MINUTES}

    @property
    def num_processes(self) -> int:
        if self._cli_args.num_processes:
            return self._cli_args.num_processes
        if self._otconfig:
            return self._otconfig.analysis.num_processes
        return DEFAULT_NUM_PROCESSES

    @property
    def log_file(self) -> Path:
        if self._cli_args.log_file:
            return Path(self._cli_args.log_file)
        if self._otconfig:
            return self._otconfig.analysis.logfile
        return DEFAULT_LOG_FILE

    @property
    def logfile_overwrite(self) -> bool:
        return self._cli_args.logfile_overwrite

    @property
    def do_events(self) -> bool:
        if self._otconfig:
            return self._otconfig.analysis.do_events
        return True

    @property
    def do_counting(self) -> bool:
        if self._otconfig:
            return self._otconfig.analysis.do_counting
        return True

    @property
    def project(self) -> Project | None:
        if self._otconfig:
            return self._otconfig.project
        return None

    @property
    def videos(self) -> Sequence[Video]:
        if self._otconfig:
            return self._otconfig.videos
        return []

    @property
    def sections(self) -> Sequence[Section]:
        return self._sections

    @property
    def flows(self) -> Sequence[Flow]:
        return self._flows


RunConfigurationBuilder = Callable[[CliArguments, OtConfig | None], RunConfiguration]
