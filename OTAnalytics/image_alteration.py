from sections import draw_polygon
from sections import draw_line_section, draw_detectors_from_dict
import tkinter as tk
from gui_dict import gui_dict
import cv2
from PIL import Image, ImageTk


def manipulate_image(
    video,
    canvas,
    flow_dictionary,
    closing=None,
    undo=False,
    adding_points=False,
):

    np_image = video.get_frame(np_image=True)

    if gui_dict["linedetector_toggle"]:

        np_image = draw_line_section(
            np_image,
            (canvas.clicked_coordinateX, canvas.clicked_coordinateY),
            (canvas.dragged_coordinateX, canvas.dragged_coordinateY),
        )

    if gui_dict["polygondetector_toggle"]:

        np_image = draw_polygon(
            np_image,
            canvas.polypoints,
            (canvas.clicked_coordinateX, canvas.clicked_coordinateY),
            adding_points,
            closing,
            undo,
        )

    np_image = draw_detectors_from_dict(np_image, flow_dictionary)

    # copy is important or else original image will be changed
    image = Image.fromarray(np_image.copy())  # to PIL format

    # The variable photo is a local variable which gets garbage collected after the
    # class is instantiated. Save a reference to the photo
    ph_image = ImageTk.PhotoImage(image)

    canvas.create_image(0, 0, anchor=tk.NW, image=ph_image)

    canvas.update()
