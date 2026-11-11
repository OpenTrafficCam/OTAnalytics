def strip_extension(file_name: str, extension: str) -> str:
    """Strip the supported file extension from the file name if present.

    Args:
        file_name: The file name.
        extension: The extension to strip (literal, including leading dot).

    Returns:
        The file name without the extension if it ends with that suffix,
        otherwise the original file name unchanged.
    """
    return file_name.removesuffix(extension)


def ensure_dot_in_extension(extension: str) -> str:
    """Ensure that the file name has a dot in the extension."""
    if not extension.startswith("."):
        return f".{extension}"
    return extension
