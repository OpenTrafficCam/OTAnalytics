from unittest.mock import Mock, patch

from OTAnalytics.application.state import FileState, TrackViewState
from OTAnalytics.application.use_cases.clear_repositories import ClearRepositories
from OTAnalytics.application.use_cases.reset_project_config import ResetProjectConfig
from OTAnalytics.application.use_cases.start_new_project import StartNewProject


class TestStartNewProject:
    @patch("OTAnalytics.application.use_cases.start_new_project.Subject.notify")
    def test_start_new_project(self, mock_notify: Mock) -> None:
        clear_repositories = Mock(spec=ClearRepositories)
        reset_project_config = Mock(spec=ResetProjectConfig)

        track_view_state = Mock(spec=TrackViewState)
        file_state = Mock(spec=FileState)
        start_new_project = StartNewProject(
            clear_repositories, reset_project_config, track_view_state, file_state
        )
        start_new_project()
        clear_repositories.assert_called_once()
        reset_project_config.assert_called_once()
        track_view_state.reset.assert_called_once()
        file_state.reset.assert_called_once()
        mock_notify.assert_called_once()
