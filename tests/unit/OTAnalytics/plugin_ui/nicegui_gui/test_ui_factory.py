import asyncio
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from unittest.mock import Mock, patch

import pytest
from nicegui import core, ui
from nicegui.client import Client
from nicegui.testing import User

from OTAnalytics.adapter_ui.message_type import MessageType
from OTAnalytics.application.resources.resource_manager import (
    GeneralKeys,
    ResourceManager,
)
from OTAnalytics.plugin_ui.nicegui_gui.ui_factory import (
    NiceGuiUiFactory,
    build_file_extensions,
)

OTCONFIG_FILETYPES = [("otconfig file", "*.otconfig")]
DOTTED_FILETYPES = [("CSV", ".csv")]
BARE_FILETYPES = [("CSV", "csv")]
MIXED_FILETYPES = [
    ("otflow file", "*.otflow"),
    ("otconfig file", "*.otconfig"),
]


@dataclass
class GivenFileExtensions:
    filetypes: list[tuple[str, str]]


def create_given(
    filetypes: list[tuple[str, str]] = OTCONFIG_FILETYPES,
) -> GivenFileExtensions:
    return GivenFileExtensions(filetypes=filetypes)


def create_target() -> Callable[..., dict[str, str]]:
    return build_file_extensions


class TestBuildFileExtensions:
    def test_strips_wildcard_from_glob_pattern(self) -> None:
        """A ``*.otconfig`` pattern must yield a bare ``otconfig`` extension.

        Leaving the wildcard in place caused saved files to be named
        ``project.*otconfig.otconfig`` (regression for OP#9548).
        """
        given = create_given(OTCONFIG_FILETYPES)
        target = create_target()

        result = target(given.filetypes)

        assert result == {"otconfig file": "otconfig"}

    def test_strips_leading_dot_extension(self) -> None:
        given = create_given(DOTTED_FILETYPES)
        target = create_target()

        result = target(given.filetypes)

        assert result == {"CSV": "csv"}

    def test_keeps_bare_extension_unchanged(self) -> None:
        given = create_given(BARE_FILETYPES)
        target = create_target()

        result = target(given.filetypes)

        assert result == {"CSV": "csv"}

    def test_cleans_every_filetype(self) -> None:
        given = create_given(MIXED_FILETYPES)
        target = create_target()

        result = target(given.filetypes)

        assert result == {"otflow file": "otflow", "otconfig file": "otconfig"}


CONFIRMATION_MESSAGE = "All configured sections will be removed."
POSITION = (0, 0)
HAS_BROWSER = "OTAnalytics.plugin_ui.nicegui_gui.ui_factory.has_browser_to_show_in"


@pytest.fixture
def browser() -> Iterator[None]:
    """Pretend a browser shows the page, so the ui calls can be inspected."""
    with patch(HAS_BROWSER, return_value=True):
        yield


@pytest.fixture
def before_app_start() -> Iterator[None]:
    """Run without a started app and without clients, as the preload at startup
    does. Clients left by other tests would keep NiceGUI out of script mode.

    Leaves no script mode behind, should the test fail by entering it.
    """
    assert not core.app.is_started
    with patch.dict(Client.instances, clear=True):
        yield
        if core.script_client is not None:
            # NiceGUI entered the client, which keeps its slot on the stack.
            core.script_client.__exit__()
            core.script_client.delete()
            core.script_client = None
        core.script_mode = False


def create_ui_factory(resource_manager: ResourceManager) -> NiceGuiUiFactory:
    return NiceGuiUiFactory(
        resource_manager,
        get_count_intervals=Mock(),
        get_counting_event=Mock(),
        get_save_name=Mock(),
        get_save_suffix=Mock(),
    )


async def _wait_for(answers: list[bool]) -> None:
    """Wait until the awaiting page handler has stored the dialog result."""
    for _ in range(100):
        if answers:
            return
        await asyncio.sleep(0.01)


class TestAskForConfirmation:
    async def test_ok_confirms(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        target = create_ui_factory(resource_manager)
        answers: list[bool] = []

        @ui.page("/test")
        async def page() -> None:
            await ui.context.client.connected()
            answers.append(
                await target.ask_for_confirmation(CONFIRMATION_MESSAGE, POSITION)
            )

        await user.open("/test")
        await user.should_see(CONFIRMATION_MESSAGE)
        user.find(resource_manager.get(GeneralKeys.LABEL_OK)).click()
        await _wait_for(answers)

        assert answers == [True]

    async def test_cancel_rejects(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        target = create_ui_factory(resource_manager)
        answers: list[bool] = []

        @ui.page("/test")
        async def page() -> None:
            await ui.context.client.connected()
            answers.append(
                await target.ask_for_confirmation(CONFIRMATION_MESSAGE, POSITION)
            )

        await user.open("/test")
        await user.should_see(CONFIRMATION_MESSAGE)
        user.find(resource_manager.get(GeneralKeys.LABEL_CANCEL)).click()
        await _wait_for(answers)

        assert answers == [False]


@pytest.mark.usefixtures("browser")
class TestShowMessage:
    def test_info_box_shows_an_error(self, resource_manager: ResourceManager) -> None:
        target = create_ui_factory(resource_manager)

        with patch.object(ui, "notify") as notify:
            target.info_box(message=CONFIRMATION_MESSAGE, initial_position=POSITION)

        notify.assert_called_once()
        assert notify.call_args.kwargs["type"] == "negative"

    @pytest.mark.parametrize(
        "message_type, notification_type",
        [
            (MessageType.ERROR, "negative"),
            (MessageType.WARNING, "warning"),
            (MessageType.INFO, "info"),
        ],
    )
    def test_shows_message_with_type(
        self,
        resource_manager: ResourceManager,
        message_type: MessageType,
        notification_type: str,
    ) -> None:
        target = create_ui_factory(resource_manager)

        with patch.object(ui, "notify") as notify:
            target.show_message(
                message=CONFIRMATION_MESSAGE,
                initial_position=POSITION,
                message_type=message_type,
            )

        notify.assert_called_once()
        assert notify.call_args.args[0] == CONFIRMATION_MESSAGE
        assert notify.call_args.kwargs["type"] == notification_type


class TestMinimalInfoBox:
    @pytest.mark.usefixtures("browser")
    def test_shows_persistent_notification(
        self, resource_manager: ResourceManager
    ) -> None:
        target = create_ui_factory(resource_manager)

        with patch.object(ui, "notification") as notification:
            target.minimal_info_box(
                message=CONFIRMATION_MESSAGE, initial_position=POSITION
            )

        notification.assert_called_once()
        assert notification.call_args.args[0] == CONFIRMATION_MESSAGE
        assert notification.call_args.kwargs["timeout"] is None

    @pytest.mark.usefixtures("browser")
    def test_update_message_changes_text(
        self, resource_manager: ResourceManager
    ) -> None:
        target = create_ui_factory(resource_manager)

        with patch.object(ui, "notification") as notification:
            box = target.minimal_info_box(
                message=CONFIRMATION_MESSAGE, initial_position=POSITION
            )
            box.update_message("Done")

        assert notification.return_value.message == "Done"

    @pytest.mark.usefixtures("browser")
    def test_close_dismisses_notification(
        self, resource_manager: ResourceManager
    ) -> None:
        target = create_ui_factory(resource_manager)

        with patch.object(ui, "notification") as notification:
            box = target.minimal_info_box(
                message=CONFIRMATION_MESSAGE, initial_position=POSITION
            )
            box.close()

        notification.return_value.dismiss.assert_called_once()

    def test_without_browser_shows_nothing(
        self, resource_manager: ResourceManager
    ) -> None:
        target = create_ui_factory(resource_manager)

        with (
            patch(HAS_BROWSER, return_value=False),
            patch.object(ui, "notification") as notification,
        ):
            box = target.minimal_info_box(
                message=CONFIRMATION_MESSAGE, initial_position=POSITION
            )
            box.update_message("Done")
            box.close()

        notification.assert_not_called()

    async def test_is_visible_in_browser(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        target = create_ui_factory(resource_manager)

        @ui.page("/test")
        def page() -> None:
            box = target.minimal_info_box(
                message=CONFIRMATION_MESSAGE, initial_position=POSITION
            )
            ui.button("update", on_click=lambda: box.update_message("Done"))

        await user.open("/test")
        await user.should_see(CONFIRMATION_MESSAGE)
        user.find("update").click()
        await user.should_see("Done")


@pytest.mark.usefixtures("before_app_start")
class TestBeforeTheAppIsStarted:
    """Preloading input files at startup reports to the user before any page
    exists. Creating ui then would make NiceGUI warn and discard it.
    """

    @pytest.mark.parametrize(
        "message_type", [MessageType.ERROR, MessageType.WARNING, MessageType.INFO]
    )
    def test_show_message_creates_no_ui(
        self, resource_manager: ResourceManager, message_type: MessageType
    ) -> None:
        target = create_ui_factory(resource_manager)

        target.show_message(
            message=CONFIRMATION_MESSAGE,
            initial_position=POSITION,
            message_type=message_type,
        )

        assert core.script_mode is False

    def test_info_box_creates_no_ui(self, resource_manager: ResourceManager) -> None:
        target = create_ui_factory(resource_manager)

        target.info_box(message=CONFIRMATION_MESSAGE, initial_position=POSITION)

        assert core.script_mode is False

    def test_minimal_info_box_creates_no_ui(
        self, resource_manager: ResourceManager
    ) -> None:
        target = create_ui_factory(resource_manager)

        box = target.minimal_info_box(
            message=CONFIRMATION_MESSAGE, initial_position=POSITION
        )
        box.update_message("Done")
        box.close()

        assert core.script_mode is False
