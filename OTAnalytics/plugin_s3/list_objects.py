"""S3 object listing with pagination support."""

from OTAnalytics.plugin_s3.store import S3Store


class S3ListObjects:
    """Lists object keys from S3 storage under a given prefix.

    Handles pagination transparently via list_objects_v2 continuation tokens.

    Args:
        store (S3Store): the S3 bucket to list objects from.
    """

    def __init__(self, store: S3Store) -> None:
        self._store = store

    async def list_keys(self, prefix: str) -> list[str]:
        """List all object keys under the given S3 prefix.

        A key is reported once, in the order it was first seen. AWS S3 never
        repeats a key, but S3-compatible services do, and a repeated key would
        otherwise be downloaded and loaded twice.

        Args:
            prefix (str): The S3 key prefix to list objects under.

        Returns:
            list[str]: All object keys matching the prefix, without duplicates.
        """
        keys: list[str] = []
        seen: set[str] = set()
        async with self._store.client() as client:
            kwargs: dict = {"Bucket": self._store.bucket, "Prefix": prefix}
            while True:
                response = await client.list_objects_v2(**kwargs)
                for content in response.get("Contents", []):
                    key = content["Key"]
                    if key not in seen:
                        seen.add(key)
                        keys.append(key)
                if not response.get("IsTruncated", False):
                    break
                kwargs["ContinuationToken"] = response["NextContinuationToken"]
        return keys
