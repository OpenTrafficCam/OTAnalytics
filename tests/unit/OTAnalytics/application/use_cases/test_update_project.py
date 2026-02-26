from datetime import datetime
from unittest.mock import Mock

import pytest

from OTAnalytics.application.datastore import Datastore
from OTAnalytics.application.project import (
    CountingDayType,
    DirectionOfStationing,
    Project,
    SvzMetadata,
    WeatherType,
)
from OTAnalytics.application.use_cases.update_project import ProjectUpdater


@pytest.fixture
def svz_metadata() -> SvzMetadata:
    tk_number = "1"
    counting_location_number = "2"
    direction = "1"
    direction_description = "direction_description"
    has_bicycle_lane = False
    is_bicycle_counting = False
    counting_day = "2"
    weather = "2"
    remark = "something"
    coordinate_x = "1.2"
    coordinate_y = "3.4"
    return SvzMetadata(
        tk_number=tk_number,
        counting_location_number=counting_location_number,
        direction=DirectionOfStationing.parse(direction),
        direction_description=direction_description,
        has_bicycle_lane=has_bicycle_lane,
        is_bicycle_counting=is_bicycle_counting,
        counting_day=CountingDayType.parse(counting_day),
        weather=WeatherType.parse(weather),
        remark=remark,
        coordinate_x=coordinate_x,
        coordinate_y=coordinate_y,
    )


@pytest.fixture
def my_project(svz_metadata: SvzMetadata) -> Project:
    return Project("My Project", datetime(2022, 1, 1, 13), svz_metadata)


@pytest.fixture
def datastore(my_project: Project) -> Mock:
    datastore = Mock(spec=Datastore)
    datastore.project = my_project
    return datastore


class TestUpdateProject:
    def test_update(
        self, datastore: Mock, my_project: Project, svz_metadata: SvzMetadata
    ) -> None:
        new_project_name = "My New Project"
        new_project_start_date = datetime(2000, 2, 2, 13)
        project_updater = ProjectUpdater(datastore)
        observer = Mock()
        project_updater.register(observer)

        project_updater(new_project_name, new_project_start_date, svz_metadata)
        expected_project = Project(
            new_project_name, new_project_start_date, svz_metadata
        )

        assert datastore.project == expected_project
        observer.assert_called_once_with(expected_project)

    def test_update_name(self, datastore: Mock, my_project: Project) -> None:
        new_project_name = "My New Project"
        project_updater = ProjectUpdater(datastore)
        observer = Mock()
        project_updater.register(observer)

        project_updater.update_name(new_project_name)
        expected_project = Project(
            new_project_name, my_project.start_date, my_project.metadata
        )

        assert datastore.project == expected_project
        observer.assert_called_once_with(expected_project)

    def test_update_start_date(self, datastore: Mock, my_project: Project) -> None:
        new_project_start_date = datetime(2000, 2, 2, 13)
        project_updater = ProjectUpdater(datastore)
        observer = Mock()
        project_updater.register(observer)

        project_updater.update_start_date(new_project_start_date)
        expected_project = Project(
            my_project.name, new_project_start_date, my_project.metadata
        )

        assert datastore.project == expected_project
        observer.assert_called_once_with(expected_project)

    def test_update_svz_metadata(
        self, datastore: Mock, my_project: Project, svz_metadata: SvzMetadata
    ) -> None:
        new_metadata = SvzMetadata(
            tk_number=svz_metadata.tk_number,
            counting_location_number=svz_metadata.counting_location_number,
            direction=svz_metadata.direction,
            direction_description=svz_metadata.direction_description,
            has_bicycle_lane=svz_metadata.has_bicycle_lane,
            is_bicycle_counting=svz_metadata.is_bicycle_counting,
            counting_day=svz_metadata.counting_day,
            weather=svz_metadata.weather,
            remark="new metadata",
            coordinate_x=svz_metadata.coordinate_x,
            coordinate_y=svz_metadata.coordinate_y,
        )
        project_updater = ProjectUpdater(datastore)
        observer = Mock()
        project_updater.register(observer)
        project_updater.update_svz_metadata(new_metadata)
        expected_project = Project(my_project.name, my_project.start_date, new_metadata)

        assert datastore.project == expected_project
        observer.assert_called_once_with(expected_project)
