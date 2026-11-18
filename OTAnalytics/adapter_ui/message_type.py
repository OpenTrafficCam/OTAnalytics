from enum import StrEnum


class MessageType(StrEnum):
    """Severity of a message shown to the user."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
