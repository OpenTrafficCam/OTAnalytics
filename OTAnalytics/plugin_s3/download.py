import asyncio
from pathlib import Path

from OTAnalytics.application.logger import logger
from OTAnalytics.plugin_s3.store import S3Store


class S3Download:
    """Downloads objects from S3 storage to the local filesystem.

    Args:
        store (S3Store): the S3 bucket to download from.
    """

    def __init__(self, store: S3Store) -> None:
        self._store = store

    async def download(self, key: str, dst: Path) -> None:
        """Downloads an object from S3 to a local file.

        Retrieves the object specified by the key from the store's bucket and
        writes it to the destination path. Creates parent directories if they
        don't exist.

        Args:
            key (str): The S3 object key (path) to download.
            dst (Path): The local filesystem path where the downloaded file
                will be saved.
        """
        async with self._store.client() as client:
            logger().debug(f"Download '{key}' from S3 to '{dst}'")
            response = await client.get_object(Bucket=self._store.bucket, Key=key)
            body = response["Body"]
            # aiobotocore provides an async StreamingBody
            data = await body.read()
            dst.parent.mkdir(parents=True, exist_ok=True)
            await asyncio.to_thread(dst.write_bytes, data)
