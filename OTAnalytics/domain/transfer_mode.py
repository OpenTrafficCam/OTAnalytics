from enum import StrEnum


class TransferMode(StrEnum):
    """How OTAnalytics obtains track and video files."""

    LOCAL_FILESYSTEM = "local-filesystem"
    S3 = "s3"
