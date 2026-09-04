import asyncio
from pathlib import Path

from OTAnalytics.application.s3_config import S3Config
from OTAnalytics.plugin_s3.connect import S3Connection


class S3Upload:
    """Uploads local files to S3 storage.

    Copied from OTCloud alongside the rest of the S3 client layer — see
    `docs/adr/0001-duplicate-s3-layer.md`. Not used by the S3 time-selection
    epic; it is here for the later work that uploads analysis results back to
    the bucket.

    Args:
        connection (S3Connection): S3 connection manager for establishing
            client sessions.
        config (S3Config): Config containing S3 bucket and connection parameters.
    """

    def __init__(self, connection: S3Connection, config: S3Config) -> None:
        self._connection = connection
        self._config = config

    async def upload(
        self, src: Path, key: str, content_type: str | None = None
    ) -> None:
        """Uploads a local file to S3.

        Reads the file from the local filesystem and uploads it to the
        configured S3 bucket with the specified key. Optionally sets the
        content type for the uploaded object.

        Args:
            src (Path): The local filesystem path of the file to upload.
            key (str): The S3 object key (path) where the file will be stored.
            content_type (str | None): Optional MIME type for the uploaded
                object. If None, S3 will attempt to infer the content type.
        """
        payload = await asyncio.to_thread(src.read_bytes)
        async with self._connection.establish(self._config) as client:
            # Spelled out rather than built as **kwargs: put_object is precisely
            # typed by types-aiobotocore-s3 and rejects a dict unpacking.
            if content_type:
                await client.put_object(
                    Bucket=self._config.bucket,
                    Key=key,
                    Body=payload,
                    ContentType=content_type,
                )
            else:
                await client.put_object(
                    Bucket=self._config.bucket, Key=key, Body=payload
                )
