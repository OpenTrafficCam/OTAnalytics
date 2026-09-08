"""Tests for the dialog that asks which time range to load from S3."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import pytest
from nicegui import ui
from nicegui.testing import User

from OTAnalytics.application.resources.resource_manager import (
    LoadWindowKeys,
    ResourceManager,
)
from OTAnalytics.domain.load_window import LoadWindow
from OTAnalytics.plugin_s3.s3_file_providers import AskForLoadWindow
from OTAnalytics.plugin_ui.nicegui_gui.dialogs.load_window_dialog import (
    MARKER_END_DATE,
    MARKER_END_TIME,
    MARKER_START_DATE,
    MARKER_START_TIME,
    LoadWindowDialog,
)

TITLE = "Load tracks from S3"
START = datetime(2023, 5, 24, 6, 0, tzinfo=timezone.utc)


@dataclass
class Given:
    resource_manager: ResourceManager


def create_given(resource_manager: ResourceManager) -> Given:
    return Given(resource_manager=resource_manager)


def create_target(given: Given) -> LoadWindowDialog:
    return LoadWindowDialog(given.resource_manager)


def _type_window(user: User, start: datetime, end: datetime) -> None:
    user.find(marker=MARKER_START_DATE).clear().type(start.strftime("%Y-%m-%d"))
    user.find(marker=MARKER_START_TIME).clear().type(start.strftime("%H:%M:%S"))
    user.find(marker=MARKER_END_DATE).clear().type(end.strftime("%Y-%m-%d"))
    user.find(marker=MARKER_END_TIME).clear().type(end.strftime("%H:%M:%S"))


class TestLoadWindowDialog:
    """#Requirement https://openproject.platomo.de/wp/10283"""

    def test_is_the_seam_the_providers_ask_through(
        self, resource_manager: ResourceManager
    ) -> None:
        given = create_given(resource_manager)

        assert isinstance(create_target(given), AskForLoadWindow)

    async def test_provides_the_selected_window(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        given = create_given(resource_manager)
        target = create_target(given)
        end = START + timedelta(hours=2)
        selected: list[LoadWindow | None] = []

        @ui.page("/test")
        async def page() -> None:
            selected.append(await target.ask(TITLE))

        await user.open("/test")
        await user.should_see(TITLE)
        _type_window(user, START, end)
        user.find("Load").click()
        await user.should_not_see(TITLE)

        assert selected == [LoadWindow(start=START, end=end)]

    async def test_cancelling_provides_nothing(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        given = create_given(resource_manager)
        target = create_target(given)
        selected: list[LoadWindow | None] = []

        @ui.page("/test")
        async def page() -> None:
            selected.append(await target.ask(TITLE))

        await user.open("/test")
        _type_window(user, START, START + timedelta(hours=2))
        user.find("Cancel").click()
        await user.should_not_see(TITLE)

        assert selected == [None]

    async def test_labels_the_fields_as_utc(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        """The digits in the file names are UTC, and a user in Berlin is not."""
        given = create_given(resource_manager)
        target = create_target(given)

        @ui.page("/test")
        async def page() -> None:
            await target.ask(TITLE)

        await user.open("/test")

        await user.should_see(resource_manager.get(LoadWindowKeys.LABEL_UTC_HINT))

    async def test_reports_a_shortened_range(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        given = create_given(resource_manager)
        target = create_target(given)
        clamped = LoadWindow(
            start=START, end=START + timedelta(hours=10), was_clamped=True
        )

        @ui.page("/test")
        def page() -> None:
            target.report_clamped(clamped)

        await user.open("/test")

        await user.should_see(
            resource_manager.get(LoadWindowKeys.MESSAGE_CLAMPED), retries=200
        )


class TestRejectedSelections:
    """#Requirement https://openproject.platomo.de/wp/10283"""

    @pytest.mark.parametrize(
        "hours, message_key",
        [
            pytest.param(
                -1, LoadWindowKeys.MESSAGE_END_BEFORE_START, id="end_before_start"
            ),
        ],
    )
    async def test_refuses_an_impossible_range(
        self,
        user: User,
        resource_manager: ResourceManager,
        hours: int,
        message_key: LoadWindowKeys,
    ) -> None:
        given = create_given(resource_manager)
        target = create_target(given)

        @ui.page("/test")
        async def page() -> None:
            await target.ask(TITLE)

        await user.open("/test")
        _type_window(user, START, START + timedelta(hours=hours))
        user.find("Load").click()

        await user.should_see(resource_manager.get(message_key), retries=200)
        await user.should_see(TITLE)
