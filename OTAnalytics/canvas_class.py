# works

import tkinter as tk


class OtcCanvas(tk.Canvas):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.bind("<ButtonPress-2>")
        self.bind("<ButtonPress-3>")

        self.slider_value = tk.DoubleVar()
        # self.linepoints = [(0, 0), (0, 0)]
        self.points = [(0, 0), (0, 0)]
        self.polygon_points = []

    def click_receive_coordinates(self, event, list_index):
        """Saves coordinates from canvas event to linepoint list.

        Args:
            event ([type]): [description]
            linepoints ([list]): cache of linepoints
            polygonpoints ([list]): [description]
            canvas ([type]): [description]
        """
        #  uses mouseevents to get coordinates (left button)
        self.coordinateX = int(self.canvasx(event.x))
        self.coordinateY = int(self.canvasy(event.y))

        self.points[list_index] = (
            self.coordinateX,
            self.coordinateY,
        )

    def slider_scroll(self, hand_slide, videoobject):

        # TODO if video plays don't call get frame!

        self.slider_value = hand_slide

        videoobject.current_frame = self.slider_value

        current_image = videoobject.get_frame()

        videoobject.current_frame += 1

        self.create_image(0, 0, anchor=tk.NW, image=current_image)
