"""Clearing the local user source that downloaded objects are staged in."""

import shutil
from pathlib import Path

from OTAnalytics.application.logger import logger
from OTAnalytics.application.use_cases.clear_repositories import ClearRepositories
from OTAnalytics.application.use_cases.reset_application import ResetApplication
from OTAnalytics.application.use_cases.reset_state import ResetState


class WipeUserSource:
    """Empties the user source, leaving the directory itself in place.

    Staged downloads are not a cache: nothing reuses them across runs, and the
    `Video` objects that point at them do not survive a restart either. Wiping
    on startup is the reliable guarantee, because it also reclaims what a
    `SIGKILL`, an OOM kill or a crash left behind.

    Args:
        user_source (Path): the directory downloads are staged in.
    """

    def __init__(self, user_source: Path) -> None:
        self._user_source = user_source

    def wipe(self) -> None:
        """Remove everything staged, then make sure the directory exists."""
        if self._user_source.exists():
            logger().info(f"Wiping user source '{self._user_source}'")
            shutil.rmtree(self._user_source, ignore_errors=True)
        self._user_source.mkdir(parents=True, exist_ok=True)


class WipeUserSourceOnReset(ResetApplication):
    """Resets a project and then frees the downloads it was using.

    The wipe happens after the repositories are cleared, so no `Video` still
    points at a file that is about to be removed.

    Args:
        clear_repositories (ClearRepositories): empties the repositories.
        reset_state (ResetState): resets the application state.
        wipe (WipeUserSource): empties the user source.
    """

    def __init__(
        self,
        clear_repositories: ClearRepositories,
        reset_state: ResetState,
        wipe: WipeUserSource,
    ) -> None:
        super().__init__(clear_repositories, reset_state)
        self._wipe = wipe

    def reset(self) -> None:
        super().reset()
        self._wipe.wipe()
