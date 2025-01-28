from pathlib import Path

from OTAnalytics.application.parser.config_parser import ConfigParser
from OTAnalytics.application.parser.deserializer import Deserializer
from OTAnalytics.application.state import ConfigurationFile
from OTAnalytics.application.use_cases.add_new_remark import AddNewRemark
from OTAnalytics.application.use_cases.clear_repositories import ClearRepositories
from OTAnalytics.application.use_cases.flow_repository import (
    AddAllFlows,
    FlowAlreadyExists,
)
from OTAnalytics.application.use_cases.load_track_files import LoadTrackFiles
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
        load_track_files: LoadTrackFiles,
        add_new_remark: AddNewRemark,
        deserialize: Deserializer,
    ) -> None:
        self._add_new_remark = add_new_remark
        self._clear_repositories = clear_repositories
        self._config_parser = config_parser
        self._update_project = update_project
        self._add_videos = add_videos
        self._add_sections = add_sections
        self._add_flows = add_flows
        self._load_track_files = load_track_files
        self._deserialize = deserialize
        self._subject = Subject[ConfigurationFile]()

    def load(self, file: Path) -> None:
        self._clear_repositories()
        config = self._config_parser.parse(file)
        try:
            self._update_project(
                config.project.name, config.project.start_date, config.project.metadata
            )
            self._add_videos.add(config.videos)
            self._add_sections.add(config.sections)
            self._add_flows.add(config.flows)
            self._load_track_files(list(config.analysis.track_files))
            if config.remark:
                self._add_new_remark.add(config.remark)
            self._subject.notify(
                ConfigurationFile(
                    file,
                    self._deserialize(file),
                )
            )
        except (SectionAlreadyExists, FlowAlreadyExists) as cause:
            self._clear_repositories()
            raise UnableToLoadOtconfigFile(
                "Error while loading otconfig file. Abort loading!"
            ) from cause

    def register(self, observer: OBSERVER[ConfigurationFile]) -> None:
        self._subject.register(observer)


class UnableToLoadOtconfigFile(Exception):
    pass
