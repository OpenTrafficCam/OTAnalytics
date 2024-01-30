from abc import ABC
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from OTAnalytics.application import project
from OTAnalytics.application.config_specification import OtConfigDefaultValueProvider
from OTAnalytics.application.datastore import FlowParser, VideoParser
from OTAnalytics.application.parser.config_parser import (
    AnalysisConfig,
    ConfigParser,
    ExportConfig,
    OtConfig,
)
from OTAnalytics.application.project import Project
from OTAnalytics.domain import flow, section, video
from OTAnalytics.domain.flow import Flow
from OTAnalytics.domain.section import Section
from OTAnalytics.domain.video import Video
from OTAnalytics.plugin_parser.json_parser import parse_json, write_json
from OTAnalytics.plugin_parser.otvision_parser import _validate_data

PROJECT: str = "project"
ANALYSIS = "analysis"
TRACKS = "tracks"
DO_EVENTS = "do_events"
DO_COUNTING = "do_counting"
EXPORT = "export"
EVENT_FORMATS = "event_formats"
SAVE_NAME = "save_name"
SAVE_SUFFIX = "save_suffix"
COUNT_INTERVALS = "count_intervals"
NUM_PROCESSES = "num_processes"
LOGFILE = "logfile"
DEBUG = "debug"
PATH = "path"


class OtConfigFormatFixer(ABC):
    def fix(self, content: dict) -> dict:
        raise NotImplementedError


class MultiFixer(OtConfigFormatFixer):
    def __init__(self, fixer: list[OtConfigFormatFixer]) -> None:
        self._fixer = fixer

    def fix(self, content: dict) -> dict:
        result = content
        for fixer in self._fixer:
            result = fixer.fix(result)
        return result


class FixMissingAnalysis(OtConfigFormatFixer):
    def __init__(self, run_config: OtConfigDefaultValueProvider) -> None:
        self._run_config = run_config

    def fix(self, content: dict) -> dict:
        if ANALYSIS in content.keys():
            return content
        content[ANALYSIS] = self._create_analysis_block()
        return content

    def _create_analysis_block(self) -> dict:
        return {
            DO_EVENTS: self._run_config.do_events,
            DO_COUNTING: self._run_config.do_counting,
            TRACKS: self._run_config.track_files,
            EXPORT: {
                EVENT_FORMATS: self._run_config.event_formats,
                SAVE_NAME: self._run_config.save_name,
                SAVE_SUFFIX: self._run_config.save_suffix,
                COUNT_INTERVALS: self._run_config.count_intervals,
            },
            NUM_PROCESSES: self._run_config.num_processes,
            LOGFILE: self._run_config.log_file,
            DEBUG: self._run_config.debug,
        }


class OtConfigParser(ConfigParser):
    def __init__(
        self,
        format_fixer: OtConfigFormatFixer,
        video_parser: VideoParser,
        flow_parser: FlowParser,
    ) -> None:
        self._format_fixer = format_fixer
        self._video_parser = video_parser
        self._flow_parser = flow_parser

    def parse(self, file: Path) -> OtConfig:
        base_folder = file.parent
        content = parse_json(file)
        fixed_content = self._format_fixer.fix(content)
        _project = self._parse_project(fixed_content[PROJECT])
        analysis_config = self._parse_analysis(fixed_content[ANALYSIS], base_folder)
        videos = self._video_parser.parse_list(fixed_content[video.VIDEOS], base_folder)
        sections, flows = self._flow_parser.parse_content(
            fixed_content[section.SECTIONS], fixed_content[flow.FLOWS]
        )
        return OtConfig(
            project=_project,
            analysis=analysis_config,
            videos=videos,
            sections=sections,
            flows=flows,
        )

    def _parse_project(self, data: dict) -> Project:
        _validate_data(data, [project.NAME, project.START_DATE])
        name = data[project.NAME]
        start_date = datetime.fromtimestamp(data[project.START_DATE], timezone.utc)
        return Project(name=name, start_date=start_date)

    def _parse_analysis(self, data: dict, base_folder: Path) -> AnalysisConfig:
        _validate_data(
            data,
            [
                DO_EVENTS,
                DO_COUNTING,
                TRACKS,
                EXPORT,
                NUM_PROCESSES,
                LOGFILE,
                DEBUG,
            ],
        )
        export_config = self._parse_export(data[EXPORT])
        analysis_config = AnalysisConfig(
            do_events=data[DO_EVENTS],
            do_counting=data[DO_COUNTING],
            track_files=self._parse_track_files(data[TRACKS], base_folder),
            export_config=export_config,
            num_processes=data[NUM_PROCESSES],
            logfile=Path(data[LOGFILE]),
        )
        return analysis_config

    def _parse_export(self, data: dict) -> ExportConfig:
        _validate_data(data, [SAVE_NAME, SAVE_SUFFIX, EVENT_FORMATS, COUNT_INTERVALS])
        export_config = ExportConfig(
            save_name=data[SAVE_NAME],
            save_suffix=data[SAVE_SUFFIX],
            event_formats=set(data[EVENT_FORMATS]),
            count_intervals=set(data[COUNT_INTERVALS]),
        )
        return export_config

    def _parse_track_files(
        self, track_files: list[str], base_folder: Path
    ) -> set[Path]:
        return {base_folder / _file for _file in track_files}

    def serialize(
        self,
        project: Project,
        video_files: Iterable[Video],
        sections: Iterable[Section],
        flows: Iterable[Flow],
        file: Path,
    ) -> None:
        """Serializes the project with the given videos, sections and flows into the
        file.

        Args:
            project (Project): description of the project
            video_files (Iterable[Video]): video files to reference
            sections (Iterable[Section]): sections to store
            flows (Iterable[Flow]): flows to store
            file (Path): output file

        Raises:
            StartDateMissing: if start date is not configured
        """
        parent_folder = file.parent
        project_content = project.to_dict()
        video_content = self._video_parser.convert(
            video_files,
            relative_to=parent_folder,
        )
        section_content = self._flow_parser.convert(sections, flows)
        content: dict[str, list[dict] | dict] = {PROJECT: project_content}
        content |= video_content
        content |= section_content
        write_json(data=content, path=file)
