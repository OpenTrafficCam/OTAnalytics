from typing import Self

from nicegui import ui
from nicegui.elements.button import Button

from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.resources.resource_manager import (
    AddTracksKeys,
    ResourceManager,
)
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.button_form import ButtonForm


class AddTracksForm(ButtonForm):
    def __init__(
        self,
        view_model: ViewModel,
        resource_manager: ResourceManager,
    ) -> None:
        self._view_model = view_model
        self._resource_manager = resource_manager
        self._add_tracks_button: ui.button | None = None

        self.introduce_to_viewmodel()

    def introduce_to_viewmodel(self) -> None:
        self._view_model.set_tracks_frame(self)

    def build(self) -> Self:
        self._add_tracks_button = ui.button(
            self._resource_manager.get(AddTracksKeys.BUTTON_ADD_TRACKS),
            on_click=self._view_model.load_tracks,
        )
        return self

    def get_general_buttons(self) -> list[Button]:
        if self._add_tracks_button:
            return [self._add_tracks_button]
        return []
