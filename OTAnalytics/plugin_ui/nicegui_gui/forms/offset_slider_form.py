from typing import Callable

from nicegui import ui

from OTAnalytics.application.resources.resource_manager import (
    OffsetSliderKeys,
    ResourceManager,
)
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate

MARKER_OFFSET_POINT = "marker-offset-point"
MARKER_OFFSET_X_VALUE = "marker-offset-x-value"
MARKER_OFFSET_Y_VALUE = "marker-offset-y-value"


def to_percent(value: float) -> str:
    return f"{round(value * 100, 2):g}%"


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
        self._point: ui.element | None = None
        self._x_value: ui.label | None = None
        self._y_value: ui.label | None = None

    def build(self) -> None:
        # The bounding box of a detection with the point at which tracks are drawn
        with ui.element("div").classes("ota-offset-box"):
            self._point = ui.element("div").classes("ota-offset-point")
            self._point.mark(MARKER_OFFSET_POINT)
        with ui.grid(rows=2).classes("w-full"):
            with ui.row(wrap=False).classes("ota-offset-row"):
                ui.label(
                    self._resource_manager.get(OffsetSliderKeys.LABEL_COORDINATE_X)
                )
                self.x_offset_slider = ui.slider(
                    min=0, max=1, value=self._initial_offset.x, step=0.1
                )
                self._x_value = ui.label().classes("ota-offset-value ota-num")
                self._x_value.mark(MARKER_OFFSET_X_VALUE)
            with ui.row(wrap=False).classes("ota-offset-row"):
                ui.label(
                    self._resource_manager.get(OffsetSliderKeys.LABEL_COORDINATE_Y)
                )
                self.y_offset_slider = ui.slider(
                    min=0, max=1, value=self._initial_offset.y, step=0.1
                )
                self._y_value = ui.label().classes("ota-offset-value ota-num")
                self._y_value.mark(MARKER_OFFSET_Y_VALUE)
            self.x_offset_slider.on_value_change(self._show_offset)
            self.y_offset_slider.on_value_change(self._show_offset)
            if self.on_offset_change is not None:
                self.x_offset_slider.on_value_change(self.on_offset_change)
                self.y_offset_slider.on_value_change(self.on_offset_change)
        self._show_offset()

    def _show_offset(self) -> None:
        """Move the point to the offset and show its coordinates."""
        offset = self.offset
        if self._point is not None:
            self._point.style(
                f"left: {to_percent(offset.x)}; top: {to_percent(offset.y)}"
            )
        if self._x_value is not None:
            self._x_value.set_text(f"{offset.x:.2f}")
        if self._y_value is not None:
            self._y_value.set_text(f"{offset.y:.2f}")

    def set_offset(self, offset: RelativeOffsetCoordinate) -> None:
        if self.y_offset_slider and self.x_offset_slider:
            self.y_offset_slider.value = offset.y
            self.x_offset_slider.value = offset.x
            self.y_offset_slider.update()
            self.x_offset_slider.update()
