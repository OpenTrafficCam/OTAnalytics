from dataclasses import dataclass
from typing import Any, Optional

import customtkinter
from customtkinter import CTkCanvas, CTkFrame
from PIL import Image, ImageTk

from OTAnalytics.application.application import OTAnalyticsApplication
from OTAnalytics.domain.track import TrackId, TrackImage, TrackObserver
from OTAnalytics.plugin_ui.constants import PADX, STICKY


@dataclass
class DisplayableImage:
    image: TrackImage

    def width(self) -> int:
        return self.pillow_image.width

    def height(self) -> int:
        return self.pillow_image.height

    def convert_image(self) -> None:
        self.pillow_image = Image.fromarray(self.image.as_array())

    def create_photo(self) -> ImageTk.PhotoImage:
        self.convert_image()
        self.pillow_photo_image = ImageTk.PhotoImage(image=self.pillow_image)
        return self.pillow_photo_image


class FrameCanvas(CTkFrame, TrackObserver):
    def __init__(self, application: OTAnalyticsApplication, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._application = application
        self._get_widgets()
        self._place_widgets()

    def _get_widgets(self) -> None:
        self.canvas_background = CanvasBackground(master=self)

    def _place_widgets(self) -> None:
        PADY = 10
        self.canvas_background.grid(
            row=0, column=0, padx=PADX, pady=PADY, sticky=STICKY
        )

    def notify_track(self, track_id: Optional[TrackId]) -> None:
        if track_id:
            if image := self._application.get_image_of_track(track_id):
                self.add_image(DisplayableImage(image))

    def add_image(self, image: DisplayableImage) -> None:
        self.canvas_background.add_image(image)


class CanvasBackground(CTkCanvas):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

    def add_image(self, image: DisplayableImage) -> None:
        self.viewable_image = image.create_photo()
        self.create_image(0, 0, image=self.viewable_image, anchor=customtkinter.NW)
        self.config(width=image.width(), height=image.height())

    def show_rectangle(self) -> None:
        self.create_rectangle(10, 10, 70, 70)

    def on_click(self, event: Any) -> None:
        x = event.x
        y = event.y
        print(f"Canvas clicked at x={x} and y={y}")
