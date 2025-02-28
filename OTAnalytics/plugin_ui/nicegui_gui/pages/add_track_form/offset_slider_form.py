from typing import Self

from nicegui import ui
from nicegui.elements.button import Button

from OTAnalytics.adapter_ui.abstract_frame_offset import AbstractFrameOffset
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.resources.resource_manager import (
    OffsetSliderKeys,
    ResourceManager,
)
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.button_form import ButtonForm


class OffSetSliderForm(AbstractFrameOffset, ButtonForm):
    def __init__(
        self,
        view_model: ViewModel,
        resource_manager: ResourceManager,
    ) -> None:
        self.update_offset_button: ui.button | None = None
        self.y_offset_slider: ui.slider | None = None
        self.x_offset_slider: ui.slider | None = None
        self._view_model = view_model
        self._resource_manager = resource_manager
        self.introduce_to_viewmodel()

    def introduce_to_viewmodel(self) -> None:
        self._view_model.set_offset_frame(self)

    def build(self) -> Self:
        with ui.grid(rows=2).style("width: 100%"):
            with ui.row(wrap=False):
                ui.label("X:")
                self.x_offset_slider = ui.slider(
                    min=0, max=1, value=0.5, step=0.1, on_change=self.on_offset_change
                )
            with ui.row(wrap=False):
                ui.label("Y:")
                self.y_offset_slider = ui.slider(
                    min=0, max=1, value=0.5, step=0.1, on_change=self.on_offset_change
                )
        self.update_offset_button = ui.button(
            self._resource_manager.get(OffsetSliderKeys.BUTTON_UPDATE_OFFSET),
            on_click=self._view_model.change_track_offset_to_section_offset,
        )
        return self

    def on_offset_change(self) -> None:
        if self.x_offset_slider and self.y_offset_slider:
            self._view_model.set_track_offset(
                self.x_offset_slider.value, self.y_offset_slider.value
            )

    def configure_offset_button(self, color: str, enable: bool) -> None:
        if self.update_offset_button:
            if enable:
                self.update_offset_button.enable()
            else:
                self.update_offset_button.disable()

    def update_offset(self, x: float, y: float) -> None:
        if self.y_offset_slider and self.x_offset_slider:
            self.y_offset_slider.value = y
            self.x_offset_slider.value = x
            self.y_offset_slider.update()
            self.x_offset_slider.update()

    def enable_update_offset_button(self, enabled: bool) -> None:
        if self.update_offset_button:
            if enabled:
                self.update_offset_button.enable()
            else:
                self.update_offset_button.disable()

    def set_offset_button_color(self, color: str) -> None:
        pass

    def get_default_offset_button_color(self) -> str:
        return ""

    def get_single_item_buttons(self) -> list[Button]:
        if self.update_offset_button:
            return [self.update_offset_button]
        return []
