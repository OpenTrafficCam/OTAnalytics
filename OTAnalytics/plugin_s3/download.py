import asyncio
from pathlib import Path

from OTAnalytics.application.logger import logger
from OTAnalytics.plugin_s3.config.s3 import S3Config
from OTAnalytics.plugin_s3.connect import S3Connection


class S3Download:
    """Downloads objects from S3 storage to the local filesystem.

    Copied from OTCloud — see `docs/adr/0001-duplicate-s3-layer.md`.

    Args:
        connection (S3Connection): S3 connection manager for establishing
            client sessions.
        config (S3Config): config containing S3 bucket and connection parameters.
    """

    def __init__(self, connection: S3Connection, config: S3Config) -> None:
        self._connection = connection
        self._config = config

    async def download(self, key: str, dst: Path) -> None:
        """Downloads an object from S3 to a local file.

        Retrieves the object specified by the key from the configured S3
        bucket and writes it to the destination path. Creates parent
        directories if they don't exist.

        Args:
            key (str): The S3 object key (path) to download.
            dst (Path): The local filesystem path where the downloaded file
                will be saved.
        """
        async with self._connection.establish(self._config) as client:
            logger().debug(f"Download '{key}' from S3 to '{dst}'")
            response = await client.get_object(Bucket=self._config.bucket, Key=key)
            body = response["Body"]
            # aiobotocore provides an async StreamingBody
            data = await body.read()
            dst.parent.mkdir(parents=True, exist_ok=True)
            await asyncio.to_thread(dst.write_bytes, data)
