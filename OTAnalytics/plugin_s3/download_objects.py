"""Downloading the selected S3 objects into the local user source."""

import asyncio
from pathlib import Path

from OTAnalytics.domain.progress import CompletionProgressBuilder
from OTAnalytics.plugin_s3.download import S3Download


class DownloadCancelled(Exception):
    """Raised when the user abandoned a download."""


class DownloadObjects:
    """Downloads object keys concurrently, mirroring them under the user source.

    A load is all or nothing: a cancel or any failure raises, so nothing is
    handed on to be parsed and no repository is touched. Downloaded bytes stay
    on disk until the next wipe.

    Args:
        download (S3Download): downloads a single object.
        user_source (Path): local base path that keys are mirrored under.
        concurrency (int): how many objects to download at once.
        progressbar_builder (CompletionProgressBuilder): shows how far the
            download has got.
    """

    def __init__(
        self,
        download: S3Download,
        user_source: Path,
        concurrency: int,
        progressbar_builder: CompletionProgressBuilder,
    ) -> None:
        self._download = download
        self._user_source = user_source
        self._concurrency = concurrency
        self._progressbar_builder = progressbar_builder

    async def download_all(self, keys: list[str], description: str) -> list[Path]:
        """Download every key, at most `concurrency` at a time.

        Args:
            keys (list[str]): the object keys to download.
            description (str): what to tell the user is happening.

        Returns:
            list[Path]: the local paths, in the order the keys were given.

        Raises:
            DownloadCancelled: if the user asked to stop.
        """
        if not keys:
            return []
        progress = self._progressbar_builder.build(
            description=description, unit="files", total=len(keys)
        )
        limit = asyncio.Semaphore(self._concurrency)

        async def download_one(key: str) -> Path:
            async with limit:
                if progress.is_cancelled:
                    raise DownloadCancelled(description)
                destination = self._destination_of(key)
                await self._download.download(key, destination)
                progress.complete(Path(key).name)
                return destination

        try:
            return list(await asyncio.gather(*(download_one(key) for key in keys)))
        finally:
            progress.close()

    def _destination_of(self, key: str) -> Path:
        """The local path an object key is mirrored to.

        Args:
            key (str): the S3 object key.

        Returns:
            Path: the local path under the user source.
        """
        return self._user_source / key
