from enum import StrEnum


class TransferMode(StrEnum):
    """How OTAnalytics obtains track and video files.

    Values match OTCloud's `TransferMode` where they overlap. OTCloud also
    defines `FTP`, which OTAnalytics does not support; leaving it out means an
    unsupported mode is rejected by the enum itself rather than needing a
    separate check.
    """

    LOCAL_FILESYSTEM = "local-filesystem"
    S3 = "s3"
