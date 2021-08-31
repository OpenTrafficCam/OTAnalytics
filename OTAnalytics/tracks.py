from gui_dict import gui_dict
import json
from tkinter import filedialog
import cv2


def load_tracks(object_dict,raw_detections, ListboxTracks):
    """loads detectors from a .Track-File and converts into displayable format
    """

    filepath = filedialog.askopenfile(filetypes=[("Detectors", '*.ottrk')])
    files = open(filepath.name, "r")
    files = files.read()

    loaded_dict = json.loads(files)

    detections = {}

    raw_detections.update(loaded_dict["data"])

    for seconds in raw_detections:
        for detection in raw_detections[seconds]:
            if 'object_'+str(detection) in object_dict.keys():
                object_dict['object_%s' % detection]["Coord"].append(
                    [raw_detections[seconds][detection]["x"],
                     raw_detections[seconds][detection]["y"]])
            else:
                object_dict['object_%s' % detection] = {}
                object_dict['object_%s' % detection]["Coord"] = []
                object_dict['object_%s' % detection]["Second"] = int(seconds)
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


def save_object_dic(object_dict):
    # experimental function / not necessary for end product

    json.dump(object_dict, open("object_dic.json", 'w'), indent=4)


def draw_bounding_box(raw_detections, frame, image):

    image_cache = image

    for detection in raw_detections[frame]:

        x_start = int(raw_detections[frame][detection]["x"]-30)
        y_start = int(raw_detections[frame][detection]["y"]-30)

        x_end = int(raw_detections[frame][detection]["x"]+30)
        y_end = int(raw_detections[frame][detection]["y"]+30)



        image_cache = cv2.rectangle(image_cache, (x_start,y_start), (x_end,y_end ), (255, 0, 0), 2)

        print(raw_detections[frame][detection])

    return image



