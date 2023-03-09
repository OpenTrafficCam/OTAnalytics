import tkinter
from pathlib import Path
from tkinter.filedialog import askopenfilename
from typing import Any

import customtkinter
from customtkinter import CTk, CTkButton, CTkCanvas, CTkFrame
from PIL import Image, ImageTk

from OTAnalytics.application.datastore import Datastore
from OTAnalytics.plugin_parser.otvision_parser import OttrkParser


class ButtonLoadTracks(CTkButton):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.bind("<ButtonRelease-1>", self.on_click)

    def on_click(self, events: Any) -> None:
        self.tracks_file = askopenfilename(
            title="Load tracks file", filetypes=[("tracks file", "*.ottrk")]
        )
        print(f"Tracks file: {self.tracks_file}")


class CanvasBackground(CTkCanvas):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.bind("<ButtonRelease-1>", self.on_click)

        # This call should come from outside later
        self.show_image(image=Image.open(r"OTAnalytics/plugin_ui/test_image.png"))
        self.show_rectangle()

    def show_image(self, image: Image.Image) -> None:
        width, height = image.size
        self.config(width=width, height=height, bg="black")
        photo_image = ImageTk.PhotoImage(image=image)
        print(photo_image)
        self.create_image(0, 0, image=photo_image, anchor=tkinter.NW)

    def show_rectangle(self) -> None:
        self.create_rectangle(10, 10, 70, 70)

    def on_click(self, event: Any) -> None:
        x = event.x
        y = event.y
        print(f"Canvas clicked at x={x} and y={y}")


class FrameFiles(CTkFrame):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.layout()

    def layout(self) -> None:
        self.button_load_tracks = ButtonLoadTracks(
            master=self,
            text="Load tracks",
        )
        self.button_load_tracks.pack()


class OTAnalyticsApplication:
    def __init__(self) -> None:
        self.datastore: Datastore
        self.app: CTk

    def layout(self) -> None:
        self.frame_files = FrameFiles(master=self.app)
        self.frame_files.pack()
        self.canvas_background = CanvasBackground(master=self.app)
        self.canvas_background.pack()

    def add_track_of_file(self) -> None:
        track_file = Path("")  # TODO read from file chooser
        self.datastore.load_track_file(file=track_file)

    def start(self) -> None:
        self.setup_application()
        self.show_gui()

    def setup_application(self) -> None:
        """
        Build all required objects and inject them where necessary
        """
        track_parser = OttrkParser()
        self.datastore = Datastore(track_parser)

    def show_gui(self) -> None:
        customtkinter.set_appearance_mode("System")
        customtkinter.set_default_color_theme("green")

        self.app = CTk()
        self.app.geometry("800x600")

        # self.add_track_loader()

        self.layout()

        self.app.mainloop()

    def add_track_loader(self) -> None:
        button = CTkButton(
            master=self.app,
            text="Read tracks",
            command=self.add_track_of_file,
        )
        button.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
