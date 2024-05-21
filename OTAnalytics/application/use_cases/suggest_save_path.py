from datetime import datetime
from pathlib import Path
from typing import Callable

from OTAnalytics.application.state import FileState
from OTAnalytics.application.use_cases.get_current_project import GetCurrentProject
from OTAnalytics.application.use_cases.track_repository import GetAllTrackFiles
from OTAnalytics.application.use_cases.video_repository import GetAllVideos

DATETIME_FORMAT = "%Y-%m-%d_%H-%M-%S"


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

    def suggest(self, file_type: str, context_file_type: str = "") -> Path:
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
            file_type (str): the file type.
            context_file_type (str): the context file type.
        """

        base_folder = self._retrieve_base_folder()
        file_stem = self._suggest_file_stem()
        if context_file_type:
            return base_folder / f"{file_stem}.{context_file_type}.{file_type}"
        return base_folder / f"{file_stem}.{file_type}"

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
