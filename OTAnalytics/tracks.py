from gui_dict import gui_dict
import json
from tkinter import filedialog
import cv2
import numpy as np


def load_tracks(object_dict, raw_detections, ListboxTracks):
    """loads detectors from a .Track-File and converts into displayable format
    """

    filepath = filedialog.askopenfile(filetypes=[("Detectors", '*.ottrk')])
    files = open(filepath.name, "r")
    files = files.read()

    loaded_dict = json.loads(files)

    # detections = {}

    raw_detections.update(loaded_dict["data"])

    for seconds in raw_detections:
        for detection in raw_detections[seconds]:
            if 'object_'+str(detection) in object_dict.keys():
                object_dict['object_%s' % detection]["Coord"].append(
                    [raw_detections[seconds][detection]["x"],
                     raw_detections[seconds][detection]["y"]])

                object_dict['object_%s' % detection]["Second"].append(int(seconds))

            else:
                object_dict['object_%s' % detection] = {}
                object_dict['object_%s' % detection]["Coord"] = []
                object_dict['object_%s' % detection]["Second"] = [int(seconds)]
                object_dict['object_%s' % detection]["Class"] = raw_detections[
                                                                seconds][detection][
                                                                "class"]
                object_dict['object_%s' % detection]["Coord"].append(
                    [raw_detections[seconds][detection]["x"],
                     raw_detections[seconds][detection]["y"]])

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

            np_image = cv2.polylines(np_image, [pts], False,
                                     color=trackcolor, thickness=2)

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
                np_image, [pts], False, color=trackcolor, thickness=2)

        return np_image

    else:
        return np_image


def save_object_dic(object_dict):
    # experimental function / not necessary for end product

    json.dump(object_dict, open("object_dic.json", 'w'), indent=4)


def draw_bounding_box(raw_detections, frame, image):

    if raw_detections:

        image_cache = image

        for detection in raw_detections[frame]:

            x_start = int(raw_detections[frame][detection]["x"]-30)
            y_start = int(raw_detections[frame][detection]["y"]-30)

            x_end = int(raw_detections[frame][detection]["x"]+30)
            y_end = int(raw_detections[frame][detection]["y"]+30)

            image_cache = cv2.rectangle(image_cache, (x_start, y_start), (x_end, y_end),
                                        (255, 0, 0), 2)

            print(raw_detections[frame][detection])

        return image

    else:

        pass
