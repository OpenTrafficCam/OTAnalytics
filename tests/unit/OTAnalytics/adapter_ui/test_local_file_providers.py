"""Tests for the local-filesystem track and video file providers."""

from dataclasses import dataclass
from pathlib import Path
from unittest.mock import AsyncMock, Mock

from OTAnalytics.adapter_ui.local_file_providers import (
    LocalTrackFileProvider,
    LocalVideoFileProvider,
)
from OTAnalytics.adapter_ui.ui_factory import UiFactory

TRACK_FILES = [Path("folder/a.ottrk"), Path("folder/b.ottrk")]
VIDEO_FILES = [Path("folder/a.mp4"), Path("folder/b.mp4")]


@dataclass
class Given:
    ui_factory: Mock


def create_given(chosen: list[Path]) -> Given:
    ui_factory = Mock(spec=UiFactory)
    ui_factory.askopenfilenames = AsyncMock(return_value=chosen)
    return Given(ui_factory=ui_factory)


def create_track_target(given: Given) -> LocalTrackFileProvider:
    return LocalTrackFileProvider(given.ui_factory)


def create_video_target(given: Given) -> LocalVideoFileProvider:
    return LocalVideoFileProvider(given.ui_factory)


class TestLocalTrackFileProvider:
    async def test_provide_returns_the_chosen_files(self) -> None:
        given = create_given(TRACK_FILES)
        target = create_track_target(given)

        assert await target.provide() == TRACK_FILES

    async def test_provide_asks_for_ottrk_files(self) -> None:
        given = create_given(TRACK_FILES)
        target = create_track_target(given)

        await target.provide()

        given.ui_factory.askopenfilenames.assert_awaited_once_with(
            title="Load track files",
            filetypes=[("tracks file", "*.ottrk")],
        )

    async def test_cancelled_selection_provides_nothing(self) -> None:
        given = create_given([])
        target = create_track_target(given)

        assert await target.provide() == []


class TestLocalVideoFileProvider:
    async def test_provide_returns_the_chosen_files(self) -> None:
        given = create_given(VIDEO_FILES)
        target = create_video_target(given)

        assert await target.provide() == VIDEO_FILES

    async def test_provide_offers_every_supported_video_type(self) -> None:
        """The extension options the view model used to build itself.

        # Requirement OP#10280
        """
        given = create_given(VIDEO_FILES)
        target = create_video_target(given)

        await target.provide()

        given.ui_factory.askopenfilenames.assert_awaited_once_with(
            title="Load video files",
            filetypes=[("video file", [".mp4", ".avi", ".mkv", ".mov"])],
            extension_options={
                "All File Endings": [".mp4", ".avi", ".mkv", ".mov"],
                ".mp4": [".mp4"],
                ".avi": [".avi"],
                ".mkv": [".mkv"],
                ".mov": [".mov"],
            },
        )

    async def test_cancelled_selection_provides_nothing(self) -> None:
        given = create_given([])
        target = create_video_target(given)

        assert await target.provide() == []
