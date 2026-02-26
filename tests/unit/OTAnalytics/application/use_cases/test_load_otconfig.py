from dataclasses import dataclass
from datetime import datetime
from unittest.mock import MagicMock, Mock

import pytest

from OTAnalytics.application.parser.config_parser import OtConfig
from OTAnalytics.application.state import ConfigurationFile
from OTAnalytics.application.use_cases.load_otconfig import (
    LoadOtconfig,
    UnableToLoadOtconfigFile,
)
from OTAnalytics.application.use_cases.section_repository import SectionAlreadyExists

REMARK = "my remark"


class TestLoadOtconfig:
    def test_load(self) -> None:
        given = setup(
            project_name="my project",
            start_date=datetime(2021, 1, 1),
            track_files={"path/to/first.ottrk", "path/to/second.ottrk"},
            remark=REMARK,
            raise_error=False,
        )
        target = create_target(given)
        observer = Mock()
        target.register(observer)

        file = Mock()
        target.load(file)

        given.update_project.assert_called_once_with(
            given.otconfig.project.name,
            given.otconfig.project.start_date,
            given.otconfig.project.metadata,
        )
        given.add_videos.add.assert_called_once_with(given.otconfig.videos)
        given.add_sections.add.assert_called_once_with(given.otconfig.sections)
        given.add_flows.add.assert_called_once_with(given.otconfig.flows)
        given.load_track_files.assert_called_once_with(
            list(given.otconfig.analysis.track_files)
        )
        observer.assert_called_once_with(
            ConfigurationFile(file, given.deserialization_result)
        )
        given.reset_application.reset.assert_called_once()
        given.remark_repository.add.assert_called_once_with(REMARK)

    def test_load_error(self) -> None:
        given = setup(
            project_name="my project",
            start_date=datetime(2021, 1, 1),
            track_files={"path/to/first.ottrk", "path/to/second.ottrk"},
            remark=REMARK,
            raise_error=True,
        )
        target = create_target(given)
        observer = Mock()
        target.register(observer)
        file = Mock()

        with pytest.raises(UnableToLoadOtconfigFile):
            target.load(file)

        assert given.reset_application.reset.call_count == 2
        given.config_parser.parse.assert_called_once_with(file)
        observer.assert_not_called()
        given.remark_repository.add.assert_not_called()


@dataclass
class Given:
    otconfig: OtConfig
    reset_application: Mock
    config_parser: Mock
    update_project: Mock
    add_videos: Mock
    add_sections: Mock
    add_flows: Mock
    load_track_files: Mock
    remark_repository: Mock
    deserializer: Mock
    deserialization_result: Mock


def setup(
    project_name: str,
    start_date: datetime,
    track_files: set[str],
    remark: str,
    raise_error: bool,
) -> Given:
    otconfig = create_otconfig(project_name, start_date, track_files, remark)

    reset_application = Mock()
    config_parser = Mock()
    config_parser.parse.return_value = otconfig
    update_project = Mock()
    add_videos = Mock()
    add_flows = Mock()
    load_track_files = Mock()
    remark_repository = Mock()
    deserialization_result = Mock()
    deserializer = Mock()
    deserializer.return_value = deserialization_result

    if raise_error:
        add_sections = MagicMock()
        add_sections.add.side_effect = SectionAlreadyExists
    else:
        add_sections = Mock()

    return Given(
        otconfig=otconfig,
        reset_application=reset_application,
        config_parser=config_parser,
        update_project=update_project,
        add_videos=add_videos,
        add_sections=add_sections,
        add_flows=add_flows,
        load_track_files=load_track_files,
        remark_repository=remark_repository,
        deserializer=deserializer,
        deserialization_result=deserialization_result,
    )


def create_otconfig(
    project_name: str,
    start_date: datetime,
    track_files: set[str],
    remark: str,
) -> OtConfig:
    project = Mock()
    project.name = project_name
    project.start_date = start_date

    analysis = Mock()
    analysis.track_files = track_files

    otconfig = Mock()
    otconfig.project = project
    otconfig.videos = Mock()
    otconfig.sections = Mock()
    otconfig.flows = Mock()
    otconfig.analysis = analysis
    otconfig.remark = remark
    return otconfig


def create_target(given: Given) -> LoadOtconfig:
    return LoadOtconfig(
        given.reset_application,
        given.config_parser,
        given.update_project,
        given.add_videos,
        given.add_sections,
        given.add_flows,
        given.load_track_files,
        given.remark_repository,
        given.deserializer,
    )
