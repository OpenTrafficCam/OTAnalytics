from pathlib import Path
from typing import Awaitable, Callable

from OTAnalytics.application.parser.config_parser import ConfigParser, OtConfig
from OTAnalytics.application.parser.deserializer import Deserializer
from OTAnalytics.application.project_location import ValidateProjectLocation
from OTAnalytics.application.state import ConfigurationFile
from OTAnalytics.application.use_cases.add_new_remark import AddNewRemark
from OTAnalytics.application.use_cases.flow_repository import (
    AddAllFlows,
    FlowAlreadyExists,
)
from OTAnalytics.application.use_cases.load_track_files import LoadTrackFiles
from OTAnalytics.application.use_cases.reset_application import ResetApplication
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
        reset_application: ResetApplication,
        config_parser: ConfigParser,
        update_project: ProjectUpdater,
        add_videos: AddAllVideos,
        add_sections: AddAllSections,
        add_flows: AddAllFlows,
        load_track_files: LoadTrackFiles,
        add_new_remark: AddNewRemark,
        deserialize: Deserializer,
        validate_project_location: ValidateProjectLocation,
    ) -> None:
        self._add_new_remark = add_new_remark
        self._reset_application = reset_application
        self._config_parser = config_parser
        self._update_project = update_project
        self._add_videos = add_videos
        self._add_sections = add_sections
        self._add_flows = add_flows
        self._load_track_files = load_track_files
        self._deserialize = deserialize
        self._validate_project_location = validate_project_location
        self._subject = Subject[ConfigurationFile]()

    def load(self, file: Path) -> None:
        """Load an otconfig and its track files, blocking.

        For use outside an event loop only, such as preloading a config file given
        on the command line at startup. Inside an event loop use `load_async`.

        Args:
            file (Path): the otconfig file.
        """
        self._apply(file, self._load_track_files)

    async def load_async(self, file: Path) -> None:
        """Load an otconfig and its track files, keeping the ui responsive.

        Args:
            file (Path): the otconfig file.
        """
        await self._apply_async(file, self._load_track_files.load)

    def _apply(self, file: Path, load_track_files: Callable[[list], None]) -> None:
        config = self._begin(file)
        try:
            self._publish_before_tracks(config)
            load_track_files(list(config.analysis.track_files))
            self._publish_after_tracks(file, config)
        except (SectionAlreadyExists, FlowAlreadyExists) as cause:
            self._abort(cause)

    async def _apply_async(
        self, file: Path, load_track_files: Callable[[list], Awaitable[None]]
    ) -> None:
        config = self._begin(file)
        try:
            self._publish_before_tracks(config)
            await load_track_files(list(config.analysis.track_files))
            self._publish_after_tracks(file, config)
        except (SectionAlreadyExists, FlowAlreadyExists) as cause:
            self._abort(cause)

    def _begin(self, file: Path) -> OtConfig:
        """Reset, parse, and refuse a project this installation cannot read.

        Validating here rather than after `_publish_before_tracks` is what keeps
        the load all-or-nothing without `_abort`: nothing has been published
        yet, so a refusal leaves the application exactly as the reset left it.
        """
        self._reset_application.reset()
        config = self._config_parser.parse(file)
        self._validate_project_location(config.s3_key_prefix)
        return config

    def _publish_before_tracks(self, config: OtConfig) -> None:
        self._update_project(
            config.project.name, config.project.start_date, config.project.metadata
        )
        self._add_videos.add(config.videos)
        self._add_sections.add(config.sections)
        self._add_flows.add(config.flows)

    def _publish_after_tracks(self, file: Path, config: OtConfig) -> None:
        if config.remark:
            self._add_new_remark.add(config.remark)
        self._subject.notify(ConfigurationFile(file, self._deserialize(file)))

    def _abort(self, cause: Exception) -> None:
        self._reset_application.reset()
        raise UnableToLoadOtconfigFile(
            "Error while loading otconfig file. Abort loading!"
        ) from cause

    def register(self, observer: OBSERVER[ConfigurationFile]) -> None:
        self._subject.register(observer)


class UnableToLoadOtconfigFile(Exception):
    pass
