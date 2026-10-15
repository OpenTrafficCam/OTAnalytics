from nicegui import ui

from OTAnalytics.application.resources.resource_manager import ResourceManager
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.dialog import BaseDialog
from OTAnalytics.plugin_ui.nicegui_gui.test_constants import TEST_ID

MARKER_CONFIRMATION_MESSAGE = "marker-confirmation-message"


class ConfirmationDialog(BaseDialog):
    """Ask the user to confirm an action with Apply or Cancel.

    Args:
        resource_manager (ResourceManager): provides the button labels.
        message (str): what the user is about to do.
    """

    def __init__(self, resource_manager: ResourceManager, message: str) -> None:
        super().__init__(resource_manager)
        self._message = message

    def build_content(self) -> None:
        message = ui.label(self._message).classes("whitespace-pre-line")
        message.mark(MARKER_CONFIRMATION_MESSAGE)
        message.props(f"{TEST_ID}={MARKER_CONFIRMATION_MESSAGE}")
