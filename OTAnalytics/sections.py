import json
from tkinter import Toplevel, filedialog, mainloop
from tkinter.constants import END
import tkinter as tk
from gui_helper import button_bool

import cv2
from canvas_class import OtcCanvas
import numpy as np

from image_alteration import manipulate_image


def save_flowfile(flowdictionary):
    """Save created dictionary with detectors
    and movements.

    Args:
        flow_dict (dictionary): Dictionary with necessary information for reuse.
    """
    files = [("Files", "*.OTflow")]
    file = filedialog.asksaveasfile(filetypes=files, defaultextension=files)
    # with open(file.name, "w") as a_file:
    #     flow_dict["Detectors"] = detectors
    #     flow_dict["Movements"] = movement_dict

    # BUG: is saved as nested dictionary in a list; empty dictionary also gets dumped
    json.dump(flowdictionary, file, indent=4)


def draw_line(
    event, video, canvas, flowdictionary, selectionlist, tracks, raw_detection
):

    np_image = video.np_image.copy()

    if not button_bool["linedetector_toggle"]:

        return

    np_image = cv2.line(
        np_image, canvas.points[0], canvas.points[1], (200, 125, 125), 3
    )

    manipulate_image(
        np_image, video, canvas, flowdictionary, selectionlist, tracks, raw_detection
    )


def draw_polygon(
    event,
    video,
    canvas,
    flowdictionary,
    selectionlist,
    tracks,
    adding_points=False,
    closing=False,
    undo=False,
):
    """Draws a polygon on canvas.

    Args:
        closing (bool): if true create polygon else continue drawing

    """
    if not button_bool["polygondetector_toggle"]:

        return

    image = video.np_image.copy()
    overlay = image.copy()

    if undo:

        del canvas.polygon_points[-1]

    if adding_points:

        canvas.polygon_points.append(canvas.points[0])

    list_of_tuples = [list(elem) for elem in canvas.polygon_points]

    pts = np.array(list_of_tuples, np.int32)
    pts = pts.reshape((-1, 1, 2))

    if closing:

        np_image = cv2.fillPoly(overlay, [pts], (200, 125, 125))
        opacity = 0.4
        np_image = cv2.addWeighted(overlay, opacity, image, 1 - opacity, 0, image)

    np_image = cv2.polylines(image, [pts], closing, (200, 125, 125), 2)

    manipulate_image(np_image, video, canvas, flowdictionary, selectionlist, tracks)


def load_flowfile():
    """loads detectors from a .OTflow-File."""
    filepath = filedialog.askopenfile(filetypes=[("Detectors", "*.OTflow")])
    files = open(filepath.name, "r")
    files = files.read()

    return json.loads(files)


def dump_to_flowdictionary(canvas, flowdictionary, detector_name):

    if button_bool["linedetector_toggle"] is True:

        flowdictionary["Detectors"][detector_name] = {
            "type": "line",
            "start_x": canvas.points[0][0],
            "start_y": canvas.points[0][1],
            "end_x": canvas.points[1][0],
            "end_y": canvas.points[1][1],
            "color": (200, 125, 125),
        }

    if button_bool["polygondetector_toggle"] is True:
        flowdictionary["Detectors"][detector_name] = {
            "type": "polygon",
            "points": canvas.polygon_points,
            "color": (200, 125, 125),
        }
