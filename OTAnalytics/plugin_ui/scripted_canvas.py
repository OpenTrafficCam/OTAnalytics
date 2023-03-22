from typing import Any

import customtkinter
from customtkinter import CTk, CTkCanvas, CTkFrame
from moviepy.editor import VideoFileClip
from PIL import Image, ImageTk


class DummyImage:
    def load_image(self) -> Any:
        video = VideoFileClip(
            r"tests/data/Testvideo_Cars-Cyclist_FR20_2020-01-01_00-00-00.mp4"
        )
        image = video.get_frame(0)
        return image

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


class DummyCanvas(CTkCanvas):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

    def add_image(self, dummy_image: DummyImage) -> None:
        self.create_image(
            0, 0, image=dummy_image.create_photo(), anchor=customtkinter.NW
        )
        self.config(width=dummy_image.width(), height=dummy_image.height())


class DummyFrame(CTkFrame):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.canvas = DummyCanvas(master=self.master)

    def add_image(self, dummy_image: DummyImage) -> None:
        self.canvas.add_image(dummy_image)
        PADX = 10
        PADY = 5
        STICKY = "NESW"
        self.canvas.grid(row=0, column=0, padx=PADX, pady=PADY, sticky=STICKY)


class Dummy:
    def __init__(self) -> None:
        self.app = CTk()

    def run(self) -> None:
        dummy_image = DummyImage()
        dummy_frame = DummyFrame(master=self.app)
        dummy_frame.add_image(dummy_image)
        self.app.mainloop()


Dummy().run()
