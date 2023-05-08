import tkinter
from dataclasses import dataclass
from typing import Any, Optional

from customtkinter import NW, CTkCheckBox, CTkFrame
from PIL import ImageTk

from OTAnalytics.adapter_ui.abstract_canvas import AbstractCanvas
from OTAnalytics.adapter_ui.abstract_frame_canvas import AbstractFrameCanvas
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.domain.track import TrackImage
from OTAnalytics.plugin_ui.customtkinter_gui.canvas_observer import (
    CanvasObserver,
    EventHandler,
)
from OTAnalytics.plugin_ui.customtkinter_gui.constants import PADX, STICKY


@dataclass
class DisplayableImage:
    _image: TrackImage

    def width(self) -> int:
        return self._image.width()

    def height(self) -> int:
        return self._image.height()

    def create_photo(self) -> ImageTk.PhotoImage:
        return ImageTk.PhotoImage(image=self._image.as_image())


class FrameCanvas(AbstractFrameCanvas, CTkFrame):
    def __init__(self, viewmodel: ViewModel, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._viewmodel = viewmodel
        self._show_tracks = tkinter.BooleanVar()
        self._get_widgets()
        self._place_widgets()
        self.introduce_to_viewmodel()

    def introduce_to_viewmodel(self) -> None:
        self._viewmodel.set_tracks_canvas(self)

    def _get_widgets(self) -> None:
        self.canvas_background = CanvasBackground(
            master=self, viewmodel=self._viewmodel
        )
        self.button_show_tracks = CTkCheckBox(
            master=self,
            text="Show tracks",
            command=self._update_show_tracks_state,
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

    def update_background(self, image: TrackImage) -> None:
        self.add_image(DisplayableImage(image), layer="background")

    def add_image(self, image: DisplayableImage, layer: str) -> None:
        self.canvas_background.add_image(image, layer)

    def remove_layer(self, layer: str) -> None:
        self.canvas_background.remove_layer(layer)

    def update_show_tracks(self, value: Optional[bool]) -> None:
        new_value = value or False
        self._show_tracks.set(new_value)

    def _update_show_tracks_state(self) -> None:
        new_value = self._show_tracks.get()
        self._viewmodel.update_show_tracks_state(new_value)


class CanvasBackground(AbstractCanvas):
    def __init__(self, viewmodel: ViewModel, **kwargs: Any):
        super().__init__(**kwargs)
        self._viewmodel = viewmodel
        self.event_handler = CanvasEventHandler(canvas=self)
        self.introduce_to_viewmodel()

        self._current_image: ImageTk.PhotoImage
        self._current_id: Any = None

    def add_image(self, image: DisplayableImage, layer: str) -> None:
        if self._current_id:
            self.delete(self._current_id)
        self._current_image = image.create_photo()
        self._draw()

    def _draw(self) -> None:
        self._current_id = self.create_image(0, 0, image=self._current_image, anchor=NW)
        self.config(
            width=self._current_image.width(), height=self._current_image.height()
        )
        self.config(highlightthickness=0)
        self._viewmodel.refresh_sections_on_gui()
        # self.master.master.update_idletasks()

    def introduce_to_viewmodel(self) -> None:
        self._viewmodel.set_canvas(self)


class CanvasEventHandler(EventHandler):
    def __init__(self, canvas: CanvasBackground):
        self._canvas = canvas
        self._observers: list[CanvasObserver] = []
        self._bind_events()

    def _bind_events(self) -> None:
        self._canvas.bind("<ButtonRelease-1>", self.on_left_mousebutton_up)
        self._canvas.bind("<ButtonRelease-2>", self.on_right_mousebutton_up)
        self._canvas.bind("<Motion>", self.on_mouse_motion)

    def attach_observer(self, observer: CanvasObserver) -> None:
        self._observers.append(observer)

    def detach_observer(self, observer: CanvasObserver) -> None:
        self._observers.remove(observer)

    def _notify_observers(self, coordinates: tuple[int, int], event_type: str) -> None:
        for observer in self._observers:
            observer.update(coordinates, event_type)

    def on_left_mousebutton_up(self, event: Any) -> None:
        coordinates = self._get_mouse_coordinates(event)
        self._notify_observers(coordinates, "left_mousebutton_up")

    def on_right_mousebutton_up(self, event: Any) -> None:
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
