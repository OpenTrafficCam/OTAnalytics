from gui_dict import gui_dict
import cv2
import tkinter as tk
from PIL import Image, ImageTk
import json
from tkinter import Listbox, filedialog

def get_coordinates_opencv(event, linepoints, canvas):

        if gui_dict["linedetector_toggle"]:

                # uses mouseevents to get coordinates (left button)
                start_x = int(canvas.canvasx(event.x))
                start_y = int(canvas.canvasy(event.y))

                linepoints[0] = (start_x, start_y)

        else:
                # uses mouseevents to get coordinates (left button)
                start_x = int(canvas.canvasx(event.x))
                start_y = int(canvas.canvasy(event.y))

                print(start_x,start_y)
                
                return start_x, start_y

def save_file(combined_dic, linedetectors, movement_dict):
        files = [('Files', '*.OTflow')]
        file = filedialog.asksaveasfile(filetypes = files, defaultextension = files)

        a_file = open(file.name, "w")

        combined_dic["Detectors"] = linedetectors
        combined_dic["Movements"] = movement_dict

        #BUG: is saved as nested dictionary in a list; empty dictionary also gets dumped
        json.dump(combined_dic, a_file, indent=4)

        a_file.close()


def draw_line(linedetectors, imagelist, linepoints):

        m =[]

        if gui_dict["linedetector_toggle"] == True:

                if linedetectors or gui_dict["display_tracks_toggle"]:
                        
                        image_cache = cv2.line(imagelist[1].copy(),linepoints[0],linepoints[1],(255,0,0),5)


                else:

                        image_cache = cv2.line(imagelist[0].copy(),linepoints[0],linepoints[1],(255,0,0),5)
                
                image = Image.fromarray(image_cache) # to PIL format
                image = ImageTk.PhotoImage(image) # to ImageTk format 

                return image
                
def load_file(linedetectors, movement_dict, ListboxDetector, ListboxMovement):
        """loads detectors from a .OTSect-File 
        """

        filepath = filedialog.askopenfile(filetypes=[("Detectors", '*.OTflow')])   
        files = open(filepath.name, "r")
        files = files.read()

        loaded_dict = json.loads(files)

        linedetectors.update(loaded_dict["Detectors"])
        movement_dict.update(loaded_dict["Movements"])

        # resets polypoints list or else creation of new polygon leads to bug
        #self.polypoints = []

        for movement in movement_dict:

                ListboxMovement.insert(0,movement)


                                
        for detector in linedetectors:

                ListboxDetector.insert(0, detector)

        ListboxMovement.select_set(0)
