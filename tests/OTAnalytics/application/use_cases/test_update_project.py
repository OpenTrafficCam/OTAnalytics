from datetime import datetime
from unittest.mock import Mock

import pytest

from OTAnalytics.application.datastore import Datastore
from OTAnalytics.application.project import Project
from OTAnalytics.application.use_cases.update_project import ProjectUpdater


@pytest.fixture
def my_project() -> Project:
    return Project("My Project", datetime(2022, 1, 1, 13))


@pytest.fixture
def datastore(my_project: Project) -> Mock:
    datastore = Mock(spec=Datastore)
    datastore.project = my_project
    return datastore


class TestUpdateProject:
    def test_update(self, datastore: Mock, my_project: Project) -> None:
        new_project_name = "My New Project"
        new_project_start_date = datetime(2000, 2, 2, 13)
        project_updater = ProjectUpdater(datastore)
        observer = Mock()
        project_updater.register(observer)

        project_updater(new_project_name, new_project_start_date)
        expected_project = Project(new_project_name, new_project_start_date)

        assert datastore.project == expected_project
        observer.assert_called_once_with(expected_project)

    def test_update_name(self, datastore: Mock, my_project: Project) -> None:
        new_project_name = "My New Project"
        project_updater = ProjectUpdater(datastore)
        observer = Mock()
        project_updater.register(observer)

        project_updater.update_name(new_project_name)
        expected_project = Project(new_project_name, my_project.start_date)

        assert datastore.project == expected_project
        observer.assert_called_once_with(expected_project)

    def test_update_start_date(self, datastore: Mock, my_project: Project) -> None:
        new_project_start_date = datetime(2000, 2, 2, 13)
        project_updater = ProjectUpdater(datastore)
        observer = Mock()
        project_updater.register(observer)

        project_updater.update_start_date(new_project_start_date)
        expected_project = Project(my_project.name, new_project_start_date)

        assert datastore.project == expected_project
        observer.assert_called_once_with(expected_project)
