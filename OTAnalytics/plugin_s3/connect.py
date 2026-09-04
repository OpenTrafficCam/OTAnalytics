from typing import TYPE_CHECKING, AsyncContextManager

import aioboto3

from OTAnalytics.application.s3_config import S3Config

if TYPE_CHECKING:
    from types_aiobotocore_s3 import S3Client


class S3Connection:
    """Manages connections to AWS S3 or S3-compatible storage services.

    Provides functionality to establish asynchronous connections to S3 storage
    using aioboto3. Copied from OTCloud — see
    `docs/adr/0001-duplicate-s3-layer.md`.
    """

    def establish(self, config: S3Config) -> AsyncContextManager["S3Client"]:
        """Establishes an asynchronous S3 client connection.

        Creates and returns an async context manager for an S3 client session
        configured with the provided credentials and endpoint information.

        Args:
            config (S3Config): Configuration object containing S3 connection
                parameters including endpoint URL, region, and access
                credentials.

        Returns:
            AsyncContextManager[S3Client]: An async context manager that
                yields a configured S3 client for performing S3 operations.
        """
        session = aioboto3.Session()
        return session.client(
            "s3",
            endpoint_url=config.endpoint_url,
            region_name=config.region,
            aws_access_key_id=config.access_key,
            aws_secret_access_key=config.secret_key,
        )
