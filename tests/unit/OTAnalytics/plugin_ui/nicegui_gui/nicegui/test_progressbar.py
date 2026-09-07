"""Tests for the in-browser progressbar of the webui."""

from dataclasses import dataclass

import pytest
from nicegui import ui
from nicegui.testing import User

from OTAnalytics.application.progress import Cancellation
from OTAnalytics.application.resources.resource_manager import ResourceManager
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.progressbar import (
    MARKER_PROGRESSBAR_CANCEL,
    NiceguiProgressbar,
    NiceguiProgressbarBuilder,
)

FILES = ["first.mp4", "second.mp4", "third.mp4", "fourth.mp4"]


@dataclass
class Given:
    resource_manager: ResourceManager
    cancellation: Cancellation


def create_given(resource_manager: ResourceManager) -> Given:
    return Given(resource_manager=resource_manager, cancellation=Cancellation())


def create_target(given: Given, total: int = 4) -> NiceguiProgressbar:
    return NiceguiProgressbar(
        resource_manager=given.resource_manager,
        description="Downloading",
        unit="files",
        total=total,
        cancellation=given.cancellation,
    )


def create_builder(given: Given) -> NiceguiProgressbarBuilder:
    return NiceguiProgressbarBuilder(given.resource_manager)


class TestNiceguiProgressbar:
    """#Requirement https://openproject.platomo.de/wp/10281"""

    @pytest.mark.asyncio
    async def test_shows_counts_and_the_current_item(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        given = create_given(resource_manager)
        target = create_target(given)

        @ui.page("/test")
        def page() -> None:
            target.open()

        await user.open("/test")
        await user.should_see("Downloading 0 / 4 files")

        target.complete("second.mp4")

        await user.should_see("Downloading 1 / 4 files")
        await user.should_see("second.mp4")

    @pytest.mark.asyncio
    async def test_cancel_button_triggers_the_cancellation_signal(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        given = create_given(resource_manager)
        target = create_target(given)

        @ui.page("/test")
        def page() -> None:
            target.open()

        await user.open("/test")
        assert given.cancellation.is_cancelled is False

        user.find(marker=MARKER_PROGRESSBAR_CANCEL).click()

        assert given.cancellation.is_cancelled is True
        assert target.is_open is False

    @pytest.mark.asyncio
    async def test_closes_once_every_item_completed(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        given = create_given(resource_manager)
        target = create_target(given, total=2)

        @ui.page("/test")
        def page() -> None:
            target.open()

        await user.open("/test")
        assert target.is_open is True

        target.complete("second.mp4")
        target.complete("first.mp4")

        assert target.is_open is False


class TestNiceguiProgressbarBuilder:
    """#Requirement https://openproject.platomo.de/wp/10281"""

    @pytest.mark.asyncio
    async def test_yields_every_element_and_counts_up(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        given = create_given(resource_manager)
        target = create_builder(given)
        seen = []
        counts = []

        @ui.page("/test")
        def page() -> None:
            progressbar = target(FILES, "Parsing", "files")
            for element in progressbar:
                seen.append(element)
                counts.append(target.progressbar.state.message)

        await user.open("/test")

        assert seen == FILES
        # an element counts as done once the consumer comes back for the next one
        assert counts == [
            "Parsing 0 / 4 files",
            "Parsing 1 / 4 files",
            "Parsing 2 / 4 files",
            "Parsing 3 / 4 files",
        ]
        assert target.progressbar.state.message == "Parsing 4 / 4 files"
        assert target.progressbar.state.finished is True

    @pytest.mark.asyncio
    async def test_shows_nothing_for_an_empty_sequence(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        """There is no progress to show, and nothing would ever close it again."""
        given = create_given(resource_manager)
        target = create_builder(given)

        @ui.page("/test")
        def page() -> None:
            list(target([], "Parsing", "files"))

        await user.open("/test")

        assert target.progressbar.is_open is False

    @pytest.mark.asyncio
    async def test_closes_the_previous_progressbar(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        given = create_given(resource_manager)
        target = create_builder(given)
        progressbars = []

        @ui.page("/test")
        def page() -> None:
            progressbars.append(target.build("Downloading", "files", 2))
            progressbars.append(target.build("Parsing", "files", 2))

        await user.open("/test")

        assert progressbars[0].is_open is False
        assert progressbars[1].is_open is True


class TestProgressbarWithoutABrowser:
    """#Requirement https://openproject.platomo.de/wp/10281"""

    @pytest.mark.asyncio
    async def test_shows_nothing_when_no_browser_is_connected(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        """Preloading input files at startup runs before any page is served."""
        given = create_given(resource_manager)
        target = create_target(given, total=2)

        target.open()

        assert target.is_open is False

    @pytest.mark.asyncio
    async def test_still_tracks_progress_when_no_browser_is_connected(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        given = create_given(resource_manager)
        target = create_target(given, total=2)
        target.open()

        target.complete("first.mp4")

        assert target.state.message == "Downloading 1 / 2 files"
