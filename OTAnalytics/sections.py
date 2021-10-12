from gui_dict import gui_dict
import cv2

# import tkinter as tk
from PIL import Image, ImageTk
import json
from tkinter import filedialog
from tkinter.constants import END


def get_coordinates_opencv(event, linepoints, polygonpoints, canvas):
    """Saves coordinates from canvas event to linepoint list.

    Args:
        event ([type]): [description]
        linepoints ([list]): cache of linepoints
        polygonpoints ([list]): [description]
        canvas ([type]): [description]
    """
    if gui_dict["linedetector_toggle"]:
        #  uses mouseevents to get coordinates (left button)
        start_x = int(canvas.canvasx(event.x))
        start_y = int(canvas.canvasy(event.y))
        linepoints[0] = (start_x, start_y)

    if gui_dict["polygondetector_toggle"]:
        # uses mouseevents to get coordinates (left button)
        start_x = int(canvas.canvasx(event.x))
        start_y = int(canvas.canvasy(event.y))
        polygonpoints.append((start_x, start_y))


def save_file(flow_dict):
    files = [("Files", "*.OTflow")]
    file = filedialog.asksaveasfile(filetypes=files, defaultextension=files)
    # with open(file.name, "w") as a_file:
    #     flow_dict["Detectors"] = detectors
    #     flow_dict["Movements"] = movement_dict

    # BUG: is saved as nested dictionary in a list; empty dictionary also gets dumped
    json.dump(flow_dict, file, indent=4)


# def draw_polygon(np_image, polygonpoints, canvas):

#     if gui_dict["polygondetector_toggle"] is True:

#         print(gui_dict["polygondetector_toggle"])

#         pts = np.array(polygonpoints, np.int32)
#         pts = pts.reshape((-1, 1, 2))

#         np_image = cv2.polylines(np_image, pts, True, (0, 255, 255))

#         return np_image


def draw_line(np_image, linepoints):

    if gui_dict["linedetector_toggle"]:
        # if linedetectors or gui_dict["display_all_tracks_toggle"]:
        np_image = cv2.line(np_image, linepoints[0], linepoints[1], (200, 125, 125), 3)
        image = Image.fromarray(np_image)  # to PIL format
        image = ImageTk.PhotoImage(image)  # to ImageTk format

        # else:
        #     image_cache = cv2.line(imagelist[0].copy(), linepoints[0], linepoints[1],
        #                            (255, 0, 0), 5)
        #     image = Image.fromarray(image_cache)  # to PIL format
        #     image = ImageTk.PhotoImage(image)  # to ImageTk format

        # if gui_dict["polygondetector_toggle"] is True:

        #     print(gui_dict["polygondetector_toggle"])

        #     np_image = cv2.line(np_image, polygonpoints, (173, 255, 47), 3)
        #     image = Image.fromarray(np_image)  # to PIL format
        #     image = ImageTk.PhotoImage(image)  # to ImageTk format

    return image


def load_file(detectors, movements, ListboxDetector, ListboxMovement):
    """loads detectors from a .OTSect-File."""
    filepath = filedialog.askopenfile(filetypes=[("Detectors", "*.OTflow")])
    files = open(filepath.name, "r")
    files = files.read()

    flow_dict = json.loads(files)

    detectors.update(flow_dict["Detectors"])
    movements.update(flow_dict["Movements"])

    # resets polypoints list or else creation of new polygon leads to bug
    # self.polypoints = []

    for movement in movements:
        ListboxMovement.insert(END, movement)

    for detector in detectors:
        ListboxDetector.insert(END, detector)
