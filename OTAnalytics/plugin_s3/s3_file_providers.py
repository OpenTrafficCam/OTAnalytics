"""Obtaining track and video files from S3 by selecting a time range.

All S3 knowledge stays here: nothing downstream computes object keys or knows
about the staging layout, which is what keeps lazy or streaming loading cheap to
adopt later.
"""

from pathlib import Path, PurePosixPath
from typing import Callable

import ijson

from OTAnalytics.application.logger import logger
from OTAnalytics.application.use_cases.ask_for_load_window import AskForLoadWindow
from OTAnalytics.application.use_cases.provide_input_files import (
    ProvideTrackFiles,
    ProvideVideoFiles,
)
from OTAnalytics.plugin_parser import ottrk_dataformat
from OTAnalytics.plugin_s3.config.s3 import S3Config
from OTAnalytics.plugin_s3.download_objects import DownloadCancelled, DownloadObjects
from OTAnalytics.plugin_s3.list_objects import S3ListObjects
from OTAnalytics.plugin_s3.select_objects import select_in_window
from OTAnalytics.plugin_track_input_source.template import (
    metadata_from_json_events,
    parse_json_bz2_events,
)

TRACK_SUFFIXES = {".ottrk"}
VIDEO_SUFFIXES = {".mp4", ".avi", ".mkv", ".mov"}

LOAD_TRACKS_TITLE = "Load tracks from S3"
LOAD_VIDEOS_TITLE = "Load videos from S3"
DOWNLOADING_TRACKS = "Downloading tracks"
DOWNLOADING_VIDEOS = "Downloading videos"

CANCELLED = "Loading from S3 cancelled. Nothing was loaded."


class MissingVideoForTrackFile(Exception):
    """Raised when a track file's video is not in the bucket.

    Loading is all or nothing: without every video the load is abandoned rather
    than leaving the user with tracks they cannot see.
    """


class UnreadableTrackFile(Exception):
    """Raised when a downloaded track file does not say which video it belongs to.

    A different failure from a video that is simply absent: here the object was
    fetched but cannot be understood, so no amount of looking in the bucket helps.
    """


def read_video_name(ottrk: Path) -> str:
    """Read the name of the video a track file was produced from.

    The name comes from the ottrk's own metadata rather than from swapping the
    suffix, because a companion may be any supported video type.

    Args:
        ottrk (Path): the downloaded track file.

    Returns:
        str: the video file name, with extension.

    Raises:
        UnreadableTrackFile: if the file carries no video metadata.
    """
    try:
        metadata = metadata_from_json_events(parse_json_bz2_events(ottrk))
        video = metadata[ottrk_dataformat.VIDEO]
        return str(video[ottrk_dataformat.FILENAME]) + str(
            video[ottrk_dataformat.FILETYPE]
        )
    except (KeyError, TypeError, OSError, ijson.JSONError) as cause:
        raise UnreadableTrackFile(
            f"'{ottrk.name}' does not say which video it belongs to."
        ) from cause


class _S3Provider:
    """The load sequence both providers share.

    Args:
        dialog (AskForLoadWindow): asks the user for the time range.
        list_objects (S3ListObjects): lists the bucket under the key prefix.
        download_objects (DownloadObjects): downloads the selected objects.
        config (S3Config): the S3 settings fixed at startup.
    """

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

    async def _provide(
        self, title: str, suffixes: set[str], description: str
    ) -> list[Path]:
        """Ask for a window, then download everything in it.

        Args:
            title (str): the dialog title.
            suffixes (set[str]): the file extensions to load.
            description (str): what to tell the user is being downloaded.

        Returns:
            list[Path]: the local paths, empty if nothing was loaded.
        """
        selected = await self._dialog.ask(title, self._source())
        if selected is None:
            return []
        window = selected.clamp(self._config.max_load_duration)
        if window.was_clamped:
            self._dialog.report_clamped(window)
        keys = await self._list_objects.list_keys(self._config.key_prefix)
        wanted = select_in_window(keys, window, suffixes)
        if not wanted:
            logger().info(f"Nothing to load between {window.start} and {window.end}")
            return []
        try:
            return await self._load(wanted, keys, description)
        except DownloadCancelled:
            logger().info(CANCELLED)
            return []
        except (MissingVideoForTrackFile, UnreadableTrackFile, OSError) as cause:
            logger().warning(str(cause))
            self._dialog.report_error(str(cause))
            return []

    async def _load(
        self, wanted: list[str], keys: list[str], description: str
    ) -> list[Path]:
        """Download what was selected. Overridden to fetch companions too."""
        return await self._download_objects.download_all(wanted, description)

    def _source(self) -> str:
        """Where files come from, for the user to see but not to change."""
        return f"{self._config.bucket}/{self._config.key_prefix}"


class S3TrackFileProvider(_S3Provider, ProvideTrackFiles):
    """Provides track files downloaded from S3, each with its own video.

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
        return await self._provide(
            LOAD_TRACKS_TITLE, TRACK_SUFFIXES, DOWNLOADING_TRACKS
        )

    async def _load(
        self, wanted: list[str], keys: list[str], description: str
    ) -> list[Path]:
        track_files = await self._download_objects.download_all(wanted, description)
        video_keys = self._resolve_videos(track_files, keys)
        await self._download_objects.download_all(video_keys, DOWNLOADING_VIDEOS)
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
        return await self._provide(
            LOAD_VIDEOS_TITLE, VIDEO_SUFFIXES, DOWNLOADING_VIDEOS
        )
