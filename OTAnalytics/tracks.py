from gui_dict import *
import json
from tkinter import Listbox, filedialog


def load_tracks(object_dict, ListboxTracks):
    """loads detectors from a .Track-File and converts into displayable format
    """

    filepath = filedialog.askopenfile(filetypes=[("Detectors", '*.ottrk')])
    files = open(filepath.name, "r")
    files = files.read()

    loaded_dict = json.loads(files)

    detections = {}

    detections.update(loaded_dict["data"])


    for seconds in detections:
        print(seconds)
        for detection in detections[seconds]:
            if 'object_'+str(detection) in object_dict.keys():
                object_dict['object_%s' % detection]["Coord"].append([detections[seconds][detection]["x"], detections[seconds][detection]["y"]])
            else:
                object_dict['object_%s' % detection] = {}
                object_dict['object_%s' % detection]["Coord"] = []
                object_dict['object_%s' % detection]["Second"] = int(seconds) 
                object_dict['object_%s' % detection]["Class"] = detections[seconds][detection]["class"]
                object_dict['object_%s' % detection]["Coord"].append([detections[seconds][detection]["x"], detections[seconds][detection]["y"]])
    

    for object in list(object_dict.keys()):

        ListboxTracks.insert(0,object)

    save_object_dic(object_dict)

    gui_dict["tracks_imported"] = True

def save_object_dic(object_dict):

    json.dump(object_dict,open( "object_dic.json", 'w' ) ,indent=4)

