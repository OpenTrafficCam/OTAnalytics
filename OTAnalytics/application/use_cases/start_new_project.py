from OTAnalytics.application.use_cases.reset_application import ResetApplication
from OTAnalytics.application.use_cases.reset_project_config import ResetProjectConfig
from OTAnalytics.domain.observer import OBSERVER, Subject


class StartNewProject:
    """Start a new OTAnalytics project.

    Resets the application the same way as loading an otconfig file does, so that
    no repository content or state of the previous project is kept.

    Args:
        reset_application (ResetApplication): use case to clear all repositories
            and reset the application state.
        reset_project_config (ResetProjectConfig): use case to reset project config.
    """

    def __init__(
        self,
        reset_application: ResetApplication,
        reset_project_config: ResetProjectConfig,
    ) -> None:
        self._reset_application = reset_application
        self._reset_project_config = reset_project_config
        self._subject: Subject[None] = Subject[None]()

    def __call__(self) -> None:
        """Start a new OTAnalytics project."""
        self._reset_application.reset()
        self._reset_project_config()
        self._subject.notify(None)

    def register(self, observer: OBSERVER[None]) -> None:
        self._subject.register(observer)
