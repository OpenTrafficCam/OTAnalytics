from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from OTAnalytics.application import project
from OTAnalytics.application.datastore import (
    ConfigParser,
    FlowParser,
    OtConfig,
    VideoParser,
)
from OTAnalytics.application.project import Project
from OTAnalytics.domain import flow, section, video
from OTAnalytics.domain.flow import Flow
from OTAnalytics.domain.section import Section
from OTAnalytics.domain.video import Video
from OTAnalytics.plugin_parser.otvision_parser import (
    _parse,
    _validate_data,
    _write_json,
)

PROJECT: str = "project"


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
        content = _parse(file)
        project = self._parse_project(content[PROJECT])
        videos = self._video_parser.parse_list(content[video.VIDEOS], base_folder)
        sections, flows = self._flow_parser.parse_content(
            content[section.SECTIONS], content[flow.FLOWS]
        )
        return OtConfig(
            project=project,
            videos=videos,
            sections=sections,
            flows=flows,
        )

    def _parse_project(self, data: dict) -> Project:
        _validate_data(data, [project.NAME, project.START_DATE])
        name = data[project.NAME]
        start_date = datetime.fromtimestamp(data[project.START_DATE], timezone.utc)
        return Project(name=name, start_date=start_date)

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
        _write_json(data=content, path=file)
