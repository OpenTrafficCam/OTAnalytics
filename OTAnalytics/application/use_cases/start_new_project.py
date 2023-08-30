from OTAnalytics.application.config import DEFAULT_TRACK_OFFSET
from OTAnalytics.application.state import TrackViewState
from OTAnalytics.application.use_cases.clear_repositories import ClearRepositories
from OTAnalytics.application.use_cases.reset_project_config import ResetProjectConfig


class StartNewProject:
    """Start a new OTAnalytics project.

    Args:
        clear_repositories (ClearRepositories): use case to clear all repositories
            used within OTAnalytics.
        reset_project_config (ResetProjectConfig): use case to reset project config.
        track_view_state (TrackViewState): the track view state.
    """

    def __init__(
        self,
        clear_repositories: ClearRepositories,
        reset_project_config: ResetProjectConfig,
        track_view_state: TrackViewState,
    ) -> None:
        self._clear_repositories = clear_repositories
        self._reset_project_config = reset_project_config
        self._track_view_state = track_view_state

    def __call__(self) -> None:
        """Start a new OTAnalytics project."""
        self._clear_repositories()
        self._reset_project_config()
        self._track_view_state.selected_videos.set([])
        self._track_view_state.background_image.set(None)
        self._track_view_state.track_offset.set(DEFAULT_TRACK_OFFSET)
