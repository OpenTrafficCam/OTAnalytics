from OTAnalytics.application.use_cases.update_project import ProjectUpdater


class ResetProjectConfig:
    """Reset the project configuration.

    Args:
        update_project (ProjectUpdater): the use case to update the project.
    """

    def __init__(self, update_project: ProjectUpdater):
        self._update_project = update_project

    def __call__(self) -> None:
        """Reset the project configuration."""
        self._update_project("", None, None)
