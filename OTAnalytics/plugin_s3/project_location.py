from pathlib import PurePosixPath

from OTAnalytics.application.key_prefix import S3KeyPrefix
from OTAnalytics.application.project_location import (
    UnsupportedProjectLocation,
    ValidateProjectLocation,
)

PARENT = ".."


class RequireWellFormedKeyPrefix(ValidateProjectLocation):
    """Requires a project to say where in the bucket its data lives.

    Wired when s3 is configured. The bucket comes from the environment and is
    never read from the file, so a prefix can only move the read within the one
    bucket this deployment may authenticate to. An absolute or `..`-bearing
    prefix is refused anyway: it reads as an attempt to leave that bucket, and
    an S3 key that means it literally would not resolve to the object intended.
    """

    def __call__(self, key_prefix: S3KeyPrefix | None) -> None:
        if key_prefix is None:
            raise UnsupportedProjectLocation(
                "This project does not say where its data lives, and this "
                "installation reads from S3. Only a project saved in s3 mode "
                "can be opened here."
            )
        if not self._stays_within_the_bucket(key_prefix):
            raise UnsupportedProjectLocation(
                f"This project names '{key_prefix}' as the location of its data, "
                "which does not describe a location inside the configured bucket."
            )

    def _stays_within_the_bucket(self, key_prefix: S3KeyPrefix) -> bool:
        path = PurePosixPath(key_prefix.value)
        return not path.is_absolute() and PARENT not in path.parts
