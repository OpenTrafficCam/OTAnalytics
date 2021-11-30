# works

import tkinter as tk
from video import Video
import keyboard


class OtcCanvas(tk.Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(**kwargs)

        self.bind("<ButtonPress-2>")
        self.bind("<ButtonPress-3>")

        self.slider_value = tk.DoubleVar()
        # self.linepoints = [(0, 0), (0, 0)]
        self.points = [(0, 0), (0, 0)]
        self.polygon_points = []

    def click_recieve_coorinates(self, event, list_index):
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
        print(self.points)

    # def drag_recieve_coordinates(self, event):
    #     self.dragged_coordinateX = int(self.canvasx(event.x))
    #     self.dragged_coordinateY = int(self.canvasy(event.y))

    #     self.linepoints[1] = (self.dragged_coordinateX, self.dragged_coordinateY)

    #     w, h = self.winfo_width(), self.winfo_height()
    #     if event.x > 0.9 * w:
    #         self.xview_scroll(1, "units")
    #     elif event.x < 0.1 * w:
    #         self.xview_scroll(-1, "units")
    #     if event.y > 0.9 * h:
    #         self.yview_scroll(1, "units")
    #     elif event.y < 0.1 * h:
    #         self.yview_scroll(-1, "units")

    #     print(self.dragged_coordinateX)

    def scroll_through_video(self, event, videoobject):

        i = 1 * event.delta // 120

        videoobject.current_frame += i

    def slider_scroll(self, event, hand_slide, videoobject):

        # TODO if video plays dont call get frame!

        self.slider_value = hand_slide

        videoobject.current_frame = self.slider_value

        current_image = videoobject.get_frame()

        videoobject.current_frame += 1

        self.create_image(0, 0, anchor=tk.NW, image=current_image)


# root = tk.Tk()


# videoobject1 = Video("tests\\test-data\\input\\radeberg.mp4")

# canvas1 = OtcCanvas(parent=root, width=videoobject1.width, height=videoobject1.height)
# canvas1.grid(row=0, column=0)

# image1 = videoobject1.get_frame()

# canvas1.create_image(0, 0, anchor=tk.NW, image=image1)


# root.mainloop()
