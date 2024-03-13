from pathlib import Path

from OTAnalytics.application.parser.config_parser import ConfigParser
from OTAnalytics.application.use_cases.clear_repositories import ClearRepositories
from OTAnalytics.application.use_cases.flow_repository import (
    AddAllFlows,
    FlowAlreadyExists,
)
from OTAnalytics.application.use_cases.section_repository import (
    AddAllSections,
    SectionAlreadyExists,
)
from OTAnalytics.application.use_cases.update_project import ProjectUpdater
from OTAnalytics.application.use_cases.video_repository import AddAllVideos
from OTAnalytics.domain.observer import OBSERVER, Subject


class LoadOtconfig:
    def __init__(
        self,
        clear_repositories: ClearRepositories,
        config_parser: ConfigParser,
        update_project: ProjectUpdater,
        add_videos: AddAllVideos,
        add_sections: AddAllSections,
        add_flows: AddAllFlows,
    ) -> None:

        self._clear_repositories = clear_repositories
        self._config_parser = config_parser
        self._update_project = update_project
        self._add_videos = add_videos
        self._add_sections = add_sections
        self._add_flows = add_flows
        self._subject = Subject[Path]()

    def load(self, file: Path) -> None:
        self._clear_repositories()
        config = self._config_parser.parse(file)
        try:
            self._update_project(config.project.name, config.project.start_date)
            self._add_videos.add(config.videos)
            self._add_sections.add(config.sections)
            self._add_flows.add(config.flows)
            self._subject.notify(file)
        except (SectionAlreadyExists, FlowAlreadyExists) as cause:
            self._clear_repositories()
            raise UnableToLoadOtconfigFile(
                "Error while loading otconfig file. Abort loading!"
            ) from cause

    def register(self, observer: OBSERVER[Path]) -> None:
        self._subject.register(observer)


class UnableToLoadOtconfigFile(Exception):
    pass
