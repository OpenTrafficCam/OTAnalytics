from abc import ABC, abstractmethod


class WidgetPositionProvider(ABC):
    @abstractmethod
    def get_position(self, offset: tuple[float, float] = (0.5, 0.5)) -> tuple[int, int]:
        raise NotImplementedError


def remove_wildcard_from(file_extension: str) -> str:
    return file_extension[1:] if file_extension.startswith("*") else file_extension


def ensure_file_extension_is_present(file: str, defaultextension: str) -> str:
    """
    Ensure that the file contains a file extension. If no extension is appended, the
    defaultextension will be used.

    Args:
        file (str): file to ensure it has a file extension
        defaultextension (str): default extension to be added if extension is missing

    Returns:
        Path: path object with file extension
    """
    file_extension = remove_wildcard_from(defaultextension)
    if file.endswith(file_extension):
        return file
    if file_extension.startswith("."):
        return file + file_extension
    return f"{file}.{file_extension}"
