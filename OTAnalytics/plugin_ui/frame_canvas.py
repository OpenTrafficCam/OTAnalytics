from typing import Any

import customtkinter
import numpy as np
from customtkinter import CTkCanvas, CTkFrame
from moviepy.editor import VideoFileClip
from PIL import Image, ImageTk

from OTAnalytics.plugin_ui.constants import PADX, STICKY


class FrameCanvas(CTkFrame):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._get_widgets()
        self._place_widgets()

    def _get_widgets(self) -> None:
        self.canvas_background = CanvasBackground(master=self)

    def _place_widgets(self) -> None:
        PADY = 10
        self.canvas_background.grid(
            row=0, column=0, padx=PADX, pady=PADY, sticky=STICKY
        )


class CanvasBackground(CTkCanvas):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.bind("<ButtonRelease-1>", self.on_click)

        # This calls should come from outside later
        video = VideoFileClip(
            r"tests/data/Testvideo_Cars-Cyclist_FR20_2020-01-01_00-00-00.mp4"
        )
        image = video.get_frame(0)
        self.show_rectangle()
        self.show_image(image=image)

    def show_image(self, image: np.ndarray) -> None:
        pillow_image = Image.fromarray(image)
        width, height = pillow_image.size
        self.config(width=width, height=height)
        pillow_photo_image = ImageTk.PhotoImage(image=pillow_image)
        print(pillow_photo_image)
        self.create_image(0, 0, image=pillow_photo_image, anchor=customtkinter.NW)

    def show_rectangle(self) -> None:
        self.create_rectangle(10, 10, 70, 70)

    def on_click(self, event: Any) -> None:
        x = event.x
        y = event.y
        print(f"Canvas clicked at x={x} and y={y}")
