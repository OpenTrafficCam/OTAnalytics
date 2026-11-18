from typing import TYPE_CHECKING, AsyncContextManager

import aioboto3

from OTAnalytics.plugin_s3.config.s3 import S3Config

if TYPE_CHECKING:
    from types_aiobotocore_s3 import S3Client


class S3Store:
    """A configured bucket on AWS S3 or an S3-compatible storage service.

    Owns the connection parameters and hands out client sessions, so that
    operations on the bucket depend on this single collaborator rather than on
    credentials and bucket configuration separately.

    Args:
        config (S3Config): config containing S3 bucket and connection parameters.
    """

    def __init__(self, config: S3Config) -> None:
        self._config = config

    @property
    def bucket(self) -> str:
        """str: name of the bucket that operations on this store address."""
        return self._config.bucket

    def client(self) -> AsyncContextManager["S3Client"]:
        """Establishes an asynchronous S3 client connection.

        Creates and returns an async context manager for an S3 client session
        configured with this store's endpoint, region and credentials.

        Returns:
            AsyncContextManager[S3Client]: An async context manager that
                yields a configured S3 client for performing S3 operations.
        """
        session = aioboto3.Session()
        return session.client(
            "s3",
            endpoint_url=self._config.endpoint_url,
            region_name=self._config.region,
            aws_access_key_id=self._config.access_key,
            aws_secret_access_key=self._config.secret_key,
        )
