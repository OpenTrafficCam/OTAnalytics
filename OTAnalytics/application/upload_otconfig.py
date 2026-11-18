from abc import ABC, abstractmethod
from pathlib import Path

from OTAnalytics.application.key_prefix import S3KeyPrefix


class UploadOtconfig(ABC):
    """Puts a saved otconfig where a later s3-mode load can find it again.

    Nothing here asks what the transfer mode is: the wiring picks an
    implementation, and the implementation is the answer. See ADR 0004 and
    OP#10323's decision log.
    """

    @abstractmethod
    async def upload(self, file: Path, key_prefix: S3KeyPrefix) -> None:
        raise NotImplementedError


class NoOtconfigUpload(UploadOtconfig):
    """Wired whenever s3 is not configured; saving stays purely local."""

    async def upload(self, file: Path, key_prefix: S3KeyPrefix) -> None:
        return None
