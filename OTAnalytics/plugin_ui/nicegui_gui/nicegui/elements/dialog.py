from abc import abstractmethod
from enum import StrEnum

from nicegui import ui

from OTAnalytics.application.resources.resource_manager import (
    GeneralKeys,
    ResourceManager,
)
from OTAnalytics.plugin_ui.nicegui_gui.test_constants import TEST_ID

MARKER_APPLY = "apply"
MARKER_CANCEL = "cancel"


class DialogResult(StrEnum):
    APPLY = "Apply"
    CANCEL = "Cancel"


class BaseDialog:

    @property
    async def result(self) -> DialogResult:
        """Build, open, and await the dialog, returning the submitted result.

        NiceGUI dialogs must be opened explicitly and awaited to capture the
        value passed to dialog.submit(...). This method ensures the dialog is
        shown and returns the DialogResult provided by the Apply/Cancel buttons.
        """
        dialog = self.build()
        dialog.open()
        # Await the dialog; this resolves with the value passed to dialog.submit
        return await dialog

    def __init__(self, resource_manager: ResourceManager) -> None:
        self.resource_manager = resource_manager

    def build(self) -> ui.dialog:
        with ui.dialog() as dialog, ui.card().classes("w-96"):
            self.build_content()
            with ui.row():
                apply = ui.button(
                    self.resource_manager.get(GeneralKeys.LABEL_APPLY),
                    on_click=lambda: dialog.submit(DialogResult.APPLY),
                )
                cancel = ui.button(
                    self.resource_manager.get(GeneralKeys.LABEL_CANCEL),
                    on_click=lambda: dialog.submit(DialogResult.CANCEL),
                )
                # Keep generic markers for compatibility
                apply.mark(MARKER_APPLY)
                cancel.mark(MARKER_CANCEL)

                apply.props(f"{TEST_ID}={MARKER_APPLY}")
                cancel.props(f"{TEST_ID}={MARKER_CANCEL}")
            return dialog

    @abstractmethod
    def build_content(self) -> None:
        raise NotImplementedError
