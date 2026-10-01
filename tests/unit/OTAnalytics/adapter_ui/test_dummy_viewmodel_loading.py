"""Tests that the view model delegates file selection to the providers.

The point of the provider seam is that `DummyViewModel` no longer knows where
input files come from. These tests pin that: the view model asks a provider and
forwards whatever it gets, with no file-chooser knowledge of its own.
"""

from dataclasses import dataclass
from pathlib import Path
from unittest.mock import AsyncMock, Mock

from OTAnalytics.adapter_ui.dummy_viewmodel import DummyViewModel
from OTAnalytics.application.use_cases.provide_input_files import (
    ProvideTrackFiles,
    ProvideVideoFiles,
)

TRACK_FILES = [Path("folder/a.ottrk"), Path("folder/b.ottrk")]
VIDEO_FILES = [Path("folder/a.mp4"), Path("folder/b.mp4")]


@dataclass
class Given:
    application: Mock
    provide_track_files: Mock
    provide_video_files: Mock


def create_given(
    tracks: list[Path] | None = None, videos: list[Path] | None = None
) -> Given:
    provide_track_files = Mock(spec=ProvideTrackFiles)
    provide_track_files.provide = AsyncMock(return_value=tracks or [])
    provide_video_files = Mock(spec=ProvideVideoFiles)
    provide_video_files.provide = AsyncMock(return_value=videos or [])
    application = Mock()
    application.add_tracks_of_files_async = AsyncMock()
    application.load_otconfig_async = AsyncMock()
    return Given(
        application=application,
        provide_track_files=provide_track_files,
        provide_video_files=provide_video_files,
    )


def create_target(given: Given) -> DummyViewModel:
    """A view model with the `@action` lifecycle stubbed out.

    `load_tracks` is decorated with `@action`, whose `_finish_action` refreshes
    the canvas and re-enables buttons — a fully wired widget tree that has
    nothing to do with where input files come from.
    """
    target = _build(given)
    target._start_action = Mock()  # type: ignore[method-assign]
    target._finish_action = Mock()  # type: ignore[method-assign]
    return target


def _build(given: Given) -> DummyViewModel:
    return DummyViewModel(
        application=given.application,
        ui_factory=Mock(),
        flow_parser=Mock(),
        name_generator=Mock(),
        event_list_export_formats={},
        show_svz=False,
        add_new_section=Mock(),
        update_section_coordinates=Mock(),
        provide_track_files=given.provide_track_files,
        provide_video_files=given.provide_video_files,
    )


class TestLoadTracks:
    async def test_forwards_the_provided_files(self) -> None:
        """Loading is awaited so the ui keeps repainting while parsing runs.

        #Requirement https://openproject.platomo.de/wp/10280
        #Requirement https://openproject.platomo.de/wp/10282
        """
        given = create_given(tracks=TRACK_FILES)
        target = create_target(given)

        await target.load_tracks()

        given.application.add_tracks_of_files_async.assert_awaited_once_with(
            track_files=TRACK_FILES
        )
        given.application.add_tracks_of_files.assert_not_called()

    async def test_loads_nothing_when_the_provider_returns_nothing(self) -> None:
        """#Requirement https://openproject.platomo.de/wp/10280"""
        given = create_given(tracks=[])
        target = create_target(given)

        await target.load_tracks()

        given.application.add_tracks_of_files_async.assert_not_awaited()


class TestAddVideo:
    async def test_forwards_the_provided_files(self) -> None:
        """#Requirement https://openproject.platomo.de/wp/10280"""
        given = create_given(videos=VIDEO_FILES)
        target = create_target(given)

        await target.add_video()

        given.application.add_videos.assert_called_once_with(files=VIDEO_FILES)

    async def test_loads_nothing_when_the_provider_returns_nothing(self) -> None:
        """#Requirement https://openproject.platomo.de/wp/10280"""
        given = create_given(videos=[])
        target = create_target(given)

        await target.add_video()

        given.application.add_videos.assert_not_called()
