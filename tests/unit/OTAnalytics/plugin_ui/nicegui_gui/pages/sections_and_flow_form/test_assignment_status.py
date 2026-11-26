"""Tests the notice about an outdated track assignment in the status bar."""

from unittest.mock import Mock

from nicegui import ui
from nicegui.testing import User

from OTAnalytics.application.resources.resource_manager import (
    FlowKeys,
    ResourceManager,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.sections_and_flow_form.assignment_status import (  # noqa
    MARKER_ASSIGNMENT_OUTDATED,
    AssignmentStatus,
)

ENDPOINT = "/test-assignment-status"


async def open_status(user: User, target: AssignmentStatus) -> None:
    @ui.page(ENDPOINT)
    def page() -> None:
        target.build()

    await user.open(ENDPOINT)


class TestAssignmentStatus:
    async def test_is_hidden_while_up_to_date(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        await open_status(user, AssignmentStatus(resource_manager, Mock()))

        await user.should_not_see(marker=MARKER_ASSIGNMENT_OUTDATED)

    async def test_shows_when_outdated(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        target = AssignmentStatus(resource_manager, Mock())
        await open_status(user, target)

        target.show_outdated(True)

        await user.should_see(marker=MARKER_ASSIGNMENT_OUTDATED)
        await user.should_see(resource_manager.get(FlowKeys.LABEL_ASSIGNMENT_OUTDATED))

    async def test_update_assigns_the_tracks(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        update = Mock()
        target = AssignmentStatus(resource_manager, update)
        await open_status(user, target)
        target.show_outdated(True)

        user.find(resource_manager.get(FlowKeys.BUTTON_UPDATE_OUTDATED)).click()

        update.assert_called_once_with()

    def test_can_be_told_before_build(self, resource_manager: ResourceManager) -> None:
        AssignmentStatus(resource_manager, Mock()).show_outdated(True)
