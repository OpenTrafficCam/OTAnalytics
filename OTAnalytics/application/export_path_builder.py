"""Centralized export file path construction.

This module provides the canonical helper for composing export file paths in
OTAnalytics. It exists to prevent recurrence of the multi-dot truncation bug
(OP#9548): ``Path.with_suffix()`` replaces the substring after the last dot, so
applying it to a stem like ``video.00000_2025-08-28_15-00-00`` silently loses
the trailing ``00000_2025-08-28_15-00-00`` portion. Concatenating ``stem`` and
``suffix`` and joining with the parent directory preserves the full stem
regardless of how many dots it contains.
"""

from pathlib import Path

SAVE_SUFFIX_SEPARATOR = "_"


def build_export_path(
    export_directory: Path,
    export_filename_stem: str,
    file_suffix: str,
) -> Path:
    """Build an export file path from directory, stem, and suffix.

    DO NOT use ``Path.with_suffix()`` to attach an extension to an export
    stem. ``with_suffix()`` replaces the substring after the last dot, so a
    stem like ``video.00000_2025-08-28_15-00-00`` becomes ``video`` plus the
    new suffix - silently losing the timestamp portion.

    Args:
        export_directory: Parent directory where the file will be written.
        export_filename_stem: Filename without any extension, possibly
            containing multiple dots (e.g., a timestamped video name). Must
            be non-empty.
        file_suffix: Format suffix to append, including the leading dot
            (e.g., ``".csv"``, ``".tracks_metadata.json"``).

    Returns:
        ``export_directory / (export_filename_stem + file_suffix)``.

    Raises:
        ValueError: If ``export_filename_stem`` is empty or ``file_suffix``
            does not start with a dot.

    Example:
        >>> build_export_path(
        ...     Path("/output"),
        ...     "video.00000_2025-08-28_15-00-00",
        ...     ".tracks.csv",
        ... )
        PosixPath('/output/video.00000_2025-08-28_15-00-00.tracks.csv')
    """
    if not export_filename_stem:
        raise ValueError("export_filename_stem must not be empty")
    if not file_suffix.startswith("."):
        raise ValueError(f"file_suffix must start with '.', got {file_suffix!r}")
    return export_directory / (export_filename_stem + file_suffix)


def compose_export_filename_stem(
    save_name: str, save_suffix: str, fallback_stem: str
) -> str:
    """Compose the export file stem from the configured save name and suffix.

    Args:
        save_name: Configured save name. Any extension is dropped. If empty,
            ``fallback_stem`` is used instead.
        save_suffix: Configured save suffix without separator. If not empty, it
            is appended after ``SAVE_SUFFIX_SEPARATOR``.
        fallback_stem: Stem to use if no save name is configured.

    Returns:
        The composed export file stem.
    """
    stem = Path(save_name).stem if save_name else fallback_stem
    return f"{stem}{format_save_suffix(save_suffix)}"


def format_save_suffix(save_suffix: str) -> str:
    """Prepend ``SAVE_SUFFIX_SEPARATOR`` to the configured save suffix.

    Args:
        save_suffix: Configured save suffix without separator.

    Returns:
        The save suffix with the separator prepended, or an empty string if no
        save suffix is configured.
    """
    if save_suffix:
        return f"{SAVE_SUFFIX_SEPARATOR}{save_suffix}"
    return ""
