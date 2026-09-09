from dataclasses import dataclass
from datetime import timedelta

DEFAULT_MAX_LOAD_DURATION = timedelta(hours=10)
DEFAULT_DOWNLOAD_CONCURRENCY = 8


@dataclass(frozen=True)
class S3Config:
    """Configuration for S3-compatible object storage.

    Attributes:
        endpoint_url (str): S3 endpoint URL.
        access_key (str): S3 access key for authentication.
        secret_key (str): S3 secret key for authentication.
        bucket (str): S3 bucket name.
        region (str | None): AWS region (None if not applicable).
        key_prefix (str): prefix under which this instance's tracks and videos
            live. Fixed at startup; the user selects a time range, not a prefix.
        user_source (str): base path on the local filesystem that downloaded
            objects are written to, mirroring their S3 keys. Named after
            OTCloud's `S3_USER_SOURCE` for cross-repo consistency.
        max_load_duration (timedelta): longest time range that may be loaded in
            one go. A longer selection is clamped to it.
        download_concurrency (int): how many objects to download at once.
    """

    endpoint_url: str
    access_key: str
    secret_key: str
    bucket: str
    region: str | None
    key_prefix: str
    user_source: str
    max_load_duration: timedelta = DEFAULT_MAX_LOAD_DURATION
    download_concurrency: int = DEFAULT_DOWNLOAD_CONCURRENCY
