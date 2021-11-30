import tkinter as tk
from gui_dict import gui_dict
import cv2
from PIL import Image, ImageTk


def manipulate_image(np_image, video, canvas):

    # np_image = draw_detectors_from_dict(np_image, flow_dictionary)

    # copy is important or else original image will be changed
    image = Image.fromarray(np_image)  # to PIL format

    # The variable photo is a local variable which gets garbage collected after the
    # class is instantiated. Save a reference to the photo
    # photo is attribute of video
    video.ph_image = ImageTk.PhotoImage(image)

    canvas.create_image(0, 0, anchor=tk.NW, image=video.ph_image)
