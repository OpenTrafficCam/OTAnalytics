from OTAnalytics.application.state import FileState, TrackViewState
from OTAnalytics.application.use_cases.clear_repositories import ClearRepositories
from OTAnalytics.application.use_cases.reset_project_config import ResetProjectConfig
from OTAnalytics.domain.observer import OBSERVER, Subject


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
        file_state: FileState,
    ) -> None:
        self._clear_repositories = clear_repositories
        self._reset_project_config = reset_project_config
        self._track_view_state = track_view_state
        self._file_state = file_state
        self._subject: Subject[None] = Subject[None]()

    def __call__(self) -> None:
        """Start a new OTAnalytics project."""
        self._clear_repositories()
        self._reset_project_config()
        self._track_view_state.reset()
        self._file_state.reset()
        self._subject.notify(None)

    def register(self, observer: OBSERVER[None]) -> None:
        self._subject.register(observer)
