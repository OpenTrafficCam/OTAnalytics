from OTAnalytics.application.use_cases.clear_repositories import ClearRepositories
from OTAnalytics.application.use_cases.reset_state import ResetState
from OTAnalytics.domain.observer import OBSERVER, Subject


class ResetApplication:
    """Reset the application to the state of a freshly started one.

    The single source of truth for resetting: starting a new project and loading
    an otconfig both reset through this use case. State that lives outside the
    application layer, such as the visualization layers or the views, is reset by
    observers registered here.

    Args:
        clear_repositories (ClearRepositories): empties the repositories.
        reset_state (ResetState): resets the application state.
    """

    def __init__(
        self, clear_repositories: ClearRepositories, reset_state: ResetState
    ) -> None:
        self._clear_repositories = clear_repositories
        self._reset_state = reset_state
        self._subject: Subject[None] = Subject[None]()

    def reset(self) -> None:
        """Reset the application, then notify the observers."""
        self._reset()
        self._subject.notify(None)

    def _reset(self) -> None:
        self._clear_repositories()
        self._reset_state.reset()

    def register(self, observer: OBSERVER[None]) -> None:
        """Notify `observer` after every reset.

        Args:
            observer (OBSERVER[None]): called after the application was reset.
        """
        self._subject.register(observer)
