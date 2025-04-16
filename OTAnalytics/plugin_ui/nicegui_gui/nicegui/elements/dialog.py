from abc import abstractmethod
from enum import StrEnum

from nicegui import ui

from OTAnalytics.application.resources.resource_manager import (
    GeneralKeys,
    ResourceManager,
)

MARKER_APPLY = "apply"
MARKER_CANCEL = "cancel"


class DialogResult(StrEnum):
    APPLY = "Apply"
    CANCEL = "Cancel"


class BaseDialog(ui.dialog):

    def __init__(self, resource_manager: ResourceManager) -> None:
        super().__init__()
        self.resource_manager = resource_manager

    async def build(self) -> DialogResult:
        with ui.dialog() as dialog, ui.card():
            await self.build_content()
            with ui.row():
                apply = ui.button(
                    self.resource_manager.get(GeneralKeys.LABEL_APPLY),
                    on_click=lambda: dialog.submit(DialogResult.APPLY),
                )
                cancel = ui.button(
                    self.resource_manager.get(GeneralKeys.LABEL_CANCEL),
                    on_click=lambda: dialog.submit(DialogResult.CANCEL),
                )
                apply.mark(MARKER_APPLY)
                cancel.mark(MARKER_CANCEL)
            return await dialog

    @abstractmethod
    async def build_content(self) -> None:
        raise NotImplementedError
