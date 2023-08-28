from OTAnalytics.application.use_cases.clear_repositories import ClearRepositories


class StartNewProject:
    """Start a new OTAnalytics project.

    Args:
        clear_repositories: the use case to clear all repositories used within
            OTAnalytics.
    """

    def __init__(self, clear_repositories: ClearRepositories) -> None:
        self._clear_repositories = clear_repositories

    def __call__(self) -> None:
        """Start a new OTAnalytics project."""
        self._clear_repositories()
