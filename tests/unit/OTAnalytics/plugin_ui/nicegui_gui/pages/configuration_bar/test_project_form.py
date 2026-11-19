"""Tests the project form and its parts in the header."""

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, Mock

from nicegui import ui
from nicegui.testing import User

from OTAnalytics.application.resources.resource_manager import (
    ProjectKeys,
    ResourceManager,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.configuration_bar.project_form import (
    MARKER_PROJECT_NAME,
    MARKER_PROJECT_NEW,
    MARKER_PROJECT_OPEN,
    MARKER_PROJECT_SAVE,
    MARKER_PROJECT_SAVE_AS,
    MARKER_SAVE_STATE,
    MARKER_TITLE,
    ProjectActions,
    ProjectForm,
    ProjectTitle,
)

ENDPOINT = "/test-project"
ACTION_MARKERS = [
    MARKER_PROJECT_NEW,
    MARKER_PROJECT_OPEN,
    MARKER_PROJECT_SAVE,
    MARKER_PROJECT_SAVE_AS,
]


def create_viewmodel() -> Mock:
    viewmodel = Mock()
    viewmodel.start_new_project = AsyncMock()
    return viewmodel


def create_parts(
    viewmodel: Mock, resource_manager: ResourceManager
) -> tuple[ProjectForm, ProjectActions, ProjectTitle]:
    title = ProjectTitle(resource_manager)
    actions = ProjectActions(viewmodel, resource_manager, title)
    form = ProjectForm(viewmodel, resource_manager, actions, title)
    return form, actions, title


def label_text(user: User, marker: str) -> str:
    label = user.find(marker=marker).elements.pop()
    assert isinstance(label, ui.label)
    return label.text


class TestProjectActions:
    async def test_new_starts_a_new_project(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        viewmodel = create_viewmodel()
        _, actions, _ = create_parts(viewmodel, resource_manager)

        @ui.page(ENDPOINT)
        def page() -> None:
            actions.build()

        await user.open(ENDPOINT)
        user.find(marker=MARKER_PROJECT_NEW).click()
        await asyncio.sleep(0.1)

        viewmodel.start_new_project.assert_awaited_once()

    def test_introduces_the_save_button_to_the_view_model(
        self, resource_manager: ResourceManager
    ) -> None:
        viewmodel = create_viewmodel()

        _, actions, _ = create_parts(viewmodel, resource_manager)

        viewmodel.set_button_quick_save_config.assert_called_once_with(
            actions.quick_save_button
        )

    async def test_project_form_enables_and_disables_the_actions(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        form, actions, _ = create_parts(create_viewmodel(), resource_manager)

        @ui.page(ENDPOINT)
        def page() -> None:
            actions.build()

        await user.open(ENDPOINT)
        form.set_enabled_general_buttons(False)

        for marker in ACTION_MARKERS:
            button = user.find(marker=marker).elements.pop()
            assert isinstance(button, ui.button)
            assert not button.enabled, marker


class TestProjectTitle:
    async def test_shows_untitled_project_without_name(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        title = ProjectTitle(resource_manager)

        @ui.page(ENDPOINT)
        def page() -> None:
            title.build()

        await user.open(ENDPOINT)

        assert label_text(user, MARKER_TITLE) == resource_manager.get(
            ProjectKeys.LABEL_UNTITLED_PROJECT
        )
        assert label_text(user, MARKER_SAVE_STATE) == resource_manager.get(
            ProjectKeys.LABEL_ALL_CHANGES_SAVED
        )

    async def test_follows_the_project_name(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        form, _, title = create_parts(create_viewmodel(), resource_manager)

        @ui.page(ENDPOINT)
        def page() -> None:
            title.build()

        await user.open(ENDPOINT)
        form.update("Kreuzung", datetime(2024, 5, 14))

        assert label_text(user, MARKER_TITLE) == "Kreuzung"

    async def test_follows_the_save_state(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        _, actions, title = create_parts(create_viewmodel(), resource_manager)

        @ui.page(ENDPOINT)
        def page() -> None:
            title.build()
            actions.build()

        await user.open(ENDPOINT)
        actions.quick_save_button.set_state_changed_color()
        unsaved = label_text(user, MARKER_SAVE_STATE)
        actions.quick_save_button.set_default_color()

        assert unsaved == resource_manager.get(ProjectKeys.LABEL_UNSAVED_CHANGES)
        assert label_text(user, MARKER_SAVE_STATE) == resource_manager.get(
            ProjectKeys.LABEL_ALL_CHANGES_SAVED
        )


class TestProjectForm:
    async def test_shows_only_name_and_start_date(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        form, _, _ = create_parts(create_viewmodel(), resource_manager)

        @ui.page(ENDPOINT)
        def page() -> None:
            form.build()

        await user.open(ENDPOINT)

        await user.should_see(marker=MARKER_PROJECT_NAME)
        for marker in ACTION_MARKERS:
            await user.should_not_see(marker=marker)
        header = resource_manager.get(ProjectKeys.LABEL_PROJECT_FORM_HEADER)
        assert user.client is not None
        assert not [
            label
            for label in user.client.layout.descendants()
            if isinstance(label, ui.label) and label.text == header
        ]
