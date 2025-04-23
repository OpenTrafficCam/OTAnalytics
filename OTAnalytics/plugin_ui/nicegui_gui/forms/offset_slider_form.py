from typing import Callable

from nicegui import ui

from OTAnalytics.application.resources.resource_manager import (
    OffsetSliderKeys,
    ResourceManager,
)
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate


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
        initial_offset: RelativeOffsetCoordinate = RelativeOffsetCoordinate(0.5, 0.5),
        on_offset_change: Callable[[], None] | None = None,
    ) -> None:
        self._resource_manager = resource_manager
        self.on_offset_change = on_offset_change
        self._initial_offset = initial_offset
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
