import tkinter
from typing import Any, Sequence

from customtkinter import CTkCheckBox, CTkFrame, CTkLabel, ThemeManager

from OTAnalytics.application.plotting import Layer
from OTAnalytics.plugin_ui.customtkinter_gui.constants import PADX, STICKY
from OTAnalytics.plugin_ui.customtkinter_gui.style import STICKY_WEST

DEFAULT_COLOR = ThemeManager.theme["CTkFrame"]["fg_color"]


class FrameTrackPlotting(CTkFrame):
    def __init__(self, layers: Sequence[Layer], **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._layers = layers
        self.get_widgets()

    def get_widgets(self) -> None:
        PADY = 10
        for idx, layer in enumerate(self._layers):
            checkbox_layer = CheckBoxLayer(master=self, layer=layer)
            checkbox_layer.grid(
                row=idx, column=0, padx=PADX, pady=(0, PADY), sticky=STICKY
            )


class CheckBoxLayer(CTkFrame):
    def __init__(self, layer: Layer, **kwargs: Any) -> None:
        super().__init__(fg_color=DEFAULT_COLOR, **kwargs)
        self._enabled = tkinter.BooleanVar()
        self._layer = layer
        self._enabled.set(self._layer.is_enabled())
        self.get_widgets()

    def get_widgets(self) -> None:
        self._label = CTkLabel(
            master=self, text=self._layer.get_name(), bg_color=DEFAULT_COLOR
        )
        self._checkbox = CTkCheckBox(
            master=self,
            text="",
            command=self._on_checkbox_clicked,
            variable=self._enabled,
            onvalue=True,
            offvalue=False,
            bg_color=DEFAULT_COLOR,
            width=5,
        )
        self._checkbox.grid(row=0, column=0, padx=0, pady=0, sticky=STICKY_WEST)
        self._label.grid(row=0, column=1, padx=0, pady=0, sticky=STICKY_WEST)

    def _on_checkbox_clicked(self) -> None:
        self._layer.set_enabled(self._enabled.get())
