from nicegui import ui

from OTAnalytics.application.resources.resource_manager import (
    GeneralKeys,
    ResourceManager,
)
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.dialog import BaseDialog


class ConfirmationDialog(BaseDialog):
    """Modal dialog asking the user to confirm (OK) or cancel an action."""

    def __init__(self, resource_manager: ResourceManager, message: str) -> None:
        super().__init__(resource_manager)
        self._message = message

    def apply_label(self) -> str:
        return self.resource_manager.get(GeneralKeys.LABEL_OK)

    def build_content(self) -> None:
        ui.label(self._message).classes("whitespace-pre-line")
