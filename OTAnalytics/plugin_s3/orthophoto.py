"""Downloading the Orthophoto an S3 project declares."""

from pathlib import Path, PurePosixPath

from OTAnalytics.application.logger import logger
from OTAnalytics.application.orthophoto import ObtainOrthophoto
from OTAnalytics.application.state import CurrentKeyPrefix
from OTAnalytics.domain.orthophoto import OrthophotoNotFound
from OTAnalytics.plugin_s3.download_objects import DownloadObjects

DOWNLOADING_ORTHOPHOTO = "Downloading orthophoto"
PARENT_DIRECTORY = ".."
NOTHING_LOADED = "Nothing was loaded."


class S3ObtainOrthophoto(ObtainOrthophoto):
    """Fetches the declared Orthophoto from under the project's Key Prefix.

    A project reads only within its own Key Prefix (ADR 0004), so a reference
    that climbs out of it or is absolute is refused before anything is fetched.

    Args:
        download_objects (DownloadObjects): downloads into the user source.
        current_key_prefix (CurrentKeyPrefix): where the project's data lives.
    """

    def __init__(
        self, download_objects: DownloadObjects, current_key_prefix: CurrentKeyPrefix
    ) -> None:
        self._download_objects = download_objects
        self._current_key_prefix = current_key_prefix

    async def obtain(self, reference: Path, base_folder: Path) -> Path:
        key = self._key_of(PurePosixPath(reference.as_posix()))
        try:
            [local_file] = await self._download_objects.download_all(
                [key], DOWNLOADING_ORTHOPHOTO
            )
        except Exception as cause:
            logger().exception(cause, exc_info=True)
            raise OrthophotoNotFound(
                f"The project's orthophoto '{key}' could not be downloaded:"
                f" {cause}. {NOTHING_LOADED}"
            ) from cause
        return local_file

    def _key_of(self, reference: PurePosixPath) -> str:
        key_prefix = self._current_key_prefix.get()
        if (
            key_prefix is None
            or reference.is_absolute()
            or PARENT_DIRECTORY in reference.parts
        ):
            raise OrthophotoNotFound(
                f"The project's orthophoto '{reference}' must lie under the"
                f" project's location. {NOTHING_LOADED}"
            )
        return f"{key_prefix.value}/{reference}"
