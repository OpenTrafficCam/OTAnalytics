from typing import Callable, Self

from nicegui import ui
from nicegui.elements.button import Button

from OTAnalytics.adapter_ui.abstract_frame_offset import AbstractFrameOffset
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.resources.resource_manager import (
    OffsetSliderKeys,
    ResourceManager,
    VisualizationOffsetSliderKeys,
)
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.button_form import ButtonForm


class OffsetSliderForm:
    @property
    def offset(self) -> RelativeOffsetCoordinate:
        if self.x_offset_slider is None or self.y_offset_slider is None:
            return self._initial_offset
        return RelativeOffsetCoordinate(
            x=self.x_offset_slider.value, y=self.y_offset_slider.value
        )

    def __init__(
        self,
        resource_manager: ResourceManager,
        on_offset_change: Callable[[], None] | None = None,
    ) -> None:
        self._resource_manager = resource_manager
        self.on_offset_change = on_offset_change
        self._initial_offset = RelativeOffsetCoordinate(0.5, 0.5)
        self.y_offset_slider: ui.slider | None = None
        self.x_offset_slider: ui.slider | None = None

    def build(self) -> None:
        with ui.grid(rows=2).style("width: 100%"):
            with ui.row(wrap=False):
                ui.label(
                    self._resource_manager.get(OffsetSliderKeys.LABEL_COORDINATE_X)
                )
                self.x_offset_slider = ui.slider(
                    min=0, max=1, value=self._initial_offset.x, step=0.1
                )
            with ui.row(wrap=False):
                ui.label(
                    self._resource_manager.get(OffsetSliderKeys.LABEL_COORDINATE_Y)
                )
                self.y_offset_slider = ui.slider(
                    min=0, max=1, value=self._initial_offset.y, step=0.1
                )
            if self.on_offset_change is not None:
                self.x_offset_slider.on_value_change(self.on_offset_change)
                self.y_offset_slider.on_value_change(self.on_offset_change)

    def set_offset(self, offset: RelativeOffsetCoordinate) -> None:
        if self.y_offset_slider and self.x_offset_slider:
            self.y_offset_slider.value = offset.y
            self.x_offset_slider.value = offset.x
            self.y_offset_slider.update()
            self.x_offset_slider.update()


class VisualizationOffSetSliderForm(AbstractFrameOffset, ButtonForm):
    def __init__(
        self,
        view_model: ViewModel,
        resource_manager: ResourceManager,
    ) -> None:
        self._view_model = view_model
        self._resource_manager = resource_manager
        self._offset_slider_form = OffsetSliderForm(
            resource_manager, on_offset_change=self.on_offset_change
        )
        self.update_offset_button: ui.button | None = None
        self.introduce_to_viewmodel()

    def introduce_to_viewmodel(self) -> None:
        self._view_model.set_offset_frame(self)

    def build(self) -> Self:
        self._offset_slider_form.build()
        self.update_offset_button = ui.button(
            self._resource_manager.get(
                VisualizationOffsetSliderKeys.BUTTON_UPDATE_OFFSET
            ),
            on_click=self._view_model.change_track_offset_to_section_offset,
        )
        return self

    def on_offset_change(self) -> None:
        if self._offset_slider_form.offset:
            self._view_model.set_track_offset(
                self._offset_slider_form.offset.x, self._offset_slider_form.offset.y
            )

    def configure_offset_button(self, color: str, enable: bool) -> None:
        if self.update_offset_button:
            if enable:
                self.update_offset_button.enable()
            else:
                self.update_offset_button.disable()

    def update_offset(self, x: float, y: float) -> None:
        if self._offset_slider_form:
            self._offset_slider_form.set_offset(RelativeOffsetCoordinate(x, y))

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
