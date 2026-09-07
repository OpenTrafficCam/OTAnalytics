"""Obtaining track and video files from S3 by selecting a time range.

All S3 knowledge stays here: nothing downstream computes object keys or knows
about the staging layout, which is what keeps lazy or streaming loading cheap to
adopt later.
"""

import bz2
from abc import ABC, abstractmethod
from datetime import timedelta
from pathlib import Path, PurePosixPath
from typing import Callable, Iterable

import ijson

from OTAnalytics.application.logger import logger
from OTAnalytics.application.use_cases.provide_input_files import (
    ProvideTrackFiles,
    ProvideVideoFiles,
)
from OTAnalytics.domain.load_window import LoadWindow
from OTAnalytics.plugin_parser import ottrk_dataformat
from OTAnalytics.plugin_s3.config.s3 import S3Config
from OTAnalytics.plugin_s3.download_objects import DownloadCancelled, DownloadObjects
from OTAnalytics.plugin_s3.list_objects import S3ListObjects
from OTAnalytics.plugin_s3.select_objects import select_in_window

TRACK_SUFFIXES = {".ottrk"}
VIDEO_SUFFIXES = {".mp4", ".avi", ".mkv", ".mov"}

LOAD_TRACKS_TITLE = "Load tracks from S3"
LOAD_VIDEOS_TITLE = "Load videos from S3"
DOWNLOADING_TRACKS = "Downloading tracks"
DOWNLOADING_VIDEOS = "Downloading videos"


class MissingVideoForTrackFile(Exception):
    """Raised when a track file's video is not in the bucket.

    Loading is all or nothing: without every video the load is abandoned rather
    than leaving the user with tracks they cannot see.
    """


class AskForLoadWindow(ABC):
    """Asks the user which time range to load.

    Owned by the S3 providers rather than added to `UiFactory`, because a new
    abstract method there would break OTCloud's `UnimplementedUiFactory`.
    """

    @abstractmethod
    async def ask(self, title: str) -> LoadWindow | None:
        """Ask for the time range to load.

        Args:
            title (str): the dialog title.

        Returns:
            LoadWindow | None: the selected window, None if the user cancelled.
        """
        raise NotImplementedError

    @abstractmethod
    def report_clamped(self, window: LoadWindow) -> None:
        """Tell the user the selected range was shortened.

        Args:
            window (LoadWindow): the window that will actually be loaded.
        """
        raise NotImplementedError


def read_video_name(ottrk: Path) -> str:
    """Read the name of the video a track file was produced from.

    The name comes from the ottrk's own metadata rather than from swapping the
    suffix, because a companion may be any supported video type.

    Args:
        ottrk (Path): the downloaded track file.

    Returns:
        str: the video file name, with extension.
    """
    with bz2.BZ2File(ottrk) as stream:
        events: Iterable = ijson.parse(stream)
        for metadata in ijson.items(events, ottrk_dataformat.METADATA):
            video = metadata[ottrk_dataformat.VIDEO]
            return str(video[ottrk_dataformat.FILENAME]) + str(
                video[ottrk_dataformat.FILETYPE]
            )
    raise MissingVideoForTrackFile(f"'{ottrk}' carries no video metadata.")


class _S3Provider:
    """What both providers share: asking for a window and listing the prefix."""

    def __init__(
        self,
        dialog: AskForLoadWindow,
        list_objects: S3ListObjects,
        download_objects: DownloadObjects,
        config: S3Config,
    ) -> None:
        self._dialog = dialog
        self._list_objects = list_objects
        self._download_objects = download_objects
        self._config = config

    async def _ask_for_window(self, title: str) -> LoadWindow | None:
        """Ask for a time range and hold it to the configured maximum.

        Args:
            title (str): the dialog title.

        Returns:
            LoadWindow | None: the window to load, None if the user cancelled.
        """
        selected = await self._dialog.ask(title)
        if selected is None:
            return None
        window = selected.clamp(self._maximum())
        if window.was_clamped:
            self._dialog.report_clamped(window)
        return window

    def _maximum(self) -> timedelta:
        return self._config.max_load_duration

    async def _list_keys(self) -> list[str]:
        return await self._list_objects.list_keys(self._config.key_prefix)


class S3TrackFileProvider(_S3Provider, ProvideTrackFiles):
    """Provides track files downloaded from S3 for a selected time range.

    Args:
        dialog (AskForLoadWindow): asks the user for the time range.
        list_objects (S3ListObjects): lists the bucket under the key prefix.
        download_objects (DownloadObjects): downloads the selected objects.
        config (S3Config): the S3 settings fixed at startup.
        read_video_name (Callable[[Path], str]): reads a track file's video name.
    """

    def __init__(
        self,
        dialog: AskForLoadWindow,
        list_objects: S3ListObjects,
        download_objects: DownloadObjects,
        config: S3Config,
        read_video_name: Callable[[Path], str] = read_video_name,
    ) -> None:
        super().__init__(dialog, list_objects, download_objects, config)
        self._read_video_name = read_video_name

    async def provide(self) -> list[Path]:
        window = await self._ask_for_window(LOAD_TRACKS_TITLE)
        if window is None:
            return []
        keys = await self._list_keys()
        track_keys = select_in_window(keys, window, TRACK_SUFFIXES)
        if not track_keys:
            logger().info(f"No track files in {window.start} - {window.end}")
            return []
        try:
            track_files = await self._download_objects.download_all(
                track_keys, DOWNLOADING_TRACKS
            )
            video_keys = self._resolve_videos(track_files, keys)
            await self._download_objects.download_all(video_keys, DOWNLOADING_VIDEOS)
        except DownloadCancelled:
            logger().info("Loading from S3 cancelled. Nothing was loaded.")
            return []
        return track_files

    def _resolve_videos(self, track_files: list[Path], keys: list[str]) -> list[str]:
        """Find the object key of every track file's video.

        Args:
            track_files (list[Path]): the downloaded track files.
            keys (list[str]): every object key found under the prefix.

        Returns:
            list[str]: the video keys, one per track file.

        Raises:
            MissingVideoForTrackFile: if any video is not in the bucket.
        """
        by_name = {PurePosixPath(key).name: key for key in keys}
        video_keys = []
        for track_file in track_files:
            video_name = self._read_video_name(track_file)
            if video_name not in by_name:
                raise MissingVideoForTrackFile(
                    f"'{track_file.name}' needs video '{video_name}', which is not"
                    f" in bucket '{self._config.bucket}'. Nothing was loaded."
                )
            video_keys.append(by_name[video_name])
        return video_keys


class S3VideoFileProvider(_S3Provider, ProvideVideoFiles):
    """Provides video files downloaded from S3 for a selected time range.

    Independent of any track load: the user may add videos on their own.
    """

    async def provide(self) -> list[Path]:
        window = await self._ask_for_window(LOAD_VIDEOS_TITLE)
        if window is None:
            return []
        keys = await self._list_keys()
        video_keys = select_in_window(keys, window, VIDEO_SUFFIXES)
        if not video_keys:
            logger().info(f"No videos in {window.start} - {window.end}")
            return []
        try:
            return await self._download_objects.download_all(
                video_keys, DOWNLOADING_VIDEOS
            )
        except DownloadCancelled:
            logger().info("Loading from S3 cancelled. Nothing was loaded.")
            return []
