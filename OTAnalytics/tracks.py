from gui_dict import gui_dict, color_dict
import json
from tkinter import filedialog
import cv2
import numpy as np


def load_tracks(object_dict, object_live_track, raw_detections, listboxtracks):
    """loads detectors from a .Track-File and converts into displayable format"""

    filepath = filedialog.askopenfile(filetypes=[("Detectors", "*.ottrk")])
    files = open(filepath.name, "r")
    files = files.read()

    loaded_dict = json.loads(files)

    # raw detections from OTVision
    raw_detections.update(loaded_dict["data"])

    for frame in raw_detections:
        for detection in raw_detections[frame]:
            if "object_" + str(detection) in object_dict.keys():
                object_dict["object_%s" % detection]["Coord"].append(
                    [
                        raw_detections[frame][detection]["x"],
                        raw_detections[frame][detection]["y"],
                    ]
                )

                object_dict["object_%s" % detection]["Frame"].append(int(frame))

            elif raw_detections[frame][detection]["class"] in color_dict.keys():
                object_dict["object_%s" % detection] = {}
                object_dict["object_%s" % detection]["Coord"] = []
                object_dict["object_%s" % detection]["Frame"] = [int(frame)]
                object_dict["object_%s" % detection]["Class"] = raw_detections[frame][
                    detection
                ]["class"]
                object_dict["object_%s" % detection]["Coord"].append(
                    [
                        raw_detections[frame][detection]["x"],
                        raw_detections[frame][detection]["y"],
                    ]
                )
    for object in list(object_dict.keys()):

        listboxtracks.insert("end", object)
        # initialize Tracks to draw live
        object_live_track[object] = []

    save_object_dic(object_dict)

    gui_dict["tracks_imported"] = True


def draw_tracks(selectionlist, object_dict, np_image):
    """Draw from listbox selected objecttracks.

    Args:
        selectionlist (list): list with selected objects
        object_dict (dictionary): dictionary with objects as keys corresponding frames-
        and coordslist.
        np_image (array): arraylike image object

    Returns:
        np_image (array): manipulated array
    """

    if gui_dict["display_all_tracks_toggle"] is True:

        for track in object_dict:

            try:
                trackcolor = color_dict[object_dict[track]["Class"]]
            except NameError:
                trackcolor = (0, 0, 255)

            pts = np.array(object_dict[track]["Coord"], np.int32)

            pts = pts.reshape((-1, 1, 2))

            np_image = cv2.polylines(
                np_image, [pts], False, color=trackcolor, thickness=2
            )

    elif selectionlist:

        for object_id in selectionlist:

            try:
                trackcolor = color_dict[object_dict[object_id]["Class"]]
            except NameError:

                trackcolor = (0, 0, 255)

            pts = np.array(object_dict[object_id]["Coord"], np.int32)

            pts = pts.reshape((-1, 1, 2))

            np_image = cv2.polylines(
                np_image, [pts], False, color=trackcolor, thickness=2
            )

    return np_image


def save_object_dic(object_dict):
    """Saves dictionary.

    Args: object_dict (dictionary)): Dictionary with objects as keys corresponding frames-
    and coordslist
    """
    # experimental function / not necessary for end product

    json.dump(object_dict, open("object_dic.json", "w"), indent=4)


def draw_tracks_live(object_dict, object_live_track, frame, raw_detections, np_image):
    """Draw tracks while playing video

    Args:
        object_dict (dictionary): resampled raw detections
        object_live_track (dictionary): dictionary with framewiselive coordinates
        frame (integer): current video frame
        raw_detections (dictionary): input file with all detections
        np_image : arraylike image object

    Returns:
        np_image: returns manipulated image
    """

    if raw_detections and gui_dict["play_video"] and gui_dict["display_live_track"]:

        for object in object_dict.keys():

            if frame in object_dict[object]["Frame"]:

                if not object_live_track[object]:
                    object_live_track[object] = [
                        object_dict[object]["Coord"][
                            object_dict[object]["Frame"].index(frame)
                        ]
                    ]

                elif frame < object_dict[object]["Frame"][-1]:

                    nextframeindex = object_dict[object]["Frame"].index(frame)
                    object_live_track[object].append(
                        object_dict[object]["Coord"][nextframeindex]
                    )

                    trackcolor = color_dict[object_dict[object]["Class"]]

                    pts = np.array(object_live_track[object], np.int32)

                    pts = pts.reshape((-1, 1, 2))

                    np_image = cv2.polylines(
                        np_image, [pts], False, color=trackcolor, thickness=2
                    )
                # else:
                # not necessary
                #     #if track is drawn completly => erase from canvas
                #     object_live_track[object] = []

    return np_image


def draw_bounding_box(raw_detections, frame, image):
    """Draws bounding boxes in every frame.

    Args:
        raw_detections (dictionary): inputfile with detections from OTVision
        frame (int): index of frame
        image (array): Arraylike image to draw on

    Returns:
       np_image: returns manipulated image
    """
    if not gui_dict["display_bb"]:
        return image
    try:
        if raw_detections:

            image_cache = image

            for detection in raw_detections[frame]:
                if raw_detections[frame][detection]["class"] in color_dict.keys():

                    class_txt = raw_detections[frame][detection]["class"]

                    confidence_txt = "{:.2f}".format(
                        (raw_detections[frame][detection]["conf"])
                    )

                    anno_txt = class_txt + " " + str(confidence_txt)

                    if raw_detections[frame][detection]["w"] < 0.3 * 100:
                        fontscale = 0.3
                    elif raw_detections[frame][detection]["w"] > 0.5 * 100:
                        fontscale = 0.5
                    else:
                        fontscale = raw_detections[frame][detection]["w"] / 100

                    x_start = int(
                        raw_detections[frame][detection]["x"]
                        - raw_detections[frame][detection]["w"] / 2
                    )

                    y_start = int(
                        raw_detections[frame][detection]["y"]
                        - raw_detections[frame][detection]["h"] / 2
                    )

                    x_end = int(
                        raw_detections[frame][detection]["x"]
                        + raw_detections[frame][detection]["w"] / 2
                    )

                    y_end = int(
                        raw_detections[frame][detection]["y"]
                        + raw_detections[frame][detection]["h"] / 2
                    )

                    try:
                        bbcolor = color_dict[raw_detections[frame][detection]["class"]]

                    except ValueError:
                        bbcolor = (0, 0, 255)

                    cv2.rectangle(
                        image_cache, (x_start, y_start), (x_end, y_end), bbcolor, 2
                    )

                    # einkommentieren  für
                    text_size, _ = cv2.getTextSize(
                        anno_txt, cv2.FONT_HERSHEY_SIMPLEX, fontscale, 1
                    )

                    text_w, text_h = text_size

                    cv2.rectangle(
                        image_cache,
                        (x_start - 1, y_start - 1),
                        (x_start + text_w + 2, y_start - text_h - 2),
                        bbcolor,
                        -1,
                    )

                    image = cv2.putText(
                        image_cache,
                        anno_txt,
                        (x_start, y_start - 2),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        fontscale,
                        (255, 255, 255),
                        1,
                    )

        return image

    except ImportError:
        return image
