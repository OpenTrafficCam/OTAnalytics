import json
from tkinter import filedialog

import cv2
import numpy as np
from view.helpers.gui_helper import button_bool, info_message
import view.image_alteration
import helpers.config
import helpers.file_helper as file_helper
from shapely.geometry import LineString


def save_flowfile():
    """Save created dictionary with detectors
    and movements.

    Args:
        flow_dict (dictionary): Dictionary with sections and movements.
    """
    if file_helper.flow_dict["Detectors"]:


        for detector in file_helper.flow_dict["Detectors"]:
            file_helper.flow_dict["Detectors"][detector]["start_x"] = file_helper.flow_dict["Detectors"][detector]["start_x"] / file_helper.list_of_analyses[file_helper.list_of_analyses_index].videoobject.x_resize_factor
            file_helper.flow_dict["Detectors"][detector]["start_y"] = file_helper.flow_dict["Detectors"][detector]["start_y"] / file_helper.list_of_analyses[file_helper.list_of_analyses_index].videoobject.y_resize_factor
            file_helper.flow_dict["Detectors"][detector]["end_x"] = file_helper.flow_dict["Detectors"][detector]["end_x"] / file_helper.list_of_analyses[file_helper.list_of_analyses_index].videoobject.x_resize_factor
            file_helper.flow_dict["Detectors"][detector]["end_y"] = file_helper.flow_dict["Detectors"][detector]["end_y"] / file_helper.list_of_analyses[file_helper.list_of_analyses_index].videoobject.y_resize_factor
            #de geometry key because it cant be saved
            if 'geometry' in file_helper.flow_dict["Detectors"][detector]:
                del file_helper.flow_dict["Detectors"][detector]['geometry']

        files = [("Files", "*.otflow")]
        file = filedialog.asksaveasfile(filetypes=files, defaultextension=files)
        # with open(file.name, "w") as a_file:
        #     flow_dict["Detectors"] = detectors
        #     flow_dict["Movements"] = movement_dict

        json.dump(file_helper.flow_dict, file, indent=4)

        for detector in file_helper.flow_dict["Detectors"]:
            file_helper.flow_dict["Detectors"][detector]["start_x"] = file_helper.flow_dict["Detectors"][detector]["start_x"] * file_helper.list_of_analyses[file_helper.list_of_analyses_index].videoobject.x_resize_factor
            file_helper.flow_dict["Detectors"][detector]["start_y"] = file_helper.flow_dict["Detectors"][detector]["start_y"] * file_helper.list_of_analyses[file_helper.list_of_analyses_index].videoobject.y_resize_factor
            file_helper.flow_dict["Detectors"][detector]["end_x"] = file_helper.flow_dict["Detectors"][detector]["end_x"] * file_helper.list_of_analyses[file_helper.list_of_analyses_index].videoobject.x_resize_factor
            file_helper.flow_dict["Detectors"][detector]["end_y"] = file_helper.flow_dict["Detectors"][detector]["end_y"] * file_helper.list_of_analyses[file_helper.list_of_analyses_index].videoobject.y_resize_factor



    else:
        info_message("Warning", "Create Sections and Movements first!")



def prepare_draw_line(
    event,
):
    """Draws line on canvas"""

    np_image = file_helper.list_of_analyses[file_helper.list_of_analyses_index].videoobject.np_image.copy()

    if not button_bool["linedetector_toggle"]:

        return

    lineobject = create_LineString(
        [
            helpers.config.maincanvas.points[0],
            helpers.config.maincanvas.points[1],
        ]
    )
    view.image_alteration.create_intersection_list(lineobject)

    view.image_alteration.manipulate_image(np_image=np_image)


def create_LineString(pts):
    """Creates linestring from two point coordinates.

    Args:
        start (tuple): x-y-coordintes
        end (tuple): x-y-coordintes

    Returns:
        geoobject: Linestring geoobject to compute intersections.
    """
    return LineString(pts)


def draw_line(np_image):
    return cv2.line(
        np_image,
        helpers.config.maincanvas.points[0],
        helpers.config.maincanvas.points[1],
        (200, 125, 125, 255),
        3,
    )


def prepare_polygon(
    event,
    adding_points=False,
    closing=False,
    undo=False,
):
    """Draws polygon on canvas.

    Args:
        event (event): mouseclick event.
        adding_points (bool, optional): adds points of polygon to a list.
        closing (bool, optional): closes polygon.
        undo (bool, optional): deletes last polygon points.
    """
    if not button_bool["polygondetector_toggle"]:

        return

    np_image = file_helper.list_of_analyses[file_helper.list_of_analyses_index].videoobject.np_image.copy()

    if undo:

        del helpers.config.maincanvas.polygon_points[-1]

    if adding_points:

        helpers.config.maincanvas.polygon_points.append(
           helpers.config.maincanvas.points[0]
        )

    list_of_tuples = [
        list(elem) for elem in helpers.config.maincanvas.polygon_points
    ]

    if len(list_of_tuples) > 1:
        lineobject = create_LineString(list_of_tuples)
        view.image_alteration.create_intersection_list(lineobject)

    view.image_alteration.manipulate_image(closing=closing, np_image=np_image)


def draw_polygon(np_image, closing):

    image = np_image
    overlay = image.copy()
    list_of_tuples = [
        list(elem) for elem in helpers.config.maincanvas.polygon_points
    ]

    pts = np.array(list_of_tuples, np.int32)
    pts = pts.reshape((-1, 1, 2))

    if closing:

        np_image = cv2.fillPoly(overlay, [pts], (200, 125, 125, 200))
        opacity = 0.4
        np_image = cv2.addWeighted(overlay, opacity, image, 1 - opacity, 0, image)

    return cv2.polylines(image, [pts], closing, (200, 125, 125, 255), 2)


def load_flowfile(TRANSFORMED_COORDS):
    """Loads flow file.

    Returns:
        json: Return json file to read from.
    """
    if not TRANSFORMED_COORDS:
        file_helper.list_of_analyses[file_helper.list_of_analyses_index].videoobject.x_resize_factor = 1
        file_helper.list_of_analyses[file_helper.list_of_analyses_index].videoobject.y_resize_factor = 1


    filepath = filedialog.askopenfile(filetypes=[("Detectors", "*.OTflow")])
    if not filepath:
        print("no flowfile selected")
    else:
        files = open(filepath.name, "r")
        files = files.read()

        flow_dict_new = json.loads(files)

        file_helper.flow_dict.update(flow_dict_new)


        for detector in flow_dict_new["Detectors"]:
            print(detector)
            file_helper.flow_dict["Detectors"][detector]["start_x"] = file_helper.flow_dict["Detectors"][detector]["start_x"] * file_helper.list_of_analyses[file_helper.list_of_analyses_index].videoobject.x_resize_factor
            file_helper.flow_dict["Detectors"][detector]["start_y"] = file_helper.flow_dict["Detectors"][detector]["start_y"] * file_helper.list_of_analyses[file_helper.list_of_analyses_index].videoobject.y_resize_factor
            file_helper.flow_dict["Detectors"][detector]["end_x"] = file_helper.flow_dict["Detectors"][detector]["end_x"] * file_helper.list_of_analyses[file_helper.list_of_analyses_index].videoobject.x_resize_factor
            file_helper.flow_dict["Detectors"][detector]["end_y"] = file_helper.flow_dict["Detectors"][detector]["end_y"] * file_helper.list_of_analyses[file_helper.list_of_analyses_index].videoobject.y_resize_factor
            #de geometry key because it cant be saved

        print(file_helper.flow_dict)


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
            "start_x": helpers.config.maincanvas.points[0][0],
            "start_y": helpers.config.maincanvas.points[0][1],
            "end_x":helpers.config.maincanvas.points[1][0],
            "end_y": helpers.config.maincanvas.points[1][1],
            "color": (200, 125, 125, 255),
        }

    if button_bool["polygondetector_toggle"] is True:
        file_helper.flow_dict["Detectors"][detector_name] = {
            "type": "polygon",
            "points": helpers.config.maincanvas.polygon_points,
            "color": (200, 125, 125, 255),
        }
