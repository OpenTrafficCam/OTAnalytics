from dataclasses import dataclass
from pathlib import Path
from typing import Any

import customtkinter
from customtkinter import CTkFrame
from moviepy.editor import VideoFileClip
from PIL import Image, ImageTk

from OTAnalytics.plugin_ui.abstract_canvas import AbstractCanvas
from OTAnalytics.plugin_ui.canvas_observer import CanvasObserver, EventHandler
from OTAnalytics.plugin_ui.constants import PADX, STICKY
from OTAnalytics.plugin_ui.view_model import ViewModel


@dataclass
class TrackImage:
    path: Path

    def load_image(self) -> Any:
        video = VideoFileClip(str(self.path))
        return video.get_frame(0)

    def width(self) -> int:
        return self.pillow_image.width

    def height(self) -> int:
        return self.pillow_image.height

    def convert_image(self) -> None:
        self.pillow_image = Image.fromarray(self.load_image())

    def create_photo(self) -> ImageTk.PhotoImage:
        self.convert_image()
        self.pillow_photo_image = ImageTk.PhotoImage(image=self.pillow_image)
        return self.pillow_photo_image


class FrameCanvas(CTkFrame):
    def __init__(self, viewmodel: ViewModel, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._viewmodel = viewmodel
        self._get_widgets()
        self._place_widgets()

    def _get_widgets(self) -> None:
        self.canvas_background = CanvasBackground(
            master=self, viewmodel=self._viewmodel
        )

    def _place_widgets(self) -> None:
        PADY = 10
        self.canvas_background.grid(
            row=0, column=0, padx=PADX, pady=PADY, sticky=STICKY
        )

    def add_image(self, image: TrackImage) -> None:
        self.canvas_background.add_image(image)
        PADX = 10
        PADY = 5
        STICKY = "NESW"
        self.canvas_background.grid(
            row=0, column=0, padx=PADX, pady=PADY, sticky=STICKY
        )


class CanvasBackground(AbstractCanvas):
    def __init__(self, viewmodel: ViewModel, **kwargs: Any):
        super().__init__(**kwargs)
        self._viewmodel = viewmodel
        self.event_handler = CanvasEventHandler(canvas=self)
        self.introduce_to_viewmodel()

    # @property
    # def event_handler(self) -> EventHandler:
    #     return self.event_handler

    # @event_handler.setter
    # def event_handler(self, value: EventHandler) -> None:
    #     self.event_handler = value

    def add_image(self, image: TrackImage) -> None:
        self.create_image(0, 0, image=image.create_photo(), anchor=customtkinter.NW)
        self.config(width=image.width(), height=image.height())
        self.config(highlightthickness=0)
        # self.master.master.update_idletasks()

    def introduce_to_viewmodel(self) -> None:
        self._viewmodel.set_canvas(self)


class CanvasEventHandler(EventHandler):
    def __init__(self, canvas: CanvasBackground):
        self._canvas = canvas
        self._observers: list[CanvasObserver] = []
        self._bind_events()

    def _bind_events(self) -> None:
        self._canvas.bind("<ButtonRelease-1>", self.left_mousebutton_up)
        self._canvas.bind("<ButtonRelease-2>", self.right_mousebutton_up)
        self._canvas.bind("<Motion>", self.on_mouse_motion)

    def attach_observer(self, observer: CanvasObserver) -> None:
        self._observers.append(observer)

    def detach_observer(self, observer: CanvasObserver) -> None:
        self._observers.remove(observer)

    def _notify_observers(self, coordinates: tuple[int, int], event_type: str) -> None:
        for observer in self._observers:
            observer.update(coordinates, event_type)

    def left_mousebutton_up(self, event: Any) -> None:
        coordinates = self._get_mouse_coordinates(event)
        self._notify_observers(coordinates, "left_mousebutton_up")

    def right_mousebutton_up(self, event: Any) -> None:
        coordinates = self._get_mouse_coordinates(event)
        self._notify_observers(coordinates, "right_mousebutton_up")

    def on_mouse_motion(self, event: Any) -> None:
        coordinates = self._get_mouse_coordinates(event)
        self._notify_observers(coordinates, "mouse_motion")

    def _get_mouse_coordinates(self, event: Any) -> tuple[int, int]:
        """Returns coordinates of event on canvas taking into account the horizontal and
        vertical scroll factors ("xscroll" and "yscroll") in case the canvas is zoomed
        and scrolled.

        Args:
            event (Any): Event on canvas

        Returns:
            tuple[int, int]: Coordinates of the event
        """
        x = int(self._canvas.canvasx(event.x))
        y = int(self._canvas.canvasy(event.y))
        return x, y
