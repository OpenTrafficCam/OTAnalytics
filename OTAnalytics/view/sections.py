import json
from tkinter import filedialog

import cv2
import numpy as np
from view.helpers.gui_helper import button_bool, info_message
import view.image_alteration
import view.config
import helpers.file_helper as file_helper
from shapely.geometry import LineString


def save_flowfile():
    """Save created dictionary with detectors
    and movements.

    Args:
        flow_dict (dictionary): Dictionary with sections and movements.
    """
    if file_helper.flow_dict["Detectors"]:
        files = [("Files", "*.otflow")]
        file = filedialog.asksaveasfile(filetypes=files, defaultextension=files)
        # with open(file.name, "w") as a_file:
        #     flow_dict["Detectors"] = detectors
        #     flow_dict["Movements"] = movement_dict

        json.dump(file_helper.flow_dict, file, indent=4)
    else:
        info_message("Warning", "Create Sections and Movements first!")


def draw_line(
    event,
):
    """Draws line on canvas"""

    np_image = view.config.videoobject.np_image.copy()

    if not button_bool["linedetector_toggle"]:

        return

    lineobject = create_LineString(
        view.config.maincanvas.points[0], view.config.maincanvas.points[1]
    )
    view.image_alteration.create_intersection_list(lineobject)

    view.image_alteration.manipulate_image(np_image=np_image)


def create_LineString(start, end):
    return LineString([start, end])


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

    image = view.config.videoobject.np_image.copy()
    overlay = image.copy()

    if undo:

        del view.config.maincanvas.polygon_points[-1]

    if adding_points:

        view.config.maincanvas.polygon_points.append(view.config.maincanvas.points[0])

    list_of_tuples = [list(elem) for elem in view.config.maincanvas.polygon_points]

    pts = np.array(list_of_tuples, np.int32)
    pts = pts.reshape((-1, 1, 2))

    if closing:

        np_image = cv2.fillPoly(overlay, [pts], (200, 125, 125, 200))
        opacity = 0.4
        np_image = cv2.addWeighted(overlay, opacity, image, 1 - opacity, 0, image)

    np_image = cv2.polylines(image, [pts], closing, (200, 125, 125, 255), 2)

    view.image_alteration.manipulate_image(np_image=np_image)


def create_polyline(pts):
    pass


def load_flowfile():
    """Loads sections from a .OTflow-File."""

    if (
        not file_helper.flow_dict["Detectors"]
        and not file_helper.flow_dict["Movements"]
    ):
        filepath = filedialog.askopenfile(filetypes=[("Detectors", "*.OTflow")])
        files = open(filepath.name, "r")
        files = files.read()

        return json.loads(files)

    else:
        info_message("Warning", "Clear existing flowfile first!")


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
            "start_x": view.config.maincanvas.points[0][0],
            "start_y": view.config.maincanvas.points[0][1],
            "end_x": view.config.maincanvas.points[1][0],
            "end_y": view.config.maincanvas.points[1][1],
            "color": (200, 125, 125, 255),
        }

    if button_bool["polygondetector_toggle"] is True:
        file_helper.flow_dict["Detectors"][detector_name] = {
            "type": "polygon",
            "points": view.config.maincanvas.polygon_points,
            "color": (200, 125, 125, 255),
        }
