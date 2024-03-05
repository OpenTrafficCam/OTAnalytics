import tkinter
from typing import Any, Sequence

from customtkinter import CTkButton, CTkCheckBox, CTkLabel

from OTAnalytics.adapter_ui.abstract_frame_track_plotting import (
    AbstractFrameTrackPlotting,
)
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.logger import logger
from OTAnalytics.application.plotting import Layer, LayerGroup
from OTAnalytics.plugin_ui.customtkinter_gui.constants import PADX, STICKY
from OTAnalytics.plugin_ui.customtkinter_gui.custom_containers import EmbeddedCTkFrame
from OTAnalytics.plugin_ui.customtkinter_gui.style import STICKY_WEST


class FrameTrackPlotting(AbstractFrameTrackPlotting, EmbeddedCTkFrame):
    def __init__(
        self, viewmodel: ViewModel, layers: Sequence[LayerGroup], **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self._view_model = viewmodel
        self._layers = layers
        self._get_widgets()
        self._place_widgets()
        self.introduce_to_viewmodel()

    def _get_widgets(self) -> None:
        self._button_update_highlight_flows = CTkButton(
            master=self,
            text="Update Flow Highlighting",
            command=self._create_events,
        )

    def _place_widgets(self) -> None:
        pady = 10
        row = 0
        for group in self._layers:
            label = CTkLabel(master=self, text=group.name)
            label.grid(row=row, column=0, padx=PADX, pady=(0, pady), sticky=STICKY_WEST)
            row += 1
            for layer in group.layers:
                checkbox_layer = CheckBoxLayer(master=self, layer=layer)
                checkbox_layer.grid(
                    row=row, column=0, padx=PADX, pady=(0, pady), sticky=STICKY
                )
                row += 1
        self._button_update_highlight_flows.grid(
            row=row,
            column=0,
            padx=PADX,
            pady=(0, pady),
            sticky=STICKY,
        )

    def _create_events(self) -> None:
        logger().info("Creating events")
        self._view_model.create_events()

    def introduce_to_viewmodel(self) -> None:
        self._view_model.set_frame_track_plotting(self)

    def reset_layers(self) -> None:
        for layer in self._layers:
            layer.reset()


class CheckBoxLayer(EmbeddedCTkFrame):
    def __init__(self, layer: Layer, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._enabled = tkinter.BooleanVar()
        self._layer = layer
        self._enabled.set(self._layer.is_enabled())
        layer.register(self._on_layer_state_changed)
        self._get_widgets()

    def _get_widgets(self) -> None:
        self._label = CTkLabel(master=self, text=self._layer.get_name())
        self._checkbox = CTkCheckBox(
            master=self,
            text="",
            command=self._on_checkbox_clicked,
            variable=self._enabled,
            onvalue=True,
            offvalue=False,
            width=5,
        )
        self._checkbox.grid(row=0, column=0, padx=0, pady=0, sticky=STICKY_WEST)
        self._label.grid(row=0, column=1, padx=0, pady=0, sticky=STICKY_WEST)

    def _on_checkbox_clicked(self) -> None:
        self._layer.set_enabled(self._enabled.get())

    def _on_layer_state_changed(self, enabled: bool) -> None:
        self._enabled.set(enabled)
