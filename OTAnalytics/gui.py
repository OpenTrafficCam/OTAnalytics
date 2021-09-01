import math
import sys
import tkinter as tk
from tkinter import Toplevel, filedialog
from tkinter.constants import END
import time

import cv2
import numpy as np
from PIL import Image, ImageTk

from auto_counting import automated_counting
from gui_dict import (button_display_tracks_toggle, button_information_line,
                      button_information_polygon, button_play_video_toggle,
                      gui_dict)
from movement import add_to_movement, curselected_movement, new_movement
from sections import draw_line, get_coordinates_opencv, load_file, save_file
from tracks import load_tracks, draw_tracks, draw_bounding_box
import timeit


class MainWindow(tk.Frame):
    """Mainwindow with initial dictionaries.

    Args:
        tk.frame ([tkinterframe]): important for the process of grouping and organizing
        other widgets in a somehow friendly way. It works like a container,
        which is responsible for arranging the position of other widgets.
    """
    def __init__(self, master):
        """Initialise window."""
        # dictionary of videoobjects
        self.videos = {}
        # dictionary of linedetectors, include id, start point, end point
        self.linepoints = [(0, 0), (0, 0)]
        self.polygonpoints = []
        # dictionary of linedetectors, include id, start point, end point
        self.polygondetectors = {}

        # only to dump detectors and movements
        self.flow_dict = {}

        # updated when flow-dictionary is loaded
        self.flow_dict["Detectors"] = {}
        self.flow_dict["Movements"] = {}
        self.object_dict = {}
        self.videoobject = None

        self.raw_detections = {}

        # list to scroll through frames
        self.framelist = []
        self.selectionlist = []
        self.counter = 0
        self.interval = 20

        # auxilery list for polygondetector creation/gets deleted after polygon creation
        self.polypoints = []

        # imagelist with original and altered images, zeros are placeholder
        self.imagelist = [0, 0]

        self.master = master
        self.frame = tk.Frame(self.master)
        self.frame.grid()
        self.master.title("OTAnalytics")

        self.Listboxvideo = tk.Listbox(self.frame)
        self.Listboxvideo.grid(row=0, column=0, columnspan=7, sticky="ew")
        self.Listboxvideo.bind('<<ListboxSelect>>', self.curselected_video)

        self.Buttonaddvideo = tk.Button(self.frame, text="Add",
                                        command=lambda:
                                        MainWindow.load_video_and_frame(self))

        self.Buttonaddvideo.grid(row=1, column=0, sticky="ew")

        self.ButtonPlayVideo = tk.Button(self.frame, text="Play", command=lambda:
                                         [button_play_video_toggle(
                                          self.ButtonPlayVideo), self.play_video()])

        self.ButtonPlayVideo.grid(row=1, column=1, columnspan=1, sticky="ew")

        self.Button3 = tk.Button(self.frame, text="Clear")
        self.Button3.grid(row=1, column=2, sticky="ew")

        self.ListboxDetector = tk.Listbox(self.frame)
        self.ListboxDetector.grid(row=2, column=0, columnspan=3, sticky="ew")
        self.ListboxDetector.bind('<<ListboxSelect>>', self.curselected_detetector)

        self.ListboxTracks = tk.Listbox(self.frame, selectmode='multiple',
                                        exportselection=False)
        self.ListboxTracks.grid(row=2, column=3, columnspan=4, sticky="ew")
        self.ListboxTracks.bind('<<ListboxSelect>>', self.curselected_track)

        self.ButtonLine = tk.Button(self.frame, text="Line", command=lambda:
                                    button_information_line(self.ButtonLine,
                                                            self.statepanel))
        self.ButtonLine.grid(row=3, column=0, sticky="ew")

        self.ButtonPoly = tk.Button(self.frame, text="Polygon", command=lambda:
                                    button_information_polygon(self.ButtonPoly,
                                                               self.statepanel))
        self.ButtonPoly.grid(row=3, column=1, sticky="ew")

        self.Button5 = tk.Button(self.frame, text="Rename")
        self.Button5.grid(row=3, column=2, sticky="ew")

        self.ButtonDeleteDetector = tk.Button(self.frame, text="Remove", command=lambda:
                                              MainWindow.delete_selected_detector(self))
        self.ButtonDeleteDetector.grid(row=3, column=3, sticky="ew")

        self.ButtonDisplayTracks = tk.Button(self.frame, width=10, text="show tracks",
                                             command=lambda:
                                             [button_display_tracks_toggle(
                                              self.ButtonDisplayTracks),
                                              self.create_canvas_picture()])

        self.ButtonDisplayTracks.grid(row=3, column=4, sticky="ew")

        self.Button9 = tk.Button(self.frame, text="Add to movement", command=lambda:
                                 add_to_movement(self.ListboxDetector,
                                                 self.ListboxMovement,
                                                 self.flow_dict["Detectors"],
                                                 self.polygondetectors,
                                                 self.flow_dict["Movements"],
                                                 self.ListBoxMovement))

        self.Button9.grid(row=4, column=0, columnspan=3, sticky="ew")

        self.ButtonLoadTracks = tk.Button(self.frame, text="Load tracks",
                                          command=lambda:
                                          [load_tracks(self.object_dict,
                                           self.raw_detections,
                                           self.ListboxTracks),
                                           self.draw_detectors_from_dict()])

        self.ButtonLoadTracks.grid(row=1, column=3, columnspan=4, sticky="ew")

        self.ButtonAutocount = tk.Button(self.frame, text="autocount", command=lambda:
                                        [automated_counting(self.flow_dict["Movements"],
                                         self.flow_dict["Detectors"],
                                         self.object_dict)])
        self.ButtonAutocount.grid(row=4, column=3, columnspan=4, sticky="ew")

        self.ListBoxMovement_detector = tk.Listbox(self.frame, width=25)
        self.ListBoxMovement_detector.grid(row=5, column=3, columnspan=4, sticky="ew")

        self.ButtonNewMovement = tk.Button(self.frame, text="New", command=lambda:
                                           new_movement(self.ListboxMovement,
                                                        self.flow_dict["Movements"]))
        self.ButtonNewMovement.grid(row=6, column=0, sticky="ew")

        self.Button11 = tk.Button(self.frame, text="Rename")
        self.Button11.grid(row=6, column=1, sticky="ew")

        self.Button12 = tk.Button(self.frame, text="Remove")
        self.Button12.grid(row=6, column=2, sticky="ew")

        self.Button13 = tk.Button(self.frame, text="Clear")
        self.Button13.grid(row=6, column=3, sticky="ew")

        self.ButtonSaveFlow = tk.Button(self.frame, text="Save", command=lambda:
                                        save_file(self.flow_dict,
                                                  self.flow_dict["Detectors"],
                                                  self.flow_dict["Movements"]))
        self.ButtonSaveFlow.grid(row=6, column=4, sticky="ew")

        self.ButtonLoadFlow = tk.Button(self.frame, text="Load", command=lambda:
                                        [load_file(self.flow_dict["Detectors"],
                                         self.flow_dict["Movements"],
                                         self.ListboxDetector,
                                         self.ListboxMovement),
                                         self.create_canvas_picture()])

        self.ButtonLoadFlow.grid(row=6, column=5, sticky="ew")

        self.ListboxMovement = tk.Listbox(self.frame, width=25, exportselection=False)
        self.ListboxMovement.grid(row=5, column=0, columnspan=3, sticky="ew")
        self.ListboxMovement.bind('<<ListboxSelect>>', lambda event:
                                curselected_movement(event,
                                self.ListBoxMovement_detector,
                                self.ListboxMovement,
                                self.flow_dict["Movements"],
                                self.statepanel))

    def load_video_and_frame(self):
        """ask for videofile via dialogue
        creates canvas on masterframe with height and width from the videoobject
        first frame is canvas image
        includes mouse motion and button press events
        """
        # opens dialog to load video file
        video_source = filedialog.askopenfile(filetypes=[("Videofiles", '*.mkv'),
                                              ("Videofiles", '*.mp4')])
        video_source = video_source.name
        video_name = video_source.split('/')[-1]

        self.statepanel = StatePanel(self.frame, 7, 0, sticky="w", columnspan=8)
        self.statepanel.update_statepanel("statepanel initialized")

        # creates Videoobject
        # key is the name of the object
        self.videos[video_name] = Video(video_source)
        self.videoobject = self.videos[video_name]

        # creates image from video
        self.image_original = cv2.cvtColor(self.videoobject.cap.read()[1],
                                           cv2.COLOR_BGR2RGB)  # to RGB
       
        # copy is important or else original image will be changed
        self.image = Image.fromarray(self.image_original.copy())  # to PIL format

        self.image = ImageTk.PhotoImage(self.image)  # to ImageTk format

        self.imagelist[0] = self.image_original

        # puts image on canvas
        self.canvas = tk.Canvas(self.frame, width=self.videoobject.width,
                                height=self.videoobject.height, bg="white")
        # prevents canvas from scrolling
        self.canvas.configure(scrollregion=(0, 0, self.videoobject.width,
                              self.videoobject.height))
        self.canvas.bind("<ButtonPress-1>", lambda event: get_coordinates_opencv(event,
                         self.linepoints, self.polypoints, self.canvas))
        self.canvas.bind("<B1-Motion>", self.draw_line_with_mousedrag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.canvas.bind("<MouseWheel>", lambda event: self.scroll_through_video(event))
        self.canvas.bind("<ButtonPress-2>")

        self.canvas.grid(row=0, rowspan=7, column=7, sticky="n")

        # puts the image from the videosourse on canvas
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image)

        # fills listbox with added video
        filename = self.videoobject.filename

        self.Listboxvideo.insert(0, filename)

    def scroll_through_video(self, event):
        """lets you scroll through the video with the mousewheel

        Args:
            event ([mousewheel]): mousewheel up and mouswheel down
        """

        # integer of mousewheel scroll event
        i = 1*event.delta//120

        if i > 0:

            _, frame = self.videoobject.cap.read()

            print(frame)

            self.framelist.append(frame)

            self.image_original = cv2.cvtColor(self.framelist[self.counter],
                                               cv2.COLOR_BGR2RGB)

            self.imagelist[0] = self.image_original

            draw_bounding_box(self.raw_detections, str(self.counter+1), self.image_original)

            self.create_canvas_picture()


            self.counter += 1

        if i < 0 and self.counter >= 1:
            self.counter -= 1

            self.image_original = cv2.cvtColor(
                self.framelist[self.counter], cv2.COLOR_BGR2RGB)  # to RGB

            self.imagelist[0] = self.image_original

            draw_bounding_box(self.raw_detections, str(self.counter+1), self.image_original)

            self.create_canvas_picture()

        # prints size of images
        print(sys.getsizeof(self.framelist))

    def draw_tracks_from_dict(self):
        """Draws tracks using distinct dictionary."""
        # if detectors exist in dictionary and "display tracks-button"
        # is pressed then use the altered picture

        if gui_dict["display_all_tracks_toggle"] is True:

            # if self.flow_dict["Detectors"]:
            #     print(bool(self.flow_dict["Detectors"]))

            #     self.image_cache = self.imagelist[1].copy()

            # else:
            #     self.image_cache = self.imagelist[0].copy()
            #     print("this pic is used 0")

            #self.imagelist[0] = 

            
            for track in self.object_dict:

                trackcolor = (0, 0, 255)

                if self.object_dict[track]["Class"] == "car":
                    trackcolor = (255, 0, 0)
                if self.object_dict[track]["Class"] == "person":
                    trackcolor = (0, 255, 0)
                if self.object_dict[track]["Class"] == "motorcycle":
                    trackcolor = (240, 248, 255)

                
                pts = np.array(self.object_dict[track]["Coord"], np.int32)

                pts = pts.reshape((-1, 1, 2))
                
                self.image = cv2.polylines(self.image_cache, [pts], False,
                                           color=trackcolor, thickness=2)
                self.imagelist[1] = self.image_cache
                self.image = Image.fromarray(self.image_cache)  # to PIL format
                self.image = ImageTk.PhotoImage(self.image)  # to ImageTk format

                self.canvas.create_image(0, 0, image=self.image, anchor=tk.NW)

        # else:
        #     if self.flow_dict["Detectors"]:

        #         print(bool(self.flow_dict["Detectors"]))

        #         self.image_cache = self.imagelist[1].copy()

        #     else:
        #         self.image_cache = self.imagelist[0].copy()
        #         print("this pic is used 0")

        else:
            if self.selectionlist:
                for track in self.selectionlist:
                    trackcolor = (0, 0, 255)

                    if self.object_dict[track]["Class"] == "car":
                        trackcolor = (255, 0, 0)
                    if self.object_dict[track]["Class"] == "person":
                        trackcolor = (0, 255, 0)
                    if self.object_dict[track]["Class"] == "motorcycle":
                        trackcolor = (240, 248, 255)

                    pts = np.array(self.object_dict[track]["Coord"], np.int32)

                    pts = pts.reshape((-1, 1, 2))

                    self.image = cv2.polylines(self.image_cache, [pts], False,
                                            color=trackcolor, thickness=2)

                    self.imagelist[1] = self.image_cache
                    self.image = Image.fromarray(self.image_cache)  # to PIL format
                    self.image = ImageTk.PhotoImage(self.image)  # to ImageTk format

                    self.canvas.create_image(0, 0, image=self.image, anchor=tk.NW)

    def curselected_track(self,  event):
        """Draws one or more selected tracks on canvas."""

        #self.draw_detectors_from_dict()
        self.widget = event.widget
        multiselection = self.widget.curselection()

        self.selectionlist = []

        for selection in multiselection:
            entry = self.widget.get(selection)
            self.selectionlist.append(entry)

        self.create_canvas_picture()

    def draw_line_with_mousedrag(self, event):
        """Lets the user use click and drag to draw a line.

        Args:
            event (event): click on canvas represents the event
        """
        if gui_dict["linedetector_toggle"] is True:

            self.end_x = int(self.canvas.canvasx(event.x))
            self.end_y = int(self.canvas.canvasy(event.y))

            self.linepoints[1] = (self.end_x, self.end_y)

            w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
            if event.x > 0.9*w:
                self.canvas.xview_scroll(1, 'units')
            elif event.x < 0.1*w:
                self.canvas.xview_scroll(-1, 'units')
            if event.y > 0.9*h:
                self.canvas.yview_scroll(1, 'units')
            elif event.y < 0.1*h:
                self.canvas.yview_scroll(-1, 'units')

            image = self.create_canvas_picture()

            print(type(image))

            self.image = draw_line(
                image, self.linepoints)

            self.canvas.create_image(0, 0, image=self.image, anchor=tk.NW)

    def on_button_release(self, event):
        """Creates toplevel window to enter detector name."""
        if gui_dict["linedetector_toggle"] is True and len(self.linepoints) == 2:

            # creates window to insert name of detector
            # if self.new_linedetector_creation_buttonClicked == True:
            self.new_detector_creation = Toplevel()
            self.new_detector_creation.title("Create new section")
            self.detector_name_entry = tk.Entry(self.new_detector_creation,
                                                textvariable="Sectionname")
            self.detector_name_entry.grid(row=1, column=0, sticky="w", pady=10, padx=10)
            self.detector_name_entry.delete(0, END)
            self.add_section = tk.Button(self.new_detector_creation, text="Add section",
                                         command=self.recieve_detectorname)
            self.add_section.grid(row=1, column=1, sticky="w", pady=10, padx=10)
            self.new_detector_creation.protocol("WM_DELETE_WINDOW",  self.on_close)
            # makes the background window unavailable
            self.new_detector_creation.grab_set()

    def curselected_detetector(self, event):
        """Re draws detectors, where the selected detectors has different color

        Args:
            event (Listboxselection): single listboxselection
        """

        self.widget = event.widget
        self.selection = self.widget.curselection()

        detector_name = self.widget.get(self.selection[0])

        for dict_key in self.flow_dict["Detectors"].keys():

            if detector_name == dict_key:

                self.flow_dict["Detectors"][detector_name]["color"] = (0, 0, 255)

            else:
                self.flow_dict["Detectors"][dict_key]["color"] = (255, 0, 0)

        self.create_canvas_picture()

    def on_close(self):
        """Deletes polygon or line on canvas if entered string is none."""
        self.create_canvas_picture()

        self.new_detector_creation.destroy()

    def recieve_detectorname(self):
        # TODO outsource this function
        # takes the new created section and adds it to the listbox

        detector_name = self.detector_name_entry.get()

        if gui_dict["linedetector_toggle"] is True:
            self.flow_dict["Detectors"][detector_name] = {
                'type': 'line',
                'start_x': self.linepoints[0][0],
                'start_y': self.linepoints[0][1],
                'end_x': self.linepoints[1][0],
                'end_y': self.linepoints[1][1],
                'color': (255, 0, 0)}

        self.create_canvas_picture()

        self.ListboxDetector.insert(0, detector_name)

        self.new_detector_creation.destroy()

    def delete_selected_detector(self):
        # gets selection from listbox
        # delete from dict and re draw detectors on canvas
        detector_name = self.ListboxDetector.get(self.ListboxDetector.curselection())

        if gui_dict["linedetector_toggle"] is True:  # WRONG

            self.ListboxDetector.delete(self.ListboxDetector.curselection())

            del self.flow_dict["Detectors"][detector_name]

            # check if detetector is in movement and delete as well

            for movement in self.flow_dict["Movements"]:
                if detector_name in self.flow_dict["Movements"][movement]:
                    self.flow_dict["Movements"][movement].remove(detector_name)

                    # BUG
                    if self.ListboxMovement.get(
                       self.ListboxMovement.curselection()) == movement:

                        self.ListBoxMovement.delete(0, 'end')

                        for detector_name in self.flow_dict["Movements"][movement]:
                            self.ListBoxMovement.insert(0, detector_name)

        # if not self.flow_dict["Detectors"]:
        #     # deletes polygon
        #     self.image = Image.fromarray(self.imagelist[0].copy())  # to PIL format
        #     self.image = ImageTk.PhotoImage(self.image)  # to ImageTk format

        #     self.canvas.create_image(0, 0, image=self.image, anchor=tk.NW)

        self.create_canvas_picture()

    def curselected_video(self, event):
        """Selected video from Listboxvideo-Listbox gets displayed on canvas.

        Args:
            event (Listselection): Event is the selection via mousepress
        """
        # return selected videoname, puts frame of selected image on canvas
        self.widget = event.widget
        self.selection = self.widget.curselection()

        video_name = self.widget.get(self.selection[0])

        # print(video_name)
        self.videoobject = self.videos[video_name]

        # creates image from video
        self.image = cv2.cvtColor(self.videoobject.cap.read()[-1],
                                  cv2.COLOR_BGR2RGB)  # to RGB
        self.image = Image.fromarray(self.image)  # to PIL format
        self.image = ImageTk.PhotoImage(self.image)  # to ImageTk format
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image)

    def draw_detectors_from_dict(self, np_image):

        m = [0, 1]

        # takes original picture
        # np_image = self.image_originale

        if self.flow_dict["Detectors"]:

            for linedetectors in self.flow_dict["Detectors"]:

                start_x = self.flow_dict["Detectors"][linedetectors]["start_x"]
                start_y = self.flow_dict["Detectors"][linedetectors]["start_y"]
                end_x = self.flow_dict["Detectors"][linedetectors]["end_x"]
                end_y = self.flow_dict["Detectors"][linedetectors]["end_y"]
                color = self.flow_dict["Detectors"][linedetectors]["color"]

                np_image = cv2.line(np_image, (start_x, start_y),
                                            (end_x, end_y), color, 3)

                # draws ellipse around detectors
                m[0] = math.ceil(((start_x+end_x)/2))
                m[1] = math.ceil(((start_y+end_y)/2))

                d = math.ceil((math.sqrt((end_x-start_x)**2+(end_y-start_y)**2)))
                d = math.ceil(d/2)

                angle = math.degrees((math.atan2((end_y-start_y), (end_x-start_x))))

                np_image = cv2.ellipse(np_image, (m[0], m[1]),
                                               (d, 50), angle, 0, 360,
                                               (255, 0, 0), 3)

            return np_image

                #self.image = Image.fromarray(self.image_cache)  # to PIL format
                #self.image = ImageTk.PhotoImage(self.image)  # to ImageTk format

                #self.canvas.create_image(0, 0, image=self.image, anchor=tk.NW)

        else:
            return np_image
            # self.image = Image.fromarray(self.image_cache)  # to PIL format
            # self.image = ImageTk.PhotoImage(self.image)  # to ImageTk format
            # self.canvas.create_image(0, 0, image=self.image, anchor=tk.NW)

        #self.draw_tracks_from_dict()

    def create_canvas_picture(self):
        # TODO wsfsdf

        np_image = self.imagelist[0].copy()

        print(type(np_image))

        np_image = self.draw_detectors_from_dict(np_image)

        np_image = draw_tracks(self.selectionlist, self.object_dict, np_image)


        # here draw tracks

        self.image = Image.fromarray(np_image)  # to PIL format
        self.image = ImageTk.PhotoImage(self.image)  # to ImageTk format

        self.canvas.create_image(0, 0, image=self.image, anchor=tk.NW)

        # draw tracks
        # use image_cache to transforn to PIL image and so on
        return np_image

    def play_video(self):
        """Play video on button press
        """
        frame_delay = 1/self.videoobject.fps

        print(frame_delay)

        while gui_dict["play_video"] is True:

            time.sleep(frame_delay)

            _, frame = self.videoobject.cap.read()

            print(frame)

            self.framelist.append(frame)

            self.image_original = cv2.cvtColor(self.framelist[self.counter],
                                                cv2.COLOR_BGR2RGB)

            self.imagelist[0] = self.image_original

            draw_bounding_box(self.raw_detections, str(self.counter+1), self.image_original)

            self.create_canvas_picture()

            self.canvas.update()

            self.ButtonPlayVideo.update()

            self.counter += 1




class Video:
    """Videoclass that gets created on importing video."""
    # objekt which contains relevant information of the video
    def __init__(self, filepath) -> None:
        """Initial class information from videofile.

        Args:
            filepath ([string]): string representaition of filepath
        """

        # self.id = id
        self.filepath = filepath
        self.filename = filepath.split('/')[-1]

        # opens video source
        self.cap = cv2.VideoCapture(self.filepath)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)

        # retrieve dimensions of video
        self.width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)


class StatePanel:
    """Statepanel that contains usefull information."""
    # initialize StatePanel
    def __init__(self, window, row, column, sticky, columnspan):
        """Initial class information.

        Args:
            window ([tkinter Frame]): window where statepanel ist shown.
            row ([tk row]): [row number]
            column ([tk column]): [column number]
            sticky ([arg]): [text alignment]
            columnspan ([arg]): [button span]
        """
        self.scrollbar = tk.Scrollbar(window)
        self.text = tk.Text(window, height=4, width=150,
                            yscrollcommand=self.scrollbar.set,
                            state="disabled")
        self.scrollbar.config(command=self.text.yview)
        self.scrollbar.grid(row=row, column=column, columnspan=2, padx='5', pady='3',
                            sticky='e')
        self.text.grid(row=row, column=column, padx='5', pady='3',
                       sticky=sticky, columnspan=columnspan)

    def update_statepanel(self, text):
        """Function to update statepanel with wanted text.

        Args:
            text ([string]): [text to be shown]
        """
        self.text.config(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert(tk.END, str(text))
        self.text.see("end")
        self.text.config(state="disabled")

    def move(self, row, column, sticky, columnspan=2):
        """Scroll thru statepanel text.

        Args:
            row ([tk row]): [row number]
            column ([tk column]): [column number]
            sticky ([arg]): [text alignment]
            columnspan (int, optional): [description]. Defaults to 2.
        """
        self.scrollbar.grid(row=row, column=column, padx='5', pady='3',
                            sticky='e')
        self.text.grid(row=row, column=column, padx='5', pady='3', sticky=sticky,
                       columnspan=columnspan)


def main():
    """Main function."""
    root = tk.Tk()
    MainWindow(root)
    root.mainloop()


if __name__ == '__main__':
    main()
