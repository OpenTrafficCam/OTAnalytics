from unittest.mock import Mock

from OTAnalytics.application.use_cases.clear_repositories import ClearRepositories
from OTAnalytics.application.use_cases.start_new_project import StartNewProject


class TestStartNewProject:
    def test_start_new_project(self) -> None:
        clear_repositories = Mock(spec=ClearRepositories)
        start_new_project = StartNewProject(clear_repositories)
        start_new_project()
        clear_repositories.assert_called_once()
