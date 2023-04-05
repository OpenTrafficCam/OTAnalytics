import tkinter
from dataclasses import dataclass
from typing import Any, Optional

import customtkinter
from customtkinter import CTkCanvas, CTkCheckBox, CTkFrame
from PIL import ImageTk

from OTAnalytics.application.application import OTAnalyticsApplication
from OTAnalytics.application.state import TrackViewState
from OTAnalytics.domain.track import TrackImage
from OTAnalytics.plugin_ui.constants import PADX, STICKY


@dataclass
class DisplayableImage:
    _image: TrackImage

    def width(self) -> int:
        return self._image.width()

    def height(self) -> int:
        return self._image.height()

    def create_photo(self) -> ImageTk.PhotoImage:
        return ImageTk.PhotoImage(image=self._image.as_image())


class FrameCanvas(CTkFrame):
    def __init__(self, application: OTAnalyticsApplication, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._application = application
        self._show_tracks = tkinter.BooleanVar()
        self._get_widgets()
        self._place_widgets()

    def _get_widgets(self) -> None:
        self.canvas_background = CanvasBackground(master=self)
        self.button_show_tracks = CTkCheckBox(
            master=self,
            text="Show tracks",
            command=self._show_tracks_command,
            variable=self._show_tracks,
            onvalue=True,
            offvalue=False,
        )

    def _place_widgets(self) -> None:
        PADY = 10
        self.canvas_background.grid(
            row=1, column=0, padx=PADX, pady=PADY, sticky=STICKY
        )
        self.button_show_tracks.grid(
            row=0, column=0, padx=PADX, pady=PADY, sticky=STICKY
        )

    def notify(self, image: Optional[TrackImage]) -> None:
        if image:
            self._image = image
            self.add_image(DisplayableImage(self._image), layer="background")

    def add_image(self, image: DisplayableImage, layer: str) -> None:
        self.canvas_background.add_image(image, layer)

    def remove_layer(self, layer: str) -> None:
        self.canvas_background.remove_layer(layer)

    def register_at(self, view_state: TrackViewState) -> None:
        self._view_state = view_state
        view_state.background_image.register(self.notify)
        view_state.show_tracks.register(self._update_show_tracks)

    def _update_show_tracks(self, value: Optional[bool]) -> None:
        new_value = value or False
        self._show_tracks.set(new_value)

    def _show_tracks_command(self) -> None:
        self._view_state.show_tracks.set(self._show_tracks.get())


class CanvasBackground(CTkCanvas):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._current_image: ImageTk.PhotoImage
        self._current_id: Any = None

    def add_image(self, image: DisplayableImage, layer: str) -> None:
        if self._current_id:
            self.delete(self._current_id)
        self._current_image = image.create_photo()
        self._draw()

    def _draw(self) -> None:
        self._current_id = self.create_image(
            0, 0, image=self._current_image, anchor=customtkinter.NW
        )
        self.config(
            width=self._current_image.width(), height=self._current_image.height()
        )

    def show_rectangle(self) -> None:
        self.create_rectangle(10, 10, 70, 70)

    def on_click(self, event: Any) -> None:
        x = event.x
        y = event.y
        print(f"Canvas clicked at x={x} and y={y}")
