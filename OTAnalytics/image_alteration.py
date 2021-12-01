import tkinter as tk
from gui_helper import button_bool, color_dict
import cv2
from PIL import Image, ImageTk
import numpy as np


def manipulate_image(np_image, video, canvas, flowdictionary, selectionlist, tracks):

    np_image = draw_detectors_from_dict(np_image, flowdictionary)

    if button_bool["tracks_imported"]:
        np_image = draw_tracks(np_image, selectionlist, tracks)

    # copy is important or else original image will be changed
    image = Image.fromarray(np_image)  # to PIL format

    # The variable photo is a local variable which gets garbage collected after the
    # class is instantiated. Save a reference to the photo
    # photo is attribute of video
    video.ph_image = ImageTk.PhotoImage(image)

    canvas.create_image(0, 0, anchor=tk.NW, image=video.ph_image)

    canvas.update()


def draw_detectors_from_dict(np_image, flowdictionary):
    """Draws detectors on every frame.

    Args:
        np_image (array): image as numpy array

    Returns:
        np_image (array): returns manipulated image"""

    if flowdictionary["Detectors"]:

        Line = "line"

        for detector in flowdictionary["Detectors"]:
            if flowdictionary["Detectors"][detector]["type"] == Line:
                start_x = flowdictionary["Detectors"][detector]["start_x"]
                start_y = flowdictionary["Detectors"][detector]["start_y"]
                end_x = flowdictionary["Detectors"][detector]["end_x"]
                end_y = flowdictionary["Detectors"][detector]["end_y"]
                color = flowdictionary["Detectors"][detector]["color"]

                np_image = cv2.line(
                    np_image, (start_x, start_y), (end_x, end_y), color, 3
                )

            else:

                # don't know why
                image = np_image
                overlay = image.copy()

                polypoints = flowdictionary["Detectors"][detector]["points"]
                color = flowdictionary["Detectors"][detector]["color"]

                list_of_tuples = [list(elem) for elem in polypoints]
                pts = np.array(list_of_tuples, np.int32)
                pts = pts.reshape((-1, 1, 2))

                np_image = cv2.fillPoly(overlay, [pts], (200, 125, 125))

                opacity = 0.4
                np_image = cv2.addWeighted(overlay, opacity, image, 1 - opacity, 0)
                np_image = cv2.polylines(np_image, [pts], True, color, 2)

    return np_image


def draw_tracks(np_image, selectionlist, tracks):
    """Draw from listbox selected objecttracks.

    Args:
        selectionlist (list): list with selected objects
        object_dict (dictionary): dictionary with objects as keys corresponding frames-
        and coordslist.
        np_image (array): arraylike image object

    Returns:
        np_image (array): manipulated array
    """

    if button_bool["display_all_tracks_toggle"] is True:

        for track in tracks:

            try:
                trackcolor = color_dict[tracks[track]["Class"]]
            except NameError:
                trackcolor = (0, 0, 255)

            pts = np.array(tracks[track]["Coord"], np.int32)

            pts = pts.reshape((-1, 1, 2))

            np_image = cv2.polylines(
                np_image, [pts], False, color=trackcolor, thickness=2
            )

    elif selectionlist:

        for object_id in selectionlist:

            try:
                trackcolor = color_dict[tracks[object_id]["Class"]]
            except NameError:

                trackcolor = (0, 0, 255)

            pts = np.array(tracks[object_id]["Coord"], np.int32)

            pts = pts.reshape((-1, 1, 2))

            np_image = cv2.polylines(
                np_image, [pts], False, color=trackcolor, thickness=2
            )

    return np_image
