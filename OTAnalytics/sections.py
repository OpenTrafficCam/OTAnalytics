from OTAnalytics_dict import gui_dict
import cv2
import tkinter as tk
from PIL import Image, ImageTk
import json
from tkinter import filedialog

def get_coordinates_opencv(event, linepoints, canvas):


        # uses mouseevents to get coordinates (left button)
        start_x = int(canvas.canvasx(event.x))
        start_y = int(canvas.canvasy(event.y))

        linepoints[0] = (start_x, start_y)

def save_detectors(linedetectors, polygondetectors):
        files = [('Files', '*.OTSect')]
        file = filedialog.asksaveasfile(filetypes = files, defaultextension = files)

        a_file = open(file.name, "w")

        #BUG: is saved as nested dictionary in a list; empty dictionary also gets dumped
        json.dump([linedetectors, polygondetectors], a_file)

        a_file.close()


def draw_line(linedetectors, imagelist, linepoints):

        if gui_dict["linedetector_toggle"] == True:

                if linedetectors:

                        image_cache = cv2.line(imagelist[1].copy(),linepoints[0],linepoints[1],(255,0,0),5)

                else:

                        image_cache = cv2.line(imagelist[0].copy(),linepoints[0],linepoints[1],(255,0,0),5)
                
                image = Image.fromarray(image_cache) # to PIL format
                image = ImageTk.PhotoImage(image) # to ImageTk format 

                return image
