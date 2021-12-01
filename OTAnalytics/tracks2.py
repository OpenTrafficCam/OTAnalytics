import json
from tkinter import filedialog

import cv2
import numpy as np
from gui_helper import color_dict, button_bool


def load_tracks():
    """loads detectors from a .Track-File and converts into displayable format"""

    filepath = filedialog.askopenfile(filetypes=[("Tracks", "*.ottrk")])
    files = open(filepath.name, "r")
    files = files.read()

    tracks = {}

    loaded_dict = json.loads(files)

    # raw detections from OTVision
    raw_detections = loaded_dict["data"]

    for frame in raw_detections:
        for detection in raw_detections[frame]:
            if "object_" + str(detection) in tracks.keys():
                tracks["object_%s" % detection]["Coord"].append(
                    [
                        raw_detections[frame][detection]["x"],
                        raw_detections[frame][detection]["y"],
                    ]
                )

                tracks["object_%s" % detection]["Frame"].append(int(frame))

            elif raw_detections[frame][detection]["class"] in color_dict.keys():
                tracks["object_%s" % detection] = {}
                tracks["object_%s" % detection]["Coord"] = []
                tracks["object_%s" % detection]["Frame"] = [int(frame)]
                tracks["object_%s" % detection]["Class"] = raw_detections[frame][
                    detection
                ]["class"]
                tracks["object_%s" % detection]["Coord"].append(
                    [
                        raw_detections[frame][detection]["x"],
                        raw_detections[frame][detection]["y"],
                    ]
                )
    button_bool["tracks_imported"] = True

    return raw_detections, tracks
