import json
from tkinter import filedialog
from tkinter.constants import END

import cv2
from canvas_class import OtcCanvas
from gui_dict import gui_dict
from PIL import Image, ImageTk
import numpy as np


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


def draw_line_section(np_image, startpoint, endpoint):

    return cv2.line(np_image, startpoint, endpoint, (200, 125, 125), 3)


def draw_polygon(np_image, polypoints, points):
    """Draws a polygon on canvas.

    Args:
        closing (bool): if true create polygon else continue drawing

    """
    image = np_image
    # overlay = image.copy()

    polypoints.append(points)

    list_of_tuples = [list(elem) for elem in polypoints]

    pts = np.array(list_of_tuples, np.int32)
    pts = pts.reshape((-1, 1, 2))

    # if closing is not False:

    #     np_image = cv2.fillPoly(overlay, [pts], (200, 125, 125))
    #     opacity = 0.4
    #     np_image = cv2.addWeighted(overlay, opacity, image, 1 - opacity, 0, image)
    return cv2.polylines(image, [pts], False, (200, 125, 125), 2)


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
