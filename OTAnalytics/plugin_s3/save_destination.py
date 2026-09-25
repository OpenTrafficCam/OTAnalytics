from pathlib import Path

from OTAnalytics.application.key_prefix import S3KeyPrefix
from OTAnalytics.application.save_destination import (
    GuardSaveDestination,
    UnsupportedSaveDestination,
)


class RequireDestinationUnderUserSource(GuardSaveDestination):
    """Refuses a destination a later s3-mode load could not resolve back to.

    `user_source` is shared across projects in one process (see the epic's
    follow-up 8), so containment under the prefix, not just under
    `user_source`, is what keeps a save from landing under a sibling project.
    """

    def __init__(self, user_source: Path) -> None:
        self._user_source = user_source

    def __call__(self, file: Path, key_prefix: S3KeyPrefix) -> None:
        root = (self._user_source / key_prefix.value).resolve()
        if not file.resolve().is_relative_to(root):
            raise UnsupportedSaveDestination(
                f"Refusing to save '{file}': it does not lie under '{root}', "
                "so a later load in s3 mode could not find it again."
            )
