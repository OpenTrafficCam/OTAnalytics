import json
from tkinter import filedialog

import cv2
import numpy as np
from gui_helper import button_bool
import image_alteration
import config
import file_helper


def save_flowfile():
    """Save created dictionary with detectors
    and movements.

    Args:
        flow_dict (dictionary): Dictionary with sections and movements.
    """
    files = [("Files", "*.OTflow")]
    file = filedialog.asksaveasfile(filetypes=files, defaultextension=files)
    # with open(file.name, "w") as a_file:
    #     flow_dict["Detectors"] = detectors
    #     flow_dict["Movements"] = movement_dict

    # BUG: is saved as nested dictionary in a list; empty dictionary also gets dumped
    json.dump(file_helper.flow_dict, file, indent=4)


def draw_line(
    event,
):
    """Draws line on canvas"""

    np_image = config.videoobject.np_image.copy()

    if not button_bool["linedetector_toggle"]:

        return

    np_image = cv2.line(
        np_image,
        config.maincanvas.points[0],
        config.maincanvas.points[1],
        (200, 125, 125),
        3,
    )

    image_alteration.manipulate_image(np_image=np_image)


def draw_polygon(
    event,
    adding_points=False,
    closing=False,
    undo=False,
):
    """Draws a polygon on canvas.

    Args:
        closing (bool): If true create polygon else polyline.
    """
    if not button_bool["polygondetector_toggle"]:

        return

    image = config.videoobject.np_image.copy()
    overlay = image.copy()

    if undo:

        del config.maincanvas.polygon_points[-1]

    if adding_points:

        config.maincanvas.polygon_points.append(config.maincanvas.points[0])

    list_of_tuples = [list(elem) for elem in config.maincanvas.polygon_points]

    pts = np.array(list_of_tuples, np.int32)
    pts = pts.reshape((-1, 1, 2))

    if closing:

        np_image = cv2.fillPoly(overlay, [pts], (200, 125, 125))
        opacity = 0.4
        np_image = cv2.addWeighted(overlay, opacity, image, 1 - opacity, 0, image)

    np_image = cv2.polylines(image, [pts], closing, (200, 125, 125), 2)

    image_alteration.manipulate_image(np_image=np_image)


def load_flowfile():
    """Loads sections from a .OTflow-File."""
    filepath = filedialog.askopenfile(filetypes=[("Detectors", "*.OTflow")])
    files = open(filepath.name, "r")
    files = files.read()

    return json.loads(files)


def dump_to_flowdictionary(detector_name):
    """Saves sections to flowdictionary.

    Args:
        canvas (tkinter.canvas): Cancvas that hand out clicked coordinates.
        flow_dict (dictionary): Dictionary with sections and movements.
        detector_name (String): Entrywidgetinput, functions as key of dictionary.
    """

    if button_bool["linedetector_toggle"] is True:

        file_helper.flow_dict["Detectors"][detector_name] = {
            "type": "line",
            "start_x": config.maincanvas.points[0][0],
            "start_y": config.maincanvas.points[0][1],
            "end_x": config.maincanvas.points[1][0],
            "end_y": config.maincanvas.points[1][1],
            "color": (200, 125, 125),
        }

    if button_bool["polygondetector_toggle"] is True:
        file_helper.flow_dict["Detectors"][detector_name] = {
            "type": "polygon",
            "points": config.maincanvas.polygon_points,
            "color": (200, 125, 125),
        }
