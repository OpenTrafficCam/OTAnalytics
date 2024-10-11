from pathlib import Path
from typing import Callable, Sequence

from OTAnalytics.application.config import (
    DEFAULT_COUNTING_INTERVAL_IN_MINUTES,
    DEFAULT_EVENTLIST_FILE_TYPE,
    DEFAULT_NUM_PROCESSES,
)
from OTAnalytics.application.config_specification import OtConfigDefaultValueProvider
from OTAnalytics.application.logger import DEFAULT_LOG_FILE
from OTAnalytics.application.parser.cli_parser import CliArguments
from OTAnalytics.application.parser.config_parser import OtConfig
from OTAnalytics.application.parser.flow_parser import FlowParser
from OTAnalytics.application.project import Project
from OTAnalytics.domain.flow import Flow
from OTAnalytics.domain.section import Section
from OTAnalytics.domain.video import Video


class RunConfigurationError(Exception):
    pass


class RunConfiguration(OtConfigDefaultValueProvider):
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
    def save_dir(self) -> Path:
        if self._cli_args.save_dir:
            return Path(self._cli_args.save_dir).expanduser()
        if self.config_file:
            return self.config_file.parent.expanduser()
        if self.otflow:
            return self.otflow.parent.expanduser()
        raise RunConfigurationError("No OTConfig nor OTFlow file passed.")

    @property
    def save_name(self) -> str:
        save_stem = self._get_save_stem()
        save_suffix = self.save_suffix
        return f"{save_stem}{save_suffix}"

    def _get_save_stem(self) -> str:
        save_name = self._get_save_name()
        if save_name:
            return Path(save_name).stem
        if self.config_file:
            return self.config_file.stem
        if self.otflow:
            return self.otflow.stem
        return ""

    def _get_save_name(self) -> str:
        if cli_save_name := self._cli_args.save_name:
            return cli_save_name
        if self._otconfig:
            return self._otconfig.analysis.export_config.save_name
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
            return set(self._cli_args.event_formats)
        if self._otconfig:
            if event_formats := self._otconfig.analysis.export_config.event_formats:
                return event_formats
        return {DEFAULT_EVENTLIST_FILE_TYPE}

    @property
    def count_intervals(self) -> set[int]:
        if self._cli_args.count_intervals:
            return set(self._cli_args.count_intervals)
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
        if self._otconfig and self._cli_args.config_file:
            base_dir = Path(self._cli_args.config_file).parent
            return base_dir / self._otconfig.analysis.logfile
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
    def do_export_tracks(self) -> bool:
        return self._cli_args.track_export

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

    @property
    def include_classes(self) -> frozenset[str]:
        if self._cli_args.include_classes is not None:
            return frozenset(self._cli_args.include_classes)
        return frozenset()

    @property
    def exclude_classes(self) -> frozenset[str]:
        if self._cli_args.exclude_classes is not None:
            return frozenset(self._cli_args.exclude_classes)
        return frozenset()

    @property
    def show_svz(self) -> bool:
        return self._cli_args.show_svz


RunConfigurationBuilder = Callable[[CliArguments, OtConfig | None], RunConfiguration]
