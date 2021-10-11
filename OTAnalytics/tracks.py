from numpy.typing import _32Bit
from gui_dict import gui_dict
import json
from tkinter import filedialog
import cv2
import numpy as np


def load_tracks(object_dict, raw_detections, ListboxTracks):
    """loads detectors from a .Track-File and converts into displayable format"""

    filepath = filedialog.askopenfile(filetypes=[("Detectors", "*.ottrk")])
    files = open(filepath.name, "r")
    files = files.read()

    loaded_dict = json.loads(files)

    # detections = {}

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

            else:
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

        ListboxTracks.insert(0, object)

    save_object_dic(object_dict)

    gui_dict["tracks_imported"] = True


def draw_tracks(selectionlist, object_dict, np_image):

    if gui_dict["display_all_tracks_toggle"] is True:

        for track in object_dict:

            trackcolor = (0, 0, 255)

            if object_dict[track]["Class"] == "car":
                trackcolor = (255, 0, 0)
            if object_dict[track]["Class"] == "person":
                trackcolor = (0, 255, 0)
            if object_dict[track]["Class"] == "motorcycle":
                trackcolor = (240, 248, 255)

            pts = np.array(object_dict[track]["Coord"], np.int32)

            pts = pts.reshape((-1, 1, 2))

            np_image = cv2.polylines(
                np_image, [pts], False, color=trackcolor, thickness=2
            )

        return np_image

    elif selectionlist:

        for object_id in selectionlist:

            trackcolor = (0, 0, 255)

            if object_dict[object_id]["Class"] == "car":
                trackcolor = (255, 0, 0)
            if object_dict[object_id]["Class"] == "person":
                trackcolor = (0, 255, 0)
            if object_dict[object_id]["Class"] == "motorcycle":
                trackcolor = (240, 248, 255)

            pts = np.array(object_dict[object_id]["Coord"], np.int32)

            pts = pts.reshape((-1, 1, 2))

            np_image = cv2.polylines(
                np_image, [pts], False, color=trackcolor, thickness=2
            )

        return np_image

    else:
        return np_image


def save_object_dic(object_dict):
    # experimental function / not necessary for end product

    json.dump(object_dict, open("object_dic.json", "w"), indent=4)


def draw_bounding_box(raw_detections, frame, image):
    """draws bounding box in every frame

    Args:
        raw_detections ([type]): [description]
        frame ([int]): index of frame
        image ([type]): image to draw on

    Returns:
        [type]: returns manipulated image
    """

    if raw_detections:

        image_cache = image

        for detection in raw_detections[frame]:

            class_txt = raw_detections[frame][detection]["class"]

            confidence_txt = round((raw_detections[frame][detection]["conf"]), 2)

            anno_txt = class_txt + " " + str(confidence_txt)

            if (raw_detections[frame][detection]["w"] / 100) < 0.3:
                fontscale = 0.3
            elif (raw_detections[frame][detection]["w"] / 100) > 0.5:
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

            cv2.rectangle(
                image_cache, (x_start, y_start), (x_end, y_end), (255, 50, 50), 2
            )

            #einkommentieren  für 
            # text_size, _ = cv2.getTextSize(
            #     anno_txt, cv2.FONT_HERSHEY_SIMPLEX, fontscale, 1
            # )

            # text_w, text_h = text_size

            # cv2.rectangle(
            #     image_cache,
            #     (x_start, y_start - 2),
            #     (x_start + text_w, y_start - text_h),
            #     (0, 0, 0),
            #     -1,
            #)

            image = cv2.putText(
                image_cache,
                anno_txt,
                (x_start, y_start - 2),
                cv2.FONT_HERSHEY_SIMPLEX,
                fontscale,
                (255, 50, 50),
                1,
            )

        return image

    else:

        pass
