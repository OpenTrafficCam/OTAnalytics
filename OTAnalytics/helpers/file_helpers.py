from pathlib import Path
from typing import Iterable

from OTAnalytics.application.logger import logger


def get_all_files_with_correct_file_ending_in_directory(
    files: Iterable[Path], file_types: list[str]
) -> list[Path]:
    files_to_save: set[Path] = set()
    for file_type in file_types:
        for file in files:
            file_to_save = file.expanduser()
            if file_to_save.is_dir():
                files_in_directory = file_to_save.rglob(file_type)
                files_to_save.update(files_in_directory)
                continue

            if not file_to_save.exists() or file_to_save.suffix != file_type:
                logger().warning(
                    f"Ottrk file'{file_to_save}' does not exist. Skipping file."
                )
                continue

            files_to_save.add(file_to_save)
    return list(files_to_save)
