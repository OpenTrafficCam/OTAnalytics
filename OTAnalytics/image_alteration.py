from sections import draw_polygon
from tracks2 import draw_line_section
import tkinter as tk
from gui_dict import gui_dict


def manipulate_image(event, canvas, video):

    np_image = video.np_image.copy()

    if gui_dict["linedetector_toggle"]:

        np_image = draw_line_section(
            np_image,
            (canvas.clicked_coordinateX, canvas.clicked_coordinateY),
            (canvas.dragged_coordinateX, canvas.dragged_coordinateY),
        )

        ph_image = video.recieve_altered_frame(np_image)

    if gui_dict["polygondetector_toggle"]:

        np_image = draw_polygon(
            np_image,
            canvas.polypoints,
        )

    canvas.create_image(0, 0, anchor=tk.NW, image=ph_image)
