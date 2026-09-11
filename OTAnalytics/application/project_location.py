from abc import ABC, abstractmethod

from OTAnalytics.application.key_prefix import S3KeyPrefix


class UnsupportedProjectLocation(Exception):
    """Raised when a project's data lives somewhere this installation cannot read.

    Carries a message meant for whoever operates the installation, since the
    remedy is a deployment decision rather than something a user can fix in the
    file.
    """

    pass


class ValidateProjectLocation(ABC):
    """Decides whether this installation can read where a project's data lives.

    The answer depends on how the process obtains files, but nothing here asks
    what the transfer mode is: the wiring picks an implementation, and the
    implementation is the answer. See ADR 0004.
    """

    @abstractmethod
    def __call__(self, key_prefix: S3KeyPrefix | None) -> None:
        """Raise UnsupportedProjectLocation if this project cannot be read here."""
        raise NotImplementedError


class RefuseAnyProjectLocation(ValidateProjectLocation):
    """Accepts only a project that names no location at all.

    Wired whenever s3 is not configured. A prefix-less otconfig is every file
    written before ADR 0004, so this leaves local mode behaving as it did.
    """

    def __call__(self, key_prefix: S3KeyPrefix | None) -> None:
        if key_prefix is not None:
            raise UnsupportedProjectLocation(
                f"This project's tracks and videos are stored in S3, under "
                f"'{key_prefix}', but this installation reads the local "
                "filesystem. Start it in s3 mode to open this project."
            )
