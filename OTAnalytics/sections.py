from gui_dict import gui_dict
import cv2
# import tkinter as tk
from PIL import Image, ImageTk
import json
from tkinter import filedialog


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
        print(polygonpoints)


def save_file(flow_dict, linedetectors, movement_dict):
    files = [('Files', '*.OTflow')]
    file = filedialog.asksaveasfile(filetypes=files, defaultextension=files)
    a_file = open(file.name, "w")
    flow_dict["Detectors"] = linedetectors
    flow_dict["Movements"] = movement_dict

    # BUG: is saved as nested dictionary in a list; empty dictionary also gets dumped
    json.dump(flow_dict, a_file, indent=4)
    a_file.close()


def draw_line(linedetectors, imagelist, linepoints):

    if gui_dict["linedetector_toggle"] is True:
        if linedetectors or gui_dict["display_tracks_toggle"]:
            image_cache = cv2.line(imagelist[1].copy(), linepoints[0], linepoints[1],
                                   (255, 0, 0), 5)
            image = Image.fromarray(image_cache)  # to PIL format
            image = ImageTk.PhotoImage(image)  # to ImageTk format

        else:
            image_cache = cv2.line(imagelist[0].copy(), linepoints[0], linepoints[1],
                                   (255, 0, 0), 5)
            image = Image.fromarray(image_cache)  # to PIL format
            image = ImageTk.PhotoImage(image)  # to ImageTk format

        return image

    if gui_dict["polygondetector_toggle"] is True:
        pass


def load_file(linedetectors, movements, ListboxDetector, ListboxMovement):
    """loads detectors from a .OTSect-File."""
    filepath = filedialog.askopenfile(filetypes=[("Detectors", '*.OTflow')])
    files = open(filepath.name, "r")
    files = files.read()

    flow_dict = json.loads(files)

    linedetectors.update(flow_dict["Detectors"])
    movements.update(flow_dict["Movements"])

    # resets polypoints list or else creation of new polygon leads to bug
    # self.polypoints = []

    print(flow_dict)

    for movement in movements:
        ListboxMovement.insert(0, movement)

    for detector in linedetectors:
        ListboxDetector.insert(0, detector)

    ListboxMovement.select_set(0)
