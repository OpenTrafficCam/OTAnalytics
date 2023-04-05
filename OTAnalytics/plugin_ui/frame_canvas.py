import tkinter
from dataclasses import dataclass
from typing import Any, Optional

import customtkinter
from customtkinter import CTkCanvas, CTkCheckBox, CTkFrame
from PIL import Image, ImageTk

from OTAnalytics.application.application import OTAnalyticsApplication
from OTAnalytics.application.state import TrackViewState
from OTAnalytics.domain.track import TrackImage
from OTAnalytics.plugin_ui.constants import PADX, STICKY


@dataclass
class DisplayableImage:
    image: TrackImage

    def width(self) -> int:
        return self.pillow_image.width

    def height(self) -> int:
        return self.pillow_image.height

    def create_pillow_image(self) -> Image.Image:
        self.pillow_image = self.image.as_image()
        return self.pillow_image

    def create_photo(self) -> ImageTk.PhotoImage:
        self.pillow_photo_image = ImageTk.PhotoImage(image=self.create_pillow_image())
        return self.pillow_photo_image


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
        self._layers: dict[str, Image.Image] = {}
        self._current_id: Any = None

    def add_image(self, image: DisplayableImage, layer: str) -> None:
        if self._current_id:
            self.delete(self._current_id)
        self._layers[layer] = image.create_pillow_image()
        self._draw()

    def _draw(self) -> None:
        self._current_image = self._build_image()
        self._current_id = self.create_image(
            0, 0, image=self._current_image, anchor=customtkinter.NW
        )
        self.config(
            width=self._current_image.width(), height=self._current_image.height()
        )

    def _build_image(self) -> ImageTk.PhotoImage:
        if "track" in self._layers.keys():
            background = self._layers["background"]
            tracks = self._layers["track"]
            return ImageTk.PhotoImage(Image.alpha_composite(background, tracks))
        return ImageTk.PhotoImage(self._layers["background"])

    def remove_layer(self, layer: str) -> None:
        if layer in self._layers.keys():
            del self._layers[layer]
        self._draw()

    def show_rectangle(self) -> None:
        self.create_rectangle(10, 10, 70, 70)

    def on_click(self, event: Any) -> None:
        x = event.x
        y = event.y
        print(f"Canvas clicked at x={x} and y={y}")
