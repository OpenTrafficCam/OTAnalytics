from datetime import datetime
from pathlib import Path
from unittest.mock import Mock

import pytest

from OTAnalytics.application.state import ConfigurationFile, FileState
from OTAnalytics.application.use_cases.get_current_project import GetCurrentProject
from OTAnalytics.application.use_cases.suggest_save_path import (
    DATETIME_FORMAT,
    SavePathSuggester,
)
from OTAnalytics.application.use_cases.track_repository import GetAllTrackFiles
from OTAnalytics.application.use_cases.video_repository import GetAllVideos

FIRST_TRACK_FILE = Path("path/to/tracks/first.ottrk")
SECOND_TRACK_FILE = Path("path/to/tracks/second.ottrk")
FIRST_VIDEO_FILE = Path("path/to/videos/first.mp4")
SECOND_VIDEO_FILE = Path("path/to/videos/second.mp4")
PROJECT_NAME = "My Project Name"
DATETIME_NOW = datetime(2024, 1, 2, 3, 4, 5)
DATETIME_NOW_FORMATTED = DATETIME_NOW.strftime(DATETIME_FORMAT)
LAST_SAVED_OTCONFIG = Path("path/to/config/last.otconfig")
LAST_SAVED_OTFLOW = Path("path/to/otflow/last.otflow")


def create_file_state(last_saved_config_file: Path | None = None) -> FileState:
    state = FileState()
    if last_saved_config_file:
        state.last_saved_config.set(ConfigurationFile(last_saved_config_file, {}))
    return state


def create_track_file_provider(
    track_files: set[Path] | None = None,
) -> GetAllTrackFiles:
    if track_files:
        return Mock(return_value=track_files)
    return Mock(return_value=set())


def create_video_provider(video_files: list[Path] | None = None) -> GetAllVideos:
    videos = []
    if video_files:
        for video_file in video_files:
            video = Mock()
            video.get_path.return_value = video_file
            videos.append(video)
    get_videos = Mock()
    get_videos.get.return_value = videos
    return get_videos


def create_project_provider(project_name: str = "") -> GetCurrentProject:
    project = Mock()
    project.name = project_name
    get_project = Mock()
    get_project.get.return_value = project
    return get_project


def create_suggestor(
    project_name: str = "",
    last_saved_config: Path | None = None,
    track_files: set[Path] | None = None,
    video_files: list[Path] | None = None,
) -> SavePathSuggester:
    get_project = create_project_provider(project_name)
    file_state = create_file_state(last_saved_config)
    get_track_files = create_track_file_provider(track_files)
    get_videos = create_video_provider(video_files)
    return SavePathSuggester(
        file_state,
        get_track_files,
        get_videos,
        get_project,
        provide_datetime,
    )


def provide_datetime() -> datetime:
    return DATETIME_NOW


class TestSavePathSuggester:
    @pytest.mark.parametrize(
        (
            "project_name,last_saved_config,track_files,video_files,"
            "context_file_type,file_type,expected"
        ),
        [
            (
                "",
                None,
                None,
                None,
                "",
                "otconfig",
                Path.cwd() / f"{DATETIME_NOW_FORMATTED}.otconfig",
            ),
            (
                PROJECT_NAME,
                LAST_SAVED_OTCONFIG,
                {FIRST_TRACK_FILE, SECOND_TRACK_FILE},
                [FIRST_VIDEO_FILE, SECOND_VIDEO_FILE],
                "",
                "otconfig",
                LAST_SAVED_OTCONFIG.with_name(f"{LAST_SAVED_OTCONFIG.stem}.otconfig"),
            ),
            (
                PROJECT_NAME,
                LAST_SAVED_OTCONFIG,
                {FIRST_TRACK_FILE, SECOND_TRACK_FILE},
                [FIRST_VIDEO_FILE, SECOND_VIDEO_FILE],
                "events",
                "csv",
                LAST_SAVED_OTCONFIG.with_name(f"{LAST_SAVED_OTCONFIG.stem}.events.csv"),
            ),
            (
                PROJECT_NAME,
                None,
                {FIRST_TRACK_FILE, SECOND_TRACK_FILE},
                [FIRST_VIDEO_FILE, SECOND_VIDEO_FILE],
                "events",
                "csv",
                FIRST_TRACK_FILE.with_name(
                    f"{PROJECT_NAME}_{DATETIME_NOW_FORMATTED}.events.csv"
                ),
            ),
            (
                PROJECT_NAME,
                None,
                None,
                [FIRST_VIDEO_FILE, SECOND_VIDEO_FILE],
                "events",
                "csv",
                FIRST_VIDEO_FILE.with_name(
                    f"{PROJECT_NAME}_{DATETIME_NOW_FORMATTED}.events.csv"
                ),
            ),
            (
                PROJECT_NAME,
                LAST_SAVED_OTCONFIG,
                None,
                [FIRST_VIDEO_FILE, SECOND_VIDEO_FILE],
                "events",
                "csv",
                LAST_SAVED_OTCONFIG.with_name(f"{LAST_SAVED_OTCONFIG.stem}.events.csv"),
            ),
        ],
    )
    def test_suggest_default(
        self,
        project_name: str,
        last_saved_config: Path | None,
        track_files: set[Path] | None,
        video_files: list[Path] | None,
        context_file_type: str,
        file_type: str,
        expected: Path,
    ) -> None:
        suggestor = create_suggestor(
            project_name, last_saved_config, track_files, video_files
        )
        suggestion = suggestor.suggest(file_type, context_file_type)
        assert suggestion == expected
