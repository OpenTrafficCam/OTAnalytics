import asyncio
from pathlib import Path

from OTAnalytics.plugin_s3.store import S3Store


class S3Upload:
    """Uploads local files to S3 storage.

    Args:
        store (S3Store): the S3 bucket to upload to.
    """

    def __init__(self, store: S3Store) -> None:
        self._store = store

    async def upload(
        self, src: Path, key: str, content_type: str | None = None
    ) -> None:
        """Uploads a local file to S3.

        Reads the file from the local filesystem and uploads it to the
        store's bucket with the specified key. Optionally sets the
        content type for the uploaded object.

        Args:
            src (Path): The local filesystem path of the file to upload.
            key (str): The S3 object key (path) where the file will be stored.
            content_type (str | None): Optional MIME type for the uploaded
                object. If None, S3 will attempt to infer the content type.
        """
        payload = await asyncio.to_thread(src.read_bytes)
        async with self._store.client() as client:
            # Spelled out rather than built as **kwargs: put_object is precisely
            # typed by types-aiobotocore-s3 and rejects a dict unpacking.
            if content_type:
                await client.put_object(
                    Bucket=self._store.bucket,
                    Key=key,
                    Body=payload,
                    ContentType=content_type,
                )
            else:
                await client.put_object(
                    Bucket=self._store.bucket, Key=key, Body=payload
                )
