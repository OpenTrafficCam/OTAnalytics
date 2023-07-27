from typing import Any

from customtkinter import CTkFrame, CTkLabel, CTkSlider

from OTAnalytics.domain import geometry
from OTAnalytics.plugin_ui.customtkinter_gui.constants import PADX


class FrameBboxOffset(CTkFrame):
    def __init__(
        self,
        frame_heading: str,
        relative_offset_coordinates: dict,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._relative_offset_coordinates = relative_offset_coordinates
        self._frame_heading = frame_heading
        self._get_widgets()
        self._place_widgets()
        self._set_initial_values()

    def _get_widgets(self) -> None:
        self.label = CTkLabel(master=self, text=self._frame_heading)
        self.label_x = CTkLabel(master=self, text="X:")
        self.label_y = CTkLabel(master=self, text="Y:")
        self.label_x_value = CTkLabel(master=self, width=20)
        self.label_y_value = CTkLabel(master=self, width=20)
        self.slider_x = CTkSlider(
            master=self,
            width=110,
            from_=0,
            to=1,
            number_of_steps=10,
            command=lambda value: self.label_x_value.configure(text=round(value, 1)),
        )
        self.slider_y = CTkSlider(
            master=self,
            width=110,
            from_=0,
            to=1,
            number_of_steps=10,
            command=lambda value: self.label_y_value.configure(text=round(value, 1)),
        )

    def _place_widgets(self) -> None:
        self.label.grid(row=0, column=0, columnspan=2, padx=PADX, sticky="E")
        self.label_x.grid(row=1, column=0, padx=PADX, sticky="E")
        self.label_y.grid(row=2, column=0, padx=PADX, sticky="E")
        self.slider_x.grid(row=1, column=1, padx=PADX, sticky="EW")
        self.slider_y.grid(row=2, column=1, padx=PADX, sticky="EW")
        self.label_x_value.grid(row=1, column=3, padx=PADX, sticky="W")
        self.label_y_value.grid(row=2, column=3, padx=PADX, sticky="W")

    def _set_initial_values(self) -> None:
        self.slider_x.set(self._relative_offset_coordinates["x"])
        self.slider_y.set(self._relative_offset_coordinates["y"])
        self.label_x_value.configure(text=self._relative_offset_coordinates["x"])
        self.label_y_value.configure(text=self._relative_offset_coordinates["y"])

    def set_relative_offset_coordintes(self, x: float, y: float) -> None:
        self.slider_x.set(x)
        self.slider_y.set(y)

    def get_relative_offset_coordintes(self) -> dict:
        x = round(self.slider_x.get(), 2)
        y = round(self.slider_y.get(), 2)
        return {geometry.X: x, geometry.Y: y}
