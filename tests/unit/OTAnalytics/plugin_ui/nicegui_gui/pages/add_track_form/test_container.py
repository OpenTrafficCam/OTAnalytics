"""Tests the track files and videos in the Project group."""

from pathlib import Path
from unittest.mock import Mock

from nicegui import ui
from nicegui.element import Element
from nicegui.testing import User

from OTAnalytics.application.resources.resource_manager import (
    ResourceManager,
    TrackFormKeys,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.add_track_form.container import (
    MARKER_TRACK_FILE,
    MARKER_TRACK_TAB,
    MARKER_VIDEO_TAB,
    TrackForm,
)

ENDPOINT = "/test-track-form"
ADD_TRACKS = "add tracks form"
VIDEOS = "add videos form"


def part(text: str) -> Mock:
    part = Mock()
    part.build.side_effect = lambda: ui.label(text)
    return part


def texts_in_order(element: Element) -> list[str]:
    texts = [element.text] if isinstance(element, ui.label) else []
    for child in element.default_slot.children:
        texts.extend(texts_in_order(child))
    return texts


def track_file_names(user: User) -> list[str]:
    try:
        elements = user.find(marker=MARKER_TRACK_FILE).elements
    except AssertionError:
        return []
    return sorted(element.text for element in elements if isinstance(element, ui.label))


async def open_form(user: User, target: TrackForm) -> None:
    @ui.page(ENDPOINT)
    def page() -> None:
        target.build()

    await user.open(ENDPOINT)


def create_view_model(track_files: set[Path]) -> Mock:
    view_model = Mock()
    view_model.get_all_track_files.return_value = track_files
    return view_model


class TestTrackForm:
    async def test_shows_track_files_then_videos_without_tabs(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        target = TrackForm(
            resource_manager, create_view_model(set()), part(ADD_TRACKS), part(VIDEOS)
        )

        await open_form(user, target)

        assert user.client is not None
        texts = texts_in_order(user.client.layout)
        assert texts == [
            resource_manager.get(TrackFormKeys.LABEL_TRACK_FILES),
            ADD_TRACKS,
            resource_manager.get(TrackFormKeys.LABEL_VIDEOS),
            VIDEOS,
        ]
        await user.should_not_see(kind=ui.tabs)
        await user.should_see(marker=MARKER_TRACK_TAB)
        await user.should_see(marker=MARKER_VIDEO_TAB)

    async def test_lists_the_track_files(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        view_model = create_view_model({Path("/data/b.ottrk"), Path("/data/a.ottrk")})
        target = TrackForm(resource_manager, view_model, part(ADD_TRACKS), part(VIDEOS))

        await open_form(user, target)

        assert track_file_names(user) == ["a.ottrk", "b.ottrk"]

    async def test_follows_loaded_tracks(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        view_model = create_view_model(set())
        target = TrackForm(resource_manager, view_model, part(ADD_TRACKS), part(VIDEOS))
        await open_form(user, target)
        view_model.get_all_track_files.return_value = {Path("/data/a.ottrk")}

        target.notify_tracks(Mock())

        assert track_file_names(user) == ["a.ottrk"]

    def test_tracks_loaded_before_build_are_ignored(
        self, resource_manager: ResourceManager
    ) -> None:
        target = TrackForm(
            resource_manager, create_view_model(set()), part(ADD_TRACKS), part(VIDEOS)
        )

        target.notify_tracks(Mock())
