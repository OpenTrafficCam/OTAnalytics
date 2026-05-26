from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable


class WidgetPositionProvider(ABC):
    @abstractmethod
    def get_position(self, offset: tuple[float, float] = (0.5, 0.5)) -> tuple[int, int]:
        raise NotImplementedError


def remove_wildcard_from(file_extension: str) -> str:
    return file_extension[1:] if file_extension.startswith("*") else file_extension


def ensure_file_extension_is_present(
    file: str, allowed_extensions: list[str], defaultextension: str
) -> str:
    """
    Ensure that the file contains a file extension. If no extension is appended, the
    defaultextension will be used.

    Args:
        file (str): file to ensure it has a file extension
        allowed_extensions (list[str]): extensions that are allowed
        defaultextension (str): default extension to be added if extension is missing

    Returns:
        Path: path object with file extension
    """
    if not file:
        return ""
    file_extension = remove_wildcard_from(defaultextension)
    allowed_file_extensions = set(
        [remove_wildcard_from(ext) for ext in allowed_extensions]
    )
    allowed_file_extensions.add(file_extension)
    for allowed_extension in allowed_file_extensions:
        if file.endswith(allowed_extension):
            return file
    if file_extension.startswith("."):
        return file + file_extension
    return f"{file}.{file_extension}"


def strip_extension(file_name: str, extension: str) -> str:
    """Strip supported file extension from file name if present.

    Args:
        file_name (str): the file name.
        extension (str): the supported file types.

    Returns:
        str: file name without supported extension if present, otherwise original file name
    """
    if file_name.endswith(extension):
        # Strip the supported file type from the file name
        return file_name.rstrip(extension)

    # file_name does not have supported file type appended yet
    return file_name


def ensure_dot_in_extension(extension: str) -> str:
    """Ensure that the file name has a dot in the extension."""
    if not extension.startswith("."):
        return f".{extension}"
    return extension
