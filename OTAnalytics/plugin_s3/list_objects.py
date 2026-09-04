"""S3 object listing with pagination support."""

from OTAnalytics.plugin_s3.config.s3 import S3Config
from OTAnalytics.plugin_s3.connect import S3Connection


class S3ListObjects:
    """Lists object keys from S3 storage under a given prefix.

    Handles pagination transparently via list_objects_v2 continuation tokens.
    Copied from OTCloud — see `docs/adr/0001-duplicate-s3-layer.md`.

    Args:
        connection (S3Connection): S3 connection manager for establishing
            client sessions.
        config (S3Config): Config containing S3 bucket and connection parameters.
    """

    def __init__(self, connection: S3Connection, config: S3Config) -> None:
        self._connection = connection
        self._config = config

    async def list_keys(self, prefix: str) -> list[str]:
        """List all object keys under the given S3 prefix.

        Args:
            prefix (str): The S3 key prefix to list objects under.

        Returns:
            list[str]: All object keys matching the prefix.
        """
        keys: list[str] = []
        async with self._connection.establish(self._config) as client:
            kwargs: dict = {"Bucket": self._config.bucket, "Prefix": prefix}
            while True:
                response = await client.list_objects_v2(**kwargs)
                for content in response.get("Contents", []):
                    keys.append(content["Key"])
                if not response.get("IsTruncated", False):
                    break
                kwargs["ContinuationToken"] = response["NextContinuationToken"]
        return keys
