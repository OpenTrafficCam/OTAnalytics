import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterable, Iterator
from uuid import uuid4

from OTAnalytics.application.logger import logger


def get_all_files_with_correct_file_ending_in_directory(
    files: Iterable[Path], file_types: list[str]
) -> list[Path]:
    files_to_save: set[Path] = set()
    for file_type in file_types:
        for file in files:
            file_to_save = file.expanduser()
            if file_to_save.is_dir():
                # Treat file_type as a glob pattern (e.g., "*.ottrk", "*.tracks.csv")
                files_in_directory = file_to_save.rglob(file_type)
                files_to_save.update(files_in_directory)
                continue

            if not file_to_save.exists():
                logger().warning(f"File '{file_to_save}' does not exist. Skipping.")
                continue

            if not file_to_save.match(file_type):
                logger().warning(
                    f"File '{file_to_save}' does not match expected pattern '{file_type}'. Skipping."  # noqa
                )
                continue

            files_to_save.add(file_to_save)
    return list(files_to_save)


@contextmanager
def atomic_write(path: Path) -> Iterator[Path]:
    """Write a file atomically.

    Yields the path of an empty temp file in the same directory as path, to be
    written by the block. If the block succeeds, the temp file is synced to
    disk and moved over path with os.replace; otherwise it is removed and path
    stays untouched. Unlike tempfile.mkstemp, the temp file gets the default
    permissions (0o666 minus the umask), so the result is as readable as any
    other export.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
    os.close(os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o666))
    try:
        yield temp
        with open(temp, "r+b") as file:
            os.fsync(file.fileno())
        os.replace(temp, path)
    except BaseException:
        temp.unlink(missing_ok=True)
        raise
