import cv2
import numpy as np
import json
import tkinter as tk
from PIL import Image, ImageTk
import keyboard


from gui_dict import gui_dict

# detectors = {}
# movement_dict = {}

# gui_dict["counting_mode"] = True

# d = {}


# detector_dic = open(
#     "C:/Users/Goerner/Desktop/code/OpenTrafficCam/OTAnalytics/tests/data//multiple_line_detectors.OTflow",
#     "r",
# )
# object_dic = open(
#     "C:/Users/Goerner/Desktop/code/OpenTrafficCam/OTAnalytics/tests/data//object_dic.json",
#     "r",
# )

# files = open(detector_dic.name, "r")
# files = files.read()

# flow_dic = json.loads(files)
# # use this
# detectors.update(flow_dic["Detectors"])
# movement_dict.update(flow_dic["Movements"])

# files = open(object_dic.name, "r")
# files = files.read()

# object_dic = json.loads(files)


# %%
def select_detector_on_canvas(
    event, canvas, detectors, mousclick_points
):  # canvas, event

    dist = 9999999

    if gui_dict["counting_mode"] is True and detectors:

        x = int(canvas.canvasx(event.x))
        y = int(canvas.canvasy(event.y))

        mouseclick = (x, y)

        mousclick_points.append(mouseclick)

        type_line = "line"

        for detector in detectors:
            detectors[detector]["color"] = (173, 255, 47)
            if detectors[detector]["type"] == type_line:
                start = (detectors[detector]["start_x"], detectors[detector]["start_y"])
                end = (detectors[detector]["end_x"], detectors[detector]["end_y"])

                nodes = (start, end)
                for n in nodes:

                    if distance(mouseclick, n) <= dist:

                        dist = distance(mouseclick, n)
                        pt = n
                        closest_detector = detector

        detectors[closest_detector]["color"] = (255, 102, 102)

        return detector, pt


# %%


def distance(pt_1, pt_2):
    pt_1 = np.array((pt_1[0], pt_1[1]))
    pt_2 = np.array((pt_2[0], pt_2[1]))
    return np.linalg.norm(pt_1 - pt_2)


def count_vehicle_process(event, canvas, detectors, mousclick_points):
    select_detector_on_canvas(event, canvas, detectors, mousclick_points)


def vehicle_class_capture(statepanel, canvas):
    statepanel.update_statepanel("Press button to finish process")
    canvas.update()
    while True:
        if keyboard.read_key() == "1":
            print("You pressed 1")
            break


def finish_counting(mousclick_points, statepanel, canvas):
    print(mousclick_points)
    if gui_dict["counting_mode"] and len(mousclick_points) == 1:

        vehicle_class_capture(statepanel, canvas)


# %%

# select_detector_on_canvas(detectors)


# %%


# %%
