import json
from tkinter import filedialog

from gui_helper import button_bool, color_dict


def load_trackfile():

    filepath = filedialog.askopenfile(filetypes=[("Tracks", "*.ottrk")])
    files = open(filepath.name, "r")
    return files.read()


def load_and_convert(autoimport=False, filepath=None):
    """loads detectors from a .Track-File and converts into displayable format"""

    if not autoimport:
        filepath = load_trackfile()

    tracks = {}

    loaded_dict = json.loads(filepath)

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
