import json
from tkinter import Toplevel, filedialog, mainloop
from tkinter.constants import END
import tkinter as tk
from gui_helper import button_bool

import cv2
from canvas_class import OtcCanvas
import numpy as np

from image_alteration import manipulate_image


def save_file(flow_dict):
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
    json.dump(flow_dict, file, indent=4)


def draw_line(event, video, canvas, flowdictionary, selectionlist, tracks):

    np_image = video.np_image.copy()

    if not button_bool["linedetector_toggle"]:

        return

    np_image = cv2.line(
        np_image, canvas.points[0], canvas.points[1], (200, 125, 125), 3
    )

    manipulate_image(np_image, video, canvas, flowdictionary, selectionlist, tracks)


def draw_polygon(event, video, canvas, adding_points=False, closing=False, undo=False):
    """Draws a polygon on canvas.

    Args:
        closing (bool): if true create polygon else continue drawing

    """
    # TODO here function manipulate image to draw everything from:
    # flow_dict, tracks....

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

    manipulate_image(np_image, video, canvas)


def load_flowfile():
    """loads detectors from a .OTflow-File."""
    filepath = filedialog.askopenfile(filetypes=[("Detectors", "*.OTflow")])
    files = open(filepath.name, "r")
    files = files.read()

    return json.loads(files)

    detectors.update(flow_dict["Detectors"])
    movements.update(flow_dict["Movements"])

    # resets polypoints list or else creation of new polygon leads to bug
    # self.polypoints = []

    for movement in movements:
        ListboxMovement.insert(END, movement)

    for detector in detectors:
        ListboxDetector.insert(END, detector)
