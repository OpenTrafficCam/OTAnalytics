from OTAnalytics_dict import gui_dict
import cv2
import tkinter as tk
from PIL import Image, ImageTk

def get_coordinates_opencv(event, linepoints, canvas):


        # uses mouseevents to get coordinates (left button)
        start_x = int(canvas.canvasx(event.x))
        start_y = int(canvas.canvasy(event.y))

        linepoints[0] = (start_x, start_y)

