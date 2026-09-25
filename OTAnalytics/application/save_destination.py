from abc import ABC, abstractmethod
from pathlib import Path

from OTAnalytics.application.key_prefix import S3KeyPrefix


class UnsupportedSaveDestination(Exception):
    """Raised when an otconfig would be saved where a later s3-mode load could
    not find it again.
    """

    pass


class GuardSaveDestination(ABC):
    """Decides whether this installation may save an otconfig to a given path.

    Nothing here asks what the transfer mode is: the wiring picks an
    implementation, and the implementation is the answer. See ADR 0004 and
    OP#10323's decision log.
    """

    @abstractmethod
    def __call__(self, file: Path, key_prefix: S3KeyPrefix) -> None:
        """Raise UnsupportedSaveDestination if `file` is not a valid destination."""
        raise NotImplementedError


class NoDestinationGuard(GuardSaveDestination):
    """Wired whenever s3 is not configured; local saves are never guarded."""

    def __call__(self, file: Path, key_prefix: S3KeyPrefix) -> None:
        return None
