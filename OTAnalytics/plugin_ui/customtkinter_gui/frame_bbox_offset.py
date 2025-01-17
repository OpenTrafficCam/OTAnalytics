from typing import Any, Callable

from customtkinter import CTkFrame, CTkLabel, CTkSlider

from OTAnalytics.domain import geometry
from OTAnalytics.plugin_ui.customtkinter_gui.constants import PADX

SLIDER_RESOLUTION = 0.1
DECIMAL_DIGITS = 1


class FrameBboxOffset(CTkFrame):
    def __init__(
        self,
        frame_heading: str,
        relative_offset_coordinates: dict,
        notify_change: Callable[[float, float], None] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._notify_change = notify_change
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
            from_=0,
            to=1,
            number_of_steps=1 / SLIDER_RESOLUTION,
            command=self._on_slider_change,
        )
        self.slider_x.bind("<ButtonRelease-1>", self._on_slider_release)
        self.slider_y = CTkSlider(
            master=self,
            from_=0,
            to=1,
            number_of_steps=10,
            command=self._on_slider_change,
        )
        self.slider_y.bind("<ButtonRelease-1>", self._on_slider_release)

    def _place_widgets(self) -> None:
        self.label.grid(row=0, column=0, columnspan=3, padx=PADX, sticky="EW")
        self.label_x.grid(row=1, column=0, padx=PADX, sticky="E")
        self.label_y.grid(row=2, column=0, padx=PADX, sticky="E")
        self.slider_x.grid(row=1, column=1, padx=PADX, sticky="EW")
        self.slider_y.grid(row=2, column=1, padx=PADX, sticky="EW")
        self.label_x_value.grid(row=1, column=2, padx=PADX, sticky="W")
        self.label_y_value.grid(row=2, column=2, padx=PADX, sticky="W")

    def _set_initial_values(self) -> None:
        self.slider_x.set(self._relative_offset_coordinates["x"])
        self.slider_y.set(self._relative_offset_coordinates["y"])
        self.label_x_value.configure(text=self._relative_offset_coordinates["x"])
        self.label_y_value.configure(text=self._relative_offset_coordinates["y"])

    def set_relative_offset_coordintes(self, x: float, y: float) -> None:
        self.slider_x.set(x)
        self.slider_y.set(y)
        self.label_x_value.configure(text=str(x))
        self.label_y_value.configure(text=str(y))

    def get_relative_offset_coordintes(self) -> dict:
        x = round(self.slider_x.get(), DECIMAL_DIGITS)
        y = round(self.slider_y.get(), DECIMAL_DIGITS)
        return {geometry.X: x, geometry.Y: y}

    def _on_slider_change(self, value: Any) -> None:
        x, y = self._get_slider_values()
        self.label_x_value.configure(text=round(x, DECIMAL_DIGITS))
        self.label_y_value.configure(text=round(y, DECIMAL_DIGITS))

    def _on_slider_release(self, value: Any) -> None:
        x, y = self._get_slider_values()
        if self._notify_change is not None:
            self._notify_change(round(x, DECIMAL_DIGITS), round(y, DECIMAL_DIGITS))

    def _get_slider_values(self) -> tuple[float, float]:
        x = self.slider_x.get()
        y = self.slider_y.get()
        return x, y
