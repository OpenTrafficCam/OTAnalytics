import json
from tkinter import Toplevel, filedialog, mainloop
from tkinter.constants import END
import tkinter as tk

import cv2
from canvas_class import OtcCanvas
from gui_dict import gui_dict
from PIL import Image, ImageTk
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


def draw_line(event, video, canvas):

    np_image = video.np_image.copy()

    if not gui_dict["linedetector_toggle"]:

        return

    np_image = cv2.line(
        np_image, canvas.points[0], canvas.points[1], (200, 125, 125), 3
    )

    manipulate_image(np_image, video, canvas)


def draw_polygon(event, video, canvas, adding_points=False, closing=False, undo=False):
    """Draws a polygon on canvas.

    Args:
        closing (bool): if true create polygon else continue drawing

    """
    # TODO here function manipulate image to draw everything from:
    # flow_dict, tracks....

    if not gui_dict["polygondetector_toggle"]:

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


def add_section(maincanvas, flow_dict, entrywidget):

    if gui_dict["linedetector_toggle"] is True:
        detector_name = entrywidget.get()

        print(maincanvas.linepoints)

        flow_dict["Detectors"][detector_name] = {
            "type": "line",
            "start_x": maincanvas.linepoints[0][0],
            "start_y": maincanvas.linepoints[0][1],
            "end_x": maincanvas.linepoints[1][0],
            "end_y": maincanvas.linepoints[1][1],
            "color": (200, 125, 125),
        }

    print(flow_dict)


def load_file(detectors, movements, ListboxDetector, ListboxMovement):
    """loads detectors from a .OTSect-File."""
    filepath = filedialog.askopenfile(filetypes=[("Detectors", "*.OTflow")])
    files = open(filepath.name, "r")
    files = files.read()

    flow_dict = json.loads(files)

    detectors.update(flow_dict["Detectors"])
    movements.update(flow_dict["Movements"])

    # resets polypoints list or else creation of new polygon leads to bug
    # self.polypoints = []

    for movement in movements:
        ListboxMovement.insert(END, movement)

    for detector in detectors:
        ListboxDetector.insert(END, detector)


def draw_detectors_from_dict(np_image, flow_dict):
    """Draws detectors on every frame.

    Args:
        np_image (array): image as numpy array

    Returns:
        np_image (array): returns manipulated image"""

    if flow_dict["Detectors"]:

        Line = "line"

        for detector in flow_dict["Detectors"]:
            if flow_dict["Detectors"][detector]["type"] == Line:
                start_x = flow_dict["Detectors"][detector]["start_x"]
                start_y = flow_dict["Detectors"][detector]["start_y"]
                end_x = flow_dict["Detectors"][detector]["end_x"]
                end_y = flow_dict["Detectors"][detector]["end_y"]
                color = flow_dict["Detectors"][detector]["color"]

                np_image = cv2.line(
                    np_image, (start_x, start_y), (end_x, end_y), color, 3
                )

            else:

                # dont know why
                image = np_image
                overlay = image.copy()

                polypoints = flow_dict["Detectors"][detector]["points"]
                color = flow_dict["Detectors"][detector]["color"]

                list_of_tuples = [list(elem) for elem in polypoints]
                pts = np.array(list_of_tuples, np.int32)
                pts = pts.reshape((-1, 1, 2))

                np_image = cv2.fillPoly(overlay, [pts], (200, 125, 125))

                opacity = 0.4
                np_image = cv2.addWeighted(overlay, opacity, image, 1 - opacity, 0)
                np_image = cv2.polylines(np_image, [pts], True, color, 2)

        print(flow_dict)

    return np_image
