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
