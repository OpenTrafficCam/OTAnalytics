from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from OTAnalytics.application import project
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


class OtConfigParser(ConfigParser):
    def __init__(
        self,
        video_parser: VideoParser,
        flow_parser: FlowParser,
    ) -> None:
        self._video_parser = video_parser
        self._flow_parser = flow_parser

    def parse(self, file: Path) -> OtConfig:
        base_folder = file.parent
        content = parse_json(file)
        _project = self._parse_project(content[PROJECT])
        analysis_config = self._parse_analysis(content[ANALYSIS])
        videos = self._video_parser.parse_list(content[video.VIDEOS], base_folder)
        sections, flows = self._flow_parser.parse_content(
            content[section.SECTIONS], content[flow.FLOWS]
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

    def _parse_analysis(self, data: dict) -> AnalysisConfig:
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
            track_files=self._parse_track_files(data[TRACKS]),
            export_config=export_config,
            num_processes=data[NUM_PROCESSES],
            logfile=Path(data[LOGFILE]),
            debug=data[DEBUG],
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

    def _parse_track_files(self, track_files: list[str]) -> set[Path]:
        return {Path(_file) for _file in track_files}

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
