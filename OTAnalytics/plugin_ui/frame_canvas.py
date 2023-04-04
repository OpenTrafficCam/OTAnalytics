import tkinter
from dataclasses import dataclass
from typing import Any, Optional

import customtkinter
from customtkinter import CTkCanvas, CTkCheckBox, CTkFrame
from PIL import Image, ImageTk

from OTAnalytics.application.application import OTAnalyticsApplication
from OTAnalytics.application.state import Observer, TrackViewState
from OTAnalytics.domain.track import TrackImage
from OTAnalytics.plugin_prototypes.track_visualization import track_viz
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


class FrameCanvas(CTkFrame, Observer[TrackImage]):
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
            self.track_image = image
            self.add_image(DisplayableImage(image))

    def add_image(self, image: DisplayableImage) -> None:
        self.canvas_background.add_image(image)

    def register_at(self, view_state: TrackViewState) -> None:
        view_state.background_image.register(self)

    def _show_tracks_command(self) -> None:
        # self.canvas_background.add_image(image)
        # self.
        if self._show_tracks:
            tracks = self._application._datastore._track_repository.get_all()
            sections = self._application._datastore._section_repository.get_all()
            tracked_image = track_viz.run(tracks, sections, self.track_image)
            self.add_image(DisplayableImage(tracked_image))
        # else:
        #     self.


class CanvasBackground(CTkCanvas):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._current_id = None

    def add_image(self, image: DisplayableImage) -> None:
        if self._current_id:
            self.delete(self._current_id)
        self.current_image = image.create_photo()
        self._current_id = self.create_image(
            0, 0, image=self.current_image, anchor=customtkinter.NW
        )
        self.config(width=image.width(), height=image.height())

    def show_rectangle(self) -> None:
        self.create_rectangle(10, 10, 70, 70)

    def on_click(self, event: Any) -> None:
        x = event.x
        y = event.y
        print(f"Canvas clicked at x={x} and y={y}")
