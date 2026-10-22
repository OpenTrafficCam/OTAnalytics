"""Tests for asking the user to confirm an action in the browser."""

import pytest
from nicegui import ui
from nicegui.testing import User

from OTAnalytics.application.resources.resource_manager import ResourceManager
from OTAnalytics.plugin_ui.nicegui_gui.ui_factory import NiceGuiUiFactory

MESSAGE = "This will start a new project."


class TestAskForConfirmation:
    @pytest.mark.parametrize("button, expected", [("OK", True), ("Cancel", False)])
    async def test_provides_the_users_answer(
        self,
        user: User,
        resource_manager: ResourceManager,
        button: str,
        expected: bool,
    ) -> None:
        target = NiceGuiUiFactory(resource_manager)
        answers: list[bool] = []

        @ui.page("/test")
        async def page() -> None:
            answers.append(await target.ask_for_confirmation(MESSAGE, (0, 0)))

        await user.open("/test")
        await user.should_see(MESSAGE)
        user.find(button).click()
        await user.should_not_see(MESSAGE)

        assert answers == [expected]
