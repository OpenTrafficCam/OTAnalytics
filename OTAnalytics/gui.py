import math  # important for drawing ellipse with open cv
import sys
import tkinter as tk
from tkinter import Event, Toplevel, filedialog
from tkinter.constants import END, HORIZONTAL
import time
import keyboard

import cv2
import numpy as np
from PIL import Image, ImageTk

from auto_counting import automated_counting

from counting import (
    select_detector_on_canvas,
    count_vehicle_process,
    vehicle_class_capture,
    finish_counting,
)
from gui_dict import (
    button_display_tracks_toggle,
    button_information_line,
    button_information_polygon,
    button_play_video_toggle,
    button_rewind_video_toggle,
    button_manuel_count,
    gui_dict,
)
from movement import add_to_movement, curselected_movement, new_movement
from sections import (
    draw_line,
    get_coordinates_opencv,
    load_file,
    save_file,
)
from tracks import load_tracks, draw_tracks, draw_bounding_box


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
        # self.polygonpoints = []
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
        self.mousclick_points = []

        # list to scroll through frames
        self.framelist = []
        self.selectionlist = []
        self.counter = 0
        self.interval = 20

        # auxilery list for polygondetector creation/gets deleted after polygon creation
        self.polypoints = []

        # imagelist with original and altered images, zeros are placeholder
        self.imagelist = [0, 0]

        self.value = tk.DoubleVar()

        self.master = master
        self.frame = tk.Frame(self.master)
        self.frame.grid()
        self.master.title("OTAnalytics")

        self.Listboxvideo = tk.Listbox(self.frame)
        self.Listboxvideo.grid(row=0, column=0, columnspan=7, sticky="ew")
        self.Listboxvideo.bind("<<ListboxSelect>>", self.curselected_video)

        self.Buttonaddvideo = tk.Button(
            self.frame,
            text="Add",
            command=lambda: MainWindow.load_video_and_frame(self),
        )

        self.Buttonaddvideo.grid(row=1, column=0, sticky="ew")

        self.ButtonPlayVideo = tk.Button(
            self.frame,
            text="Play",
            command=lambda: [
                button_play_video_toggle(self.ButtonPlayVideo, self.ButtonRewindVideo),
                self.play_video(),
            ],
        )
        self.ButtonPlayVideo.grid(row=1, column=1, columnspan=1, sticky="ew")

        self.ButtonRewindVideo = tk.Button(
            self.frame,
            text="Rewind",
            command=lambda: [
                button_rewind_video_toggle(
                    self.ButtonPlayVideo, self.ButtonRewindVideo
                ),
                self.rewind_video(),
            ],
        )

        self.ButtonRewindVideo.grid(row=1, column=2, columnspan=1, sticky="ew")

        self.Button3 = tk.Button(self.frame, text="Clear")
        self.Button3.grid(row=1, column=3, sticky="ew")

        self.ListboxDetector = tk.Listbox(self.frame)
        self.ListboxDetector.grid(row=2, column=0, columnspan=3, sticky="ew")
        self.ListboxDetector.bind("<<ListboxSelect>>", self.curselected_detetector)

        self.ListboxTracks = tk.Listbox(
            self.frame, selectmode="multiple", exportselection=False
        )
        self.ListboxTracks.grid(row=2, column=3, columnspan=4, sticky="ew")
        self.ListboxTracks.bind("<<ListboxSelect>>", self.curselected_track)

        self.ButtonLine = tk.Button(
            self.frame,
            text="Line",
            command=lambda: button_information_line(
                self.ButtonLine, self.ButtonPoly, self.statepanel
            ),
        )
        self.ButtonLine.grid(row=3, column=0, sticky="ew")

        self.ButtonPoly = tk.Button(
            self.frame,
            text="Polygon",
            command=lambda: button_information_polygon(
                self.ButtonPoly, self.ButtonLine, self.statepanel
            ),
        )
        self.ButtonPoly.grid(row=3, column=1, sticky="ew")

        self.Button5 = tk.Button(self.frame, text="Rename")
        self.Button5.grid(row=3, column=2, sticky="ew")

        self.ButtonDeleteDetector = tk.Button(
            self.frame,
            text="Remove",
            command=lambda: MainWindow.delete_selected_detector(self),
        )
        self.ButtonDeleteDetector.grid(row=3, column=3, sticky="ew")

        self.ButtonDisplayTracks = tk.Button(
            self.frame,
            width=10,
            text="show tracks",
            command=lambda: [
                button_display_tracks_toggle(self.ButtonDisplayTracks),
                self.create_canvas_picture(),
            ],
        )

        self.ButtonDisplayTracks.grid(row=3, column=4, sticky="ew")

        self.Button9 = tk.Button(
            self.frame,
            text="Add to movement",
            command=lambda: add_to_movement(
                self.ListboxDetector,
                self.ListboxMovement,
                self.flow_dict["Detectors"],
                self.polygondetectors,
                self.flow_dict["Movements"],
                self.ListBoxMovement_detector,
            ),
        )

        self.Button9.grid(row=4, column=0, columnspan=3, sticky="ew")

        self.ButtonLoadTracks = tk.Button(
            self.frame,
            text="Load tracks",
            command=lambda: [
                load_tracks(self.object_dict, self.raw_detections, self.ListboxTracks),
                self.create_canvas_picture(),
            ],
        )

        self.ButtonLoadTracks.grid(row=1, column=4, columnspan=3, sticky="ew")

        self.ButtonAutocount = tk.Button(
            self.frame,
            text="autocount",
            command=lambda: [
                automated_counting(
                    self.videoobject.fps,
                    self.flow_dict["Movements"],
                    self.flow_dict["Detectors"],
                    self.object_dict,
                )
            ],
        )
        self.ButtonAutocount.grid(row=4, column=3, columnspan=1, sticky="ew")

        self.ButtonMancount = tk.Button(
            self.frame,
            text="count",
            command=lambda: button_manuel_count(
                self.ButtonMancount,
            ),
        )

        self.ButtonMancount.grid(row=4, column=4, columnspan=1, sticky="ew")

        self.ListBoxMovement_detector = tk.Listbox(self.frame, width=25)
        self.ListBoxMovement_detector.grid(row=5, column=3, columnspan=4, sticky="ew")

        self.ButtonNewMovement = tk.Button(
            self.frame,
            text="New",
            command=lambda: new_movement(
                self.ListboxMovement, self.flow_dict["Movements"]
            ),
        )
        self.ButtonNewMovement.grid(row=6, column=0, sticky="ew")

        self.Button11 = tk.Button(self.frame, text="Rename")
        self.Button11.grid(row=6, column=1, sticky="ew")

        self.ButtonRemoveMovement = tk.Button(
            self.frame,
            text="Remove",
            command=lambda: MainWindow.delete_selected_movement(self),
        )
        self.ButtonRemoveMovement.grid(row=6, column=2, sticky="ew")

        self.Button13 = tk.Button(self.frame, text="Clear")
        self.Button13.grid(row=6, column=3, sticky="ew")

        self.ButtonSaveFlow = tk.Button(
            self.frame,
            text="Save",
            command=lambda: save_file(self.flow_dict),
        )
        self.ButtonSaveFlow.grid(row=6, column=4, sticky="ew")

        self.ButtonLoadFlow = tk.Button(
            self.frame,
            text="Load",
            command=lambda: [
                load_file(
                    self.flow_dict["Detectors"],
                    self.flow_dict["Movements"],
                    self.ListboxDetector,
                    self.ListboxMovement,
                ),
                self.create_canvas_picture(),
            ],
        )

        self.ButtonLoadFlow.grid(row=6, column=5, sticky="ew")

        self.ListboxMovement = tk.Listbox(self.frame, width=25, exportselection=False)
        self.ListboxMovement.grid(row=5, column=0, columnspan=3, sticky="ew")
        self.ListboxMovement.bind(
            "<<ListboxSelect>>",
            lambda event: curselected_movement(
                event,
                self.ListBoxMovement_detector,
                self.ListboxMovement,
                self.flow_dict["Movements"],
                self.statepanel,
            ),
        )

    def load_video_and_frame(self):
        """ask for videofile via dialogue
        creates canvas on masterframe with height and width from the videoobject
        first frame is canvas image
        includes mouse motion and button press events
        """
        # opens dialog to load video file
        video_source = filedialog.askopenfile(
            filetypes=[("Videofiles", "*.mkv"), ("Videofiles", "*.mp4")]
        )
        video_source = video_source.name
        video_name = video_source.split("/")[-1]

        self.statepanel = StatePanel(self.frame, 7, 0, sticky="w", columnspan=6)
        self.statepanel.update_statepanel("statepanel initialized")

        # creates Videoobject
        # key is the name of the object
        self.videos[video_name] = Video(video_source)
        self.videoobject = self.videos[video_name]

        # creates image from video
        self.image_original = cv2.cvtColor(
            self.videoobject.cap.read()[1], cv2.COLOR_BGR2RGB
        )  # to RGB

        # copy is important or else original image will be changed
        self.image = Image.fromarray(self.image_original.copy())  # to PIL format

        self.image = ImageTk.PhotoImage(self.image)  # to ImageTk format

        self.imagelist[0] = self.image_original

        # puts image on canvas
        self.canvas = tk.Canvas(
            self.frame,
            width=self.videoobject.width,
            height=self.videoobject.height,
            bg="white",
        )

        # prevents canvas from scrolling
        self.canvas.configure(
            scrollregion=(0, 0, self.videoobject.width, self.videoobject.height)
        )
        self.canvas.bind(
            "<ButtonPress-1>",
            lambda event: [
                get_coordinates_opencv(
                    event, self.linepoints, self.polypoints, self.canvas
                ),
                self.draw_polygon(False),
                count_vehicle_process(
                    event,
                    self.canvas,
                    self.flow_dict["Detectors"],
                    self.mousclick_points,
                ),
                # self.create_canvas_picture(),
            ],
        )
        self.canvas.bind(
            "<B1-Motion>", lambda event: self.draw_line_with_mousedrag(event)
        )
        # self.canvas.bind("<ButtonRelease-1>", self.finish_detector_creation)
        self.canvas.bind("<MouseWheel>", lambda event: self.mouse_scroll_video(event))
        self.canvas.bind("<ButtonPress-2>", lambda event: self.draw_polygon(True))
        self.canvas.bind("<ButtonPress-3>", lambda event: self.undo_polygon_point())
        keyboard.add_hotkey("enter", lambda: self.finish_detector_creation())
        keyboard.add_hotkey("escape", lambda: self.kill_creation_process())

        self.canvas.grid(row=0, rowspan=7, column=7, sticky="n")

        # puts the image from the videosourse on canvas
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image)

        self.slider = tk.Scale(
            self.frame,
            variable=self.value,
            from_=0,
            to=self.videoobject.totalframecount - 1,
            orient=HORIZONTAL,
            command=lambda event: self.slider_scroll(
                int(event)
            ),  # event is the slided number/ gets triggered through mousescroll/ slows down videoplay
        )

        self.slider.grid(row=7, column=7, sticky="wen")

        # fills listbox with added video
        filename = self.videoobject.filename

        self.Listboxvideo.insert(0, filename)

    def scroll_video(self, counter):

        _, frame = self.videoobject.cap.read()

        self.framelist.append(frame)

        self.image_original = cv2.cvtColor(self.framelist[counter], cv2.COLOR_BGR2RGB)

        self.imagelist[0] = self.image_original

        draw_bounding_box(self.raw_detections, str(counter + 1), self.image_original)

        self.create_canvas_picture()

    def slider_scroll(self, counter):
        self.counter = counter

        self.scroll_video(self.counter)

    def mouse_scroll_video(self, event):
        """lets you scroll through the video with the mousewheel

        Args:
            event ([mousewheel]): mousewheel up and mouswheel down
        """
        # deletes polypoint, if process of creating detector is aborted
        self.polypoints = []

        # integer of mousewheel scroll event
        i = 1 * event.delta // 120

        if i > 0 and self.counter < self.videoobject.totalframecount:

            self.scroll_video(self.counter)

            self.value.set(self.counter)

            self.counter += 1

        if i < 0 and self.counter >= 1:

            self.counter -= 1

            self.value.set(self.counter)

            self.scroll_video(self.counter)

        # prints size of images
        # print(sys.getsizeof(self.framelist))

    def curselected_track(self, event):
        """Draws one or more selected tracks on canvas."""

        # self.draw_detectors_from_dict()
        self.widget = event.widget
        multiselection = self.widget.curselection()

        self.selectionlist = []

        for selection in multiselection:
            entry = self.widget.get(selection)
            self.selectionlist.append(entry)

        self.create_canvas_picture()

    def left_button_click(self, event, canvas):

        select_detector_on_canvas(event, canvas)

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
            if event.x > 0.9 * w:
                self.canvas.xview_scroll(1, "units")
            elif event.x < 0.1 * w:
                self.canvas.xview_scroll(-1, "units")
            if event.y > 0.9 * h:
                self.canvas.yview_scroll(1, "units")
            elif event.y < 0.1 * h:
                self.canvas.yview_scroll(-1, "units")

            image = self.create_canvas_picture()

            self.image = draw_line(image, self.linepoints)

            self.canvas.create_image(0, 0, image=self.image, anchor=tk.NW)

    def finish_detector_creation(self):
        """Creates toplevel window to enter detector name."""
        if (
            gui_dict["linedetector_toggle"] is True
            and len(self.linepoints) == 2
            or gui_dict["polygondetector_toggle"]
        ):

            # creates window to insert name of detector
            # if self.new_linedetector_creation_buttonClicked == True:
            self.new_detector_creation = Toplevel()
            self.new_detector_creation.title("Create new section")
            self.detector_name_entry = tk.Entry(
                self.new_detector_creation, textvariable="Sectionname"
            )
            self.detector_name_entry.grid(row=1, column=0, sticky="w", pady=10, padx=10)
            self.detector_name_entry.delete(0, END)
            self.add_section = tk.Button(
                self.new_detector_creation,
                text="Add section",
                command=self.recieve_detectorname,
            )
            self.add_section.grid(row=1, column=1, sticky="w", pady=10, padx=10)
            self.new_detector_creation.protocol("WM_DELETE_WINDOW", self.on_close)
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
                self.flow_dict["Detectors"][dict_key]["color"] = (173, 255, 47)

        self.create_canvas_picture()

    def on_close(self):
        """Deletes polygon or line on canvas if entered string is none."""
        # self.create_canvas_picture()

        self.new_detector_creation.destroy()

    def recieve_detectorname(self):
        # TODO outsource this function
        # takes the new created section and adds it to the listbox

        detector_name = self.detector_name_entry.get()

        if gui_dict["linedetector_toggle"] is True:
            self.flow_dict["Detectors"][detector_name] = {
                "type": "line",
                "start_x": self.linepoints[0][0],
                "start_y": self.linepoints[0][1],
                "end_x": self.linepoints[1][0],
                "end_y": self.linepoints[1][1],
                "color": (173, 255, 47),
            }

        if gui_dict["polygondetector_toggle"] is True:
            self.flow_dict["Detectors"][detector_name] = {
                "type": "polygon",
                "points": self.polypoints,
                "color": (173, 255, 47),
            }

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

        elif gui_dict["polygondetector_toggle"] is True:

            self.ListboxDetector.delete(self.ListboxDetector.curselection())

            del self.flow_dict["Detectors"][detector_name]

            # check if detetector is in movement and delete as well

            for movement in self.flow_dict["Movements"]:
                if detector_name in self.flow_dict["Movements"][movement]:
                    self.flow_dict["Movements"][movement].remove(detector_name)

        self.create_canvas_picture()

    def delete_selected_movement(self):
        movement_name = self.ListboxMovement.get(self.ListboxMovement.curselection())

        self.ListboxMovement.delete(self.ListboxMovement.curselection())

        del self.flow_dict["Movements"][movement_name]

        print(self.flow_dict["Movements"])

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
        self.image = cv2.cvtColor(
            self.videoobject.cap.read()[-1], cv2.COLOR_BGR2RGB
        )  # to RGB
        self.image = Image.fromarray(self.image)  # to PIL format
        self.image = ImageTk.PhotoImage(self.image)  # to ImageTk format
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image)

    def draw_detectors_from_dict(self, np_image):

        # m = [0, 1]

        # takes original picture
        # np_image = self.image_originale

        Line = "line"

        if self.flow_dict["Detectors"]:

            for detector in self.flow_dict["Detectors"]:
                if self.flow_dict["Detectors"][detector]["type"] == Line:
                    start_x = self.flow_dict["Detectors"][detector]["start_x"]
                    start_y = self.flow_dict["Detectors"][detector]["start_y"]
                    end_x = self.flow_dict["Detectors"][detector]["end_x"]
                    end_y = self.flow_dict["Detectors"][detector]["end_y"]
                    color = self.flow_dict["Detectors"][detector]["color"]

                    np_image = cv2.line(
                        np_image, (start_x, start_y), (end_x, end_y), color, 3
                    )

                else:

                    # dont know why
                    image = np_image
                    overlay = image.copy()

                    polypoints = self.flow_dict["Detectors"][detector]["points"]
                    color = self.flow_dict["Detectors"][detector]["color"]

                    list_of_tuples = [list(elem) for elem in polypoints]
                    pts = np.array(list_of_tuples, np.int32)
                    pts = pts.reshape((-1, 1, 2))

                    np_image = cv2.fillPoly(overlay, [pts], (255, 255, 0))

                    opacity = 0.4
                    np_image = cv2.addWeighted(overlay, opacity, image, 1 - opacity, 0)
                    np_image = cv2.polylines(np_image, [pts], True, color, 2)

                # TODO ASK IF ELLIPSE AROUND SECTION IS USEFUL

                # # draws ellipse around detectors
                # m[0] = math.ceil(((start_x + end_x) / 2))
                # m[1] = math.ceil(((start_y + end_y) / 2))

                # d = math.ceil(
                #     (math.sqrt((end_x - start_x) ** 2 + (end_y - start_y) ** 2))
                # )
                # d = math.ceil(d / 2)

                # angle = math.degrees((math.atan2((end_y - start_y),
                #  (end_x - start_x))))

                # np_image = cv2.ellipse(
                #     np_image, (m[0], m[1]), (d, 50), angle, 0, 360, (255, 0, 0), 3
                # )

                # indent if necessary again
                # self.image = Image.fromarray(self.image_cache)  # to PIL format
                # self.image = ImageTk.PhotoImage(self.image)  # to ImageTk format

                # self.canvas.create_image(0, 0, image=self.image, anchor=tk.NW)

        return np_image

    def draw_vehicle_direction(self, np_image):

        if gui_dict["counting_mode"] is True and len(self.mousclick_points) == 2:

            np_image = cv2.line(
                np_image,
                self.mousclick_points[0],
                self.mousclick_points[1],
                (255, 102, 102),
                2,
            )

            self.mousclick_points = []

            gui_dict["during_counting_process"] = True

        return np_image

    def create_canvas_picture(self):
        # TODO wsfsdf

        np_image = self.imagelist[0].copy()

        np_image = self.draw_detectors_from_dict(np_image)

        np_image = draw_tracks(self.selectionlist, self.object_dict, np_image)

        np_image = self.draw_vehicle_direction(np_image)

        self.image = Image.fromarray(np_image)  # to PIL format
        self.image = ImageTk.PhotoImage(self.image)  # to ImageTk format

        self.canvas.create_image(0, 0, image=self.image, anchor=tk.NW)

        finish_counting(self.mousclick_points, self.statepanel, self.canvas)

        # draw tracks
        # use image_cache to transforn to PIL image and so on
        return np_image

    def play_video(self):
        """Play video on button press"""
        frame_delay = 1 / self.videoobject.fps

        print(frame_delay)

        gui_dict["rewind_video"] = False

        while gui_dict["play_video"] is True:

            time.sleep(frame_delay)

            _, frame = self.videoobject.cap.read()

            self.framelist.append(frame)

            self.image_original = cv2.cvtColor(
                self.framelist[self.counter], cv2.COLOR_BGR2RGB
            )

            self.imagelist[0] = self.image_original

            draw_bounding_box(
                self.raw_detections, str(self.counter + 1), self.image_original
            )

            self.create_canvas_picture()

            self.canvas.update()

            self.ButtonPlayVideo.update()

            self.counter += 1

            self.slider.set(self.counter)

    def rewind_video(self):

        frame_delay = 1 / self.videoobject.fps

        gui_dict["play_video"] = False

        while gui_dict["rewind_video"] is True:

            time.sleep(frame_delay)

            # _, frame = self.videoobject.cap.read()

            # self.framelist.append(frame)

            self.image_original = cv2.cvtColor(
                self.framelist[self.counter], cv2.COLOR_BGR2RGB
            )

            self.imagelist[0] = self.image_original

            draw_bounding_box(
                self.raw_detections, str(self.counter + 1), self.image_original
            )

            self.create_canvas_picture()

            self.canvas.update()

            self.ButtonPlayVideo.update()

            self.counter -= 1

            self.slider.set(self.counter)

    def draw_polygon(self, closing):

        if gui_dict["polygondetector_toggle"] is True:

            image = self.create_canvas_picture()

            overlay = image.copy()

            list_of_tuples = [list(elem) for elem in self.polypoints]

            print(gui_dict["polygondetector_toggle"])

            pts = np.array(list_of_tuples, np.int32)
            pts = pts.reshape((-1, 1, 2))

            if closing is False:

                np_image = cv2.polylines(image, [pts], closing, (255, 255, 0), 2)

            else:

                np_image = cv2.fillPoly(overlay, [pts], (255, 255, 0))
                opacity = 0.4
                np_image = cv2.addWeighted(
                    overlay, opacity, image, 1 - opacity, 0, image
                )
                np_image = cv2.polylines(image, [pts], closing, (255, 255, 0), 2)

            image = Image.fromarray(np_image)  # to PIL format
            self.image = ImageTk.PhotoImage(image)  # to ImageTk format

            self.canvas.create_image(0, 0, image=self.image, anchor=tk.NW)

    def undo_polygon_point(self):

        del self.polypoints[-1]

        self.draw_polygon(False)

    def kill_creation_process(self):
        self.polypoints = []

        self.create_canvas_picture()


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
        self.filename = filepath.split("/")[-1]

        # opens video source
        self.cap = cv2.VideoCapture(self.filepath)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)

        # retrieve dimensions of video
        self.width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

        self.totalframecount = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

        print(self.totalframecount)
        print(type(self.totalframecount))


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
        self.text = tk.Text(
            window,
            height=3,
            width=50,
            yscrollcommand=self.scrollbar.set,
            state="disabled",
        )
        self.scrollbar.config(command=self.text.yview)
        self.scrollbar.grid(
            row=row, column=column, columnspan=2, padx="5", pady="3", sticky="w"
        )
        self.text.grid(
            row=row,
            column=column,
            padx="5",
            pady="3",
            sticky=sticky,
            columnspan=columnspan,
        )

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
        self.scrollbar.grid(row=row, column=column, padx="5", pady="3", sticky="e")
        self.text.grid(
            row=row,
            column=column,
            padx="5",
            pady="3",
            sticky=sticky,
            columnspan=columnspan,
        )


def main():
    """Main function."""
    root = tk.Tk()
    MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
