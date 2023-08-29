from OTAnalytics.application.use_cases.clear_repositories import ClearRepositories
from OTAnalytics.application.use_cases.reset_project_config import ResetProjectConfig


class StartNewProject:
    """Start a new OTAnalytics project.

    Args:
        clear_repositories (ClearRepositories): use case to clear all repositories
            used within OTAnalytics.
        reset_project_config (ResetProjectConfig): use case to reset project config.
    """

    def __init__(
        self,
        clear_repositories: ClearRepositories,
        reset_project_config: ResetProjectConfig,
    ) -> None:
        self._clear_repositories = clear_repositories
        self._reset_project_config = reset_project_config

    def __call__(self) -> None:
        """Start a new OTAnalytics project."""
        self._clear_repositories()
        self._reset_project_config()
