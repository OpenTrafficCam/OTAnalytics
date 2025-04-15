from abc import abstractmethod
from enum import StrEnum

from nicegui import ui

from OTAnalytics.application.resources.resource_manager import (
    GeneralKeys,
    ResourceManager,
)


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
                ui.button(
                    self.resource_manager.get(GeneralKeys.LABEL_APPLY),
                    on_click=lambda: dialog.submit(DialogResult.APPLY),
                )
                ui.button(
                    self.resource_manager.get(GeneralKeys.LABEL_CANCEL),
                    on_click=lambda: dialog.submit(DialogResult.CANCEL),
                )
            return await dialog

    @abstractmethod
    async def build_content(self) -> None:
        raise NotImplementedError
