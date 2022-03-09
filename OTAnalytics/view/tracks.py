import json
from tkinter import filedialog

from gui_helper import button_bool, color_dict


def load_trackfile():

    filepath = filedialog.askopenfile(filetypes=[("Tracks", "*.ottrk")])
    files = open(filepath.name, "r")
    return files.read()


def load_and_convert(x_factor, y_factor, autoimport=False, filepath=None):
    """loads detectors from a .Track-File and converts into displayable format"""

    if not autoimport:
        filepath = load_trackfile()

    tracks = {}

    loaded_dict = json.loads(filepath)

    # raw detections from OTVision
    raw_detections = loaded_dict["data"]

    for frame in raw_detections:
        for detection in raw_detections[frame]:
            if f"object_{str(detection)}" in tracks:
                tracks["object_%s" % detection]["Coord"].append(
                    [
                        raw_detections[frame][detection]["x"] * x_factor,
                        raw_detections[frame][detection]["y"] * y_factor,
                    ]
                )

                tracks["object_%s" % detection]["Frame"].append(int(frame))

            elif raw_detections[frame][detection]["class"] in color_dict.keys():
                tracks["object_%s" % detection] = {
                    "Coord": [],
                    "Frame": [int(frame)],
                    "Class": raw_detections[frame][detection]["class"],
                }

                tracks["object_%s" % detection]["Coord"].append(
                    [
                        raw_detections[frame][detection]["x"] * x_factor,
                        raw_detections[frame][detection]["y"] * y_factor,
                    ]
                )
    button_bool["tracks_imported"] = True

    return raw_detections, tracks
