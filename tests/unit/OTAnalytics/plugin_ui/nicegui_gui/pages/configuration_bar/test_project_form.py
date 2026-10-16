"""Tests the project form's button for starting a new project."""

import asyncio
from unittest.mock import AsyncMock, Mock

from nicegui import ui
from nicegui.testing import User

from OTAnalytics.application.resources.resource_manager import ResourceManager
from OTAnalytics.plugin_ui.nicegui_gui.pages.configuration_bar.project_form import (
    MARKER_PROJECT_NEW,
    ProjectForm,
)


class TestNewProjectButton:
    async def test_starts_a_new_project(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        viewmodel = create_viewmodel()
        target = ProjectForm(viewmodel, resource_manager)

        @ui.page("/test")
        def page() -> None:
            target.build()

        await user.open("/test")
        user.find(marker=MARKER_PROJECT_NEW).click()
        await asyncio.sleep(0.1)

        viewmodel.start_new_project.assert_awaited_once()

    async def test_is_disabled_with_the_other_general_buttons(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        target = ProjectForm(create_viewmodel(), resource_manager)

        @ui.page("/test")
        def page() -> None:
            target.build()

        await user.open("/test")

        assert target.new_project_button in target.get_general_buttons()


def create_viewmodel() -> Mock:
    viewmodel = Mock()
    viewmodel.start_new_project = AsyncMock()
    return viewmodel
