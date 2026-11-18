from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable

from OTAnalytics.application.files import ensure_dot_in_extension
from OTAnalytics.application.state import FileState
from OTAnalytics.application.use_cases.get_current_project import GetCurrentProject
from OTAnalytics.application.use_cases.track_repository import GetAllTrackFiles
from OTAnalytics.application.use_cases.video_repository import GetAllVideos

DATETIME_FORMAT = "%Y-%m-%d_%H-%M-%S"


@dataclass(frozen=True)
class SavePathSuggestion:
    save_directory: Path
    file_stem: str
    context_file_type: str | None
    file_type: str

    def __post_init__(self) -> None:
        if not self.file_type.startswith("."):
            raise ValueError(f"file_type must start with '.', got '{self.file_type}'")

        if self.context_file_type is not None and self.context_file_type.startswith(
            "."
        ):
            raise ValueError(
                f"context_file_type must not start with '.', got "
                f"'{self.context_file_type}'"
            )

    @property
    def file_path(self) -> Path:
        if self.context_file_type is not None:
            return (
                self.save_directory
                / f"{self.file_stem}.{self.context_file_type}{self.file_type}"
            )
        return self.save_directory / f"{self.file_stem}{self.file_type}"

    @property
    def name_without_file_type(self) -> str:
        """Filename suggestion without the trailing ``file_type`` extension."""
        if self.context_file_type is not None:
            return f"{self.file_stem}.{self.context_file_type}"
        return self.file_stem


class SavePathSuggester:
    """
    Class for suggesting save paths based on the config file, otflow file,
    the first track file, and video file.

    Args:
        file_state (FileState): Holds information on files loaded in application.
        get_all_track_files (GetAllTrackFiles): A use case that retrieves
            all track files.
        get_all_videos (GetAllVideos): A use case that retrieves all
            video files.
        get_project (GetCurrentProject): A use case that retrieves
            the current project.
    """

    @property
    def __config_file(self) -> Path | None:
        """The path to the last loaded or saved configuration file."""
        if config_file := self._file_state.last_saved_config.get():
            return config_file.file
        return None

    @property
    def __first_track_file(self) -> Path | None:
        """The path to the first track file."""

        if track_files := self._get_all_track_files():
            return next(iter(track_files))
        return None

    @property
    def __first_video_file(self) -> Path | None:
        """The path to the first video file."""

        if video_files := self._get_all_videos.get():
            return video_files[0].get_path()
        return None

    def __init__(
        self,
        file_state: FileState,
        get_all_track_files: GetAllTrackFiles,
        get_all_videos: GetAllVideos,
        get_project: GetCurrentProject,
        provide_datetime: Callable[[], datetime] = datetime.now,
    ) -> None:
        self._file_state = file_state
        self._get_all_track_files = get_all_track_files
        self._get_all_videos = get_all_videos
        self._get_project = get_project
        self._provide_datetime = provide_datetime

    def suggest(
        self, file_type: str, context_file_type: str = ""
    ) -> SavePathSuggestion:
        """Suggests a save path based on the given file type and an optional
        related file type.

        The suggested path is in the following format:
        <BASE FOLDER>/<FILE STEM>.<CONTEXT FILE TYPE>.<FILE TYPE>

        The base folder will be determined in the following precedence:
            1. First loaded config file (otconfig or otflow)
            2. First loaded track file (ottrk)
            3. First loaded video file
            4. Default: Current working directory

        The file stem suggestion will be determined in the following precedence:
            1. The file stem of the loaded config file (otconfig or otflow)
            2. <CURRENT PROJECT NAME>_<CURRENT DATE AND TIME>
            3. Default: <CURRENT DATE AND TIME>

        Args:
            file_type (str): Can start with or without a leading dot.
            context_file_type (str): the context file type.

        Returns:
            SavePathSuggestion (SavePathSuggestion): the suggested save path.
        """

        base_folder = self._retrieve_base_folder()
        file_stem = self._suggest_file_stem()
        actual_context_file_type = self._parse_context_file_type(context_file_type)
        sanitized_file_type = ensure_dot_in_extension(file_type)
        return SavePathSuggestion(
            save_directory=base_folder,
            file_stem=file_stem,
            context_file_type=actual_context_file_type,
            file_type=sanitized_file_type,
        )

    def _retrieve_base_folder(self) -> Path:
        """Returns the base folder for suggesting a new file name."""
        if self.__config_file:
            return self.__config_file.parent
        if self.__first_track_file:
            return self.__first_track_file.parent
        if self.__first_video_file:
            return self.__first_video_file.parent
        return Path.cwd()

    def _suggest_file_stem(self) -> str:
        """Generates a suggestion for the file stem."""

        if self.__config_file:
            return f"{self.__config_file.stem}"

        current_time = self._provide_datetime().strftime(DATETIME_FORMAT)
        if project_name := self._get_project.get().name:
            return f"{project_name}_{current_time}"
        return current_time

    def _parse_context_file_type(self, context_file_type: str) -> str | None:
        if context_file_type:
            return context_file_type.lower()
        return None
