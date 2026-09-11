from dataclasses import dataclass


class InvalidS3KeyPrefix(ValueError):
    """Raised when a string cannot be a key prefix at all."""

    pass


@dataclass(frozen=True)
class S3KeyPrefix:
    """Where in the bucket a project's tracks and videos live.

    Declared by the otconfig rather than the environment (ADR 0004), so that one
    deployment can open projects stored under different prefixes of the bucket
    it is configured for.

    This type only guarantees that the string names something. Whether a prefix
    may be honoured by *this* installation is a separate question, answered on
    load by ValidateProjectLocation: local mode refuses any prefix, s3 mode
    requires one that stays inside the bucket.
    """

    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise InvalidS3KeyPrefix(
                "An s3 key prefix must name a location in the bucket, "
                "but the given prefix is empty."
            )

    def __str__(self) -> str:
        return self.value
