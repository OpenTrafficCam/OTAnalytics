"""Tests for obtaining track and video files from S3 by time selection."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import AsyncMock, Mock

from OTAnalytics.application.key_prefix import S3KeyPrefix
from OTAnalytics.application.state import CurrentKeyPrefix
from OTAnalytics.application.use_cases.ask_for_load_window import AskForLoadWindow
from OTAnalytics.domain.load_window import LoadWindow
from OTAnalytics.plugin_s3.download_objects import DownloadCancelled
from OTAnalytics.plugin_s3.s3_file_providers import (
    S3TrackFileProvider,
    S3VideoFileProvider,
)

PREFIX = "cam19"
USER_SOURCE = Path("/staging")
START = datetime(2023, 5, 24, 6, 0, tzinfo=timezone.utc)
MAXIMUM = timedelta(hours=10)

TRACK_0600 = f"{PREFIX}/OTCamera19_FR20_2023-05-24_06-00-00.ottrk"
TRACK_0615 = f"{PREFIX}/OTCamera19_FR20_2023-05-24_06-15-00.ottrk"
TRACK_0900 = f"{PREFIX}/OTCamera19_FR20_2023-05-24_09-00-00.ottrk"
VIDEO_0600 = f"{PREFIX}/OTCamera19_FR20_2023-05-24_06-00-00.mp4"
VIDEO_0615 = f"{PREFIX}/OTCamera19_FR20_2023-05-24_06-15-00.mkv"
VIDEO_0900 = f"{PREFIX}/OTCamera19_FR20_2023-05-24_09-00-00.mp4"

ALL_KEYS = [TRACK_0600, TRACK_0615, TRACK_0900, VIDEO_0600, VIDEO_0615, VIDEO_0900]

VIDEO_NAMES = {
    USER_SOURCE / TRACK_0600: "OTCamera19_FR20_2023-05-24_06-00-00.mp4",
    USER_SOURCE / TRACK_0615: "OTCamera19_FR20_2023-05-24_06-15-00.mkv",
    USER_SOURCE / TRACK_0900: "OTCamera19_FR20_2023-05-24_09-00-00.mp4",
}


@dataclass
class Given:
    dialog: Mock
    list_objects: Mock
    download_objects: Mock
    config: Mock
    current_key_prefix: CurrentKeyPrefix
    downloads: list[tuple[list[str], str]]


def create_given(
    window: LoadWindow | None = None,
    keys: list[str] | None = None,
    cancel: bool = False,
    project_loaded: bool = True,
) -> Given:
    current_key_prefix = CurrentKeyPrefix()
    if project_loaded:
        current_key_prefix.set(S3KeyPrefix(PREFIX))
    given = Given(
        dialog=Mock(spec=AskForLoadWindow),
        list_objects=Mock(),
        download_objects=Mock(),
        config=Mock(),
        current_key_prefix=current_key_prefix,
        downloads=[],
    )
    given.config.bucket = "recordings"
    given.config.max_load_duration = MAXIMUM
    given.dialog.ask = AsyncMock(
        return_value=(
            window
            if window is not None
            else LoadWindow(start=START, end=START + timedelta(hours=1))
        )
    )
    given.list_objects.list_keys = AsyncMock(
        return_value=ALL_KEYS if keys is None else keys
    )

    async def fake_download_all(
        keys_to_load: list[str], description: str
    ) -> list[Path]:
        if cancel:
            raise DownloadCancelled(description)
        given.downloads.append((keys_to_load, description))
        return [USER_SOURCE / key for key in keys_to_load]

    given.download_objects.download_all = AsyncMock(side_effect=fake_download_all)
    return given


def read_video_name(ottrk: Path) -> str:
    return VIDEO_NAMES[ottrk]


def create_track_target(given: Given) -> S3TrackFileProvider:
    return S3TrackFileProvider(
        dialog=given.dialog,
        list_objects=given.list_objects,
        download_objects=given.download_objects,
        config=given.config,
        current_key_prefix=given.current_key_prefix,
        read_video_name=read_video_name,
    )


def create_video_target(given: Given) -> S3VideoFileProvider:
    return S3VideoFileProvider(
        dialog=given.dialog,
        list_objects=given.list_objects,
        download_objects=given.download_objects,
        config=given.config,
        current_key_prefix=given.current_key_prefix,
    )


class TestS3TrackFileProvider:
    """#Requirement https://openproject.platomo.de/wp/10283"""

    async def test_provides_the_track_files_in_the_selected_window(self) -> None:
        given = create_given()
        target = create_track_target(given)

        provided = await target.provide()

        assert provided == [USER_SOURCE / TRACK_0600, USER_SOURCE / TRACK_0615]

    async def test_lists_only_the_configured_prefix(self) -> None:
        given = create_given()
        target = create_track_target(given)

        await target.provide()

        given.list_objects.list_keys.assert_awaited_once_with(PREFIX)

    async def test_downloads_each_video_named_by_its_own_track_file(self) -> None:
        """The companion is read from the ottrk, not guessed as '.mp4'."""
        given = create_given()
        target = create_track_target(given)

        await target.provide()

        assert given.downloads[1][0] == [VIDEO_0600, VIDEO_0615]

    async def test_downloads_tracks_before_videos(self) -> None:
        given = create_given()
        target = create_track_target(given)

        await target.provide()

        assert [keys for keys, _ in given.downloads] == [
            [TRACK_0600, TRACK_0615],
            [VIDEO_0600, VIDEO_0615],
        ]

    async def test_a_missing_video_aborts_the_whole_load(self) -> None:
        given = create_given(keys=[TRACK_0600, TRACK_0615, VIDEO_0600])
        target = create_track_target(given)

        assert await target.provide() == []

    async def test_a_missing_video_is_named_to_the_user(self) -> None:
        given = create_given(keys=[TRACK_0600, TRACK_0615, VIDEO_0600])
        target = create_track_target(given)

        await target.provide()

        reported = given.dialog.report_error.call_args.args[0]
        assert "OTCamera19_FR20_2023-05-24_06-15-00.mkv" in reported

    async def test_a_missing_video_leaves_no_videos_downloaded(self) -> None:
        given = create_given(keys=[TRACK_0600, TRACK_0615, VIDEO_0600])
        target = create_track_target(given)

        await target.provide()

        assert [description for _, description in given.downloads] == [
            "Downloading tracks"
        ]

    async def test_choosing_no_window_loads_nothing(self) -> None:
        given = create_given()
        given.dialog.ask = AsyncMock(return_value=None)
        target = create_track_target(given)

        assert await target.provide() == []
        given.list_objects.list_keys.assert_not_awaited()

    async def test_an_empty_window_loads_nothing(self) -> None:
        given = create_given(
            window=LoadWindow(
                start=START - timedelta(days=1), end=START - timedelta(hours=23)
            )
        )
        target = create_track_target(given)

        assert await target.provide() == []
        given.download_objects.download_all.assert_not_awaited()

    async def test_cancelling_loads_nothing(self) -> None:
        given = create_given(cancel=True)
        target = create_track_target(given)

        assert await target.provide() == []

    async def test_a_failed_download_is_explained_rather_than_raised(self) -> None:
        """A raw traceback in the browser tells the user nothing useful."""
        given = create_given()
        given.download_objects.download_all = AsyncMock(
            side_effect=RuntimeError("the bucket said no")
        )
        target = create_track_target(given)

        assert await target.provide() == []

        given.dialog.report_error.assert_called_once()

    async def test_an_over_long_window_is_clamped_and_reported(self) -> None:
        given = create_given(
            window=LoadWindow(start=START, end=START + timedelta(hours=24))
        )
        target = create_track_target(given)

        provided = await target.provide()

        clamped = given.dialog.report_clamped.call_args.args[0]
        assert clamped.end == START + MAXIMUM
        assert clamped.was_clamped is True
        assert provided == [
            USER_SOURCE / TRACK_0600,
            USER_SOURCE / TRACK_0615,
            USER_SOURCE / TRACK_0900,
        ]

    async def test_a_window_within_the_cap_is_not_reported(self) -> None:
        given = create_given()
        target = create_track_target(given)

        await target.provide()

        given.dialog.report_clamped.assert_not_called()


class TestS3VideoFileProvider:
    """#Requirement https://openproject.platomo.de/wp/10283"""

    async def test_provides_the_videos_in_the_selected_window(self) -> None:
        given = create_given()
        target = create_video_target(given)

        provided = await target.provide()

        assert provided == [USER_SOURCE / VIDEO_0600, USER_SOURCE / VIDEO_0615]

    async def test_loads_videos_without_any_track_file(self) -> None:
        given = create_given()
        target = create_video_target(given)

        await target.provide()

        assert [keys for keys, _ in given.downloads] == [[VIDEO_0600, VIDEO_0615]]

    async def test_cancelling_loads_nothing(self) -> None:
        given = create_given(cancel=True)
        target = create_video_target(given)

        assert await target.provide() == []


class TestWithoutALoadedProject:
    """In s3 mode the prefix comes from the project, so until one is loaded
    there is nowhere to list.

    #Requirement https://openproject.platomo.de/wp/10322
    """

    async def test_asks_for_no_window_and_lists_nothing(self) -> None:
        given = create_given(project_loaded=False)
        target = create_track_target(given)

        provided = await target.provide()

        assert provided == []
        given.dialog.ask.assert_not_awaited()
        given.list_objects.list_keys.assert_not_awaited()

    async def test_says_a_project_has_to_be_loaded_first(self) -> None:
        given = create_given(project_loaded=False)
        target = create_video_target(given)

        await target.provide()

        given.dialog.report_error.assert_called_once()
        assert "project" in given.dialog.report_error.call_args.args[0]

    async def test_lists_under_the_prefix_the_loaded_project_declares(self) -> None:
        given = create_given()

        await create_video_target(given).provide()

        given.list_objects.list_keys.assert_awaited_once_with(PREFIX)
