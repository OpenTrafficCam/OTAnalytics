import tkinter as tk
import config
from gui_helper import button_bool
import image_alteration
import sections


class OtcCanvas(tk.Canvas):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.bind("<ButtonPress-2>")
        self.bind("<ButtonPress-3>")

        # self.linepoints = [(0, 0), (0, 0)]
        self.points = [(0, 0), (0, 0)]
        self.polygon_points = []

        self.bind(
            "<B1-Motion>",
            lambda event: [
                self.click_receive_coordinates(event, 1),
                sections.draw_line(
                    event,
                ),
            ],
        )

        self.bind(
            "<ButtonPress-1>",
            lambda event: [
                self.click_receive_coordinates(event, 0),
                sections.draw_polygon(
                    event,
                    adding_points=True,
                ),
            ],
        )
        self.bind(
            "<ButtonPress-2>",
            lambda event: [
                sections.draw_polygon(
                    event,
                    undo=True,
                )
            ],
        )

        self.bind(
            "<ButtonPress-3>",
            lambda event: [
                sections.draw_polygon(
                    event,
                    closing=True,
                )
            ],
        )

    def delete_polygon_points(self):
        """delete list of polygon points after scrolling, sliding, playing, rewinding"""
        if self.polygon_points:
            self.polygon_points = []

    def click_receive_coordinates(self, event, list_index):
        """Saves coordinates from canvas event to linepoint list.

        Args:
            event (tkinter.event): Click on canvas triggers event.
            list_index (index):
        """
        #  uses mouseevents to get coordinates (left button)
        self.coordinateX = int(self.canvasx(event.x))
        self.coordinateY = int(self.canvasy(event.y))

        self.points[list_index] = (
            self.coordinateX,
            self.coordinateY,
        )

        print(self.points)

    def delete_polygon_points(self):
        """delete list of polygon points after scrolling, sliding, playing, rewinding"""
        if self.polygon_points:
            self.polygon_points = []


class CanvasFrame(tk.Frame):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.frame_canvas = tk.Frame(master=self)
        self.frame_canvas.pack(fill="x")

        config.maincanvas = OtcCanvas(master=self.frame_canvas, width=0, height=0)
        config.maincanvas.pack()

        config.sliderobject = SliderFrame(master=self.frame_canvas)
        config.sliderobject.pack(fill="x")


class SliderFrame(tk.Frame):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.frame_slider = tk.Frame(master=self)
        self.frame_slider.pack(fill="x")

        self.slider_value = tk.DoubleVar()

    def create_slider(self):

        self.slider = tk.Scale(
            master=self.frame_slider,
            variable=self.slider_value,
            from_=0,
            to=config.videoobject.totalframecount - 1,
            orient=tk.HORIZONTAL,
            command=lambda event: self.slider_scroll(int(event)),
        )

        self.slider.bind("<ButtonPress-1>", self.slider_pressed)
        self.slider.bind("<ButtonRelease-1>", self.slider_released)

        self.slider.pack(fill="x")

    def destroy_slider(self):
        self.slider.destroy()

    def slider_pressed(self, event):
        """
        Args:
            event (Sliderbutton is pressed): When slider is pressed, thread that updates
            queue with frames stops and gets terminated.
        """

        button_bool["slider"] = True

    def slider_released(self, event):
        """
        Args:
            event (Sliderbutton is pressed): When slider is pressed, thread that updates
            queue with frames stops and gets terminated.
        """
        config.maincanvas.delete_polygon_points()

        button_bool["slider"] = False

    def slider_scroll(self, slider_number):
        """Slides through video with tkinter slider.

        Args:
            slider_number (int): Represents current videoframe.
        """
        print(button_bool["slider"])

        if (
            not button_bool["play_video"]
            and not button_bool["rewind_video"]
            and button_bool["slider"]
        ):
            config.videoobject.current_frame = slider_number

            np_image = config.videoobject.set_frame()

            image_alteration.manipulate_image(np_image=np_image)
