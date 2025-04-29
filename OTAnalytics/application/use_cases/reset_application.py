from OTAnalytics.application.use_cases.clear_repositories import ClearRepositories
from OTAnalytics.application.use_cases.reset_state import ResetState


class ResetApplication:
    def __init__(
        self, clear_repositories: ClearRepositories, reset_state: ResetState
    ) -> None:
        self._clear_repositories = clear_repositories
        self._reset_state = reset_state

    def reset(self) -> None:
        self._clear_repositories()
        self._reset_state.reset()
