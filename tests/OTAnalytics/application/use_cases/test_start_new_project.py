from unittest.mock import Mock

from OTAnalytics.application.config import DEFAULT_TRACK_OFFSET
from OTAnalytics.application.state import (
    ObservableOptionalProperty,
    ObservableProperty,
    TrackViewState,
)
from OTAnalytics.application.use_cases.clear_repositories import ClearRepositories
from OTAnalytics.application.use_cases.reset_project_config import ResetProjectConfig
from OTAnalytics.application.use_cases.start_new_project import StartNewProject


class TestStartNewProject:
    def test_start_new_project(self) -> None:
        clear_repositories = Mock(spec=ClearRepositories)
        reset_project_config = Mock(spec=ResetProjectConfig)

        observable_background_image = Mock(spec=ObservableOptionalProperty)
        observable_track_offset = Mock(spec=ObservableOptionalProperty)
        observable_selected_videos = Mock(spec=ObservableProperty)
        track_view_state = Mock(spec=TrackViewState)
        track_view_state.background_image = observable_background_image
        track_view_state.track_offset = observable_track_offset
        track_view_state.selected_videos = observable_selected_videos

        start_new_project = StartNewProject(
            clear_repositories, reset_project_config, track_view_state
        )
        start_new_project()
        clear_repositories.assert_called_once()
        reset_project_config.assert_called_once()
        observable_background_image.set.assert_called_once_with(None)
        observable_track_offset.set.assert_called_once_with(DEFAULT_TRACK_OFFSET)
        observable_selected_videos.set.assert_called_once_with([])
