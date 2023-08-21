from abc import ABC, abstractmethod


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
