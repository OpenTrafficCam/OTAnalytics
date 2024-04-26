from os import path
from os.path import normcase, splitdrive
from pathlib import Path
from typing import Callable


class DifferentDrivesException(Exception):
    pass


def build_relative_path(
    actual: Path, relative_to: Path, exception_msg_provider: Callable[[str, str], str]
) -> str:
    self_drive, _ = splitdrive(actual)
    other_drive, _ = splitdrive(relative_to)
    if normcase(self_drive) != normcase(other_drive):
        raise DifferentDrivesException(exception_msg_provider(self_drive, other_drive))
    return path.relpath(actual, relative_to)
