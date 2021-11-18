import tkinter as tk
from tkinter import Toplevel, filedialog
from tkinter.constants import END, HORIZONTAL
import time
import keyboard

import cv2
import numpy as np
from PIL import Image, ImageTk

from auto_counting import create_setting_window

from counting import (
    select_detector_on_canvas,
    count_vehicle_process,
    finish_counting,
)
from gui_dict import (
    button_display_bb,
    button_display_tracks_toggle,
    button_information_line,
    button_information_polygon,
    button_play_video_toggle,
    button_rewind_video_toggle,
    button_manuel_count,
    button_display_live_track,
    gui_dict,
)
from movement import add_to_movement, curselected_movement, new_movement
from sections import (
    draw_line,
    get_coordinates_opencv,
    load_file,
    save_file,
)
from tracks import load_tracks, draw_tracks, draw_bounding_box, draw_tracks_live


class MainWindow(tk.Frame):
    """Mainwindow with initial dictionaries.

    Args:
        tk.frame (tkinterframe): important for the process of grouping and organizing
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

        # only to dump detectors and movements
        self.flow_dict = {"Detectors": {}, "Movements": {}}

        self.object_dict = {}
        self.object_live_track = {}
        self.videoobject = None

        self.raw_detections = {}
        self.mousclick_points = []

        self.selectionlist = []
        self.counter = 0
        self.interval = 20

        # auxilery list for polygondetector creation/gets deleted after polygon creation
        self.polypoints = []

        # imagelist with original and altered images, zeros are placeholder
        self.imagelist = [0, 0]

        # number of frame in the video
        self.value = tk.DoubleVar()

        self.master = master
        self.frame = tk.Frame(self.master)
        self.frame.grid()
        self.master.title("OTAnalytics")

        self.videolabel = tk.Label(
            self.frame, text="Videos and Tracks", fg="white", bg="#37483E"
        )
        self.videolabel.grid(row=0, column=0, columnspan=7, sticky="ew")
        self.listbox_video = tk.Listbox(self.frame, height=3)
        self.listbox_video.grid(row=1, column=0, columnspan=7, sticky="ew")
        self.listbox_video.bind("<<ListboxSelect>>", self.curselected_video)

        self.button_addvideo = tk.Button(
            self.frame,
            text="Add",
            command=lambda: MainWindow.load_video_and_frame(self),
        )

        self.button_addvideo.grid(row=2, column=0, sticky="ew")

        self.button_playvideo = tk.Button(
            self.frame,
            text="Play",
            command=lambda: [
                button_play_video_toggle(
                    self.button_playvideo, self.button_rewindvideo
                ),
                self.play_video(),
            ],
        )
        self.button_playvideo.grid(row=2, column=1, columnspan=1, sticky="ew")

        self.button_rewindvideo = tk.Button(
            self.frame,
            text="Rewind",
            command=lambda: [
                button_rewind_video_toggle(
                    self.button_rewindvideo, self.button_playvideo
                ),
                self.rewind_video(),
            ],
        )

        self.button_rewindvideo.grid(row=2, column=2, columnspan=1, sticky="ew")

        self.button_clear = tk.Button(self.frame, text="Clear")
        self.button_clear.grid(row=2, column=3, sticky="ew")

        self.detectionlabel = tk.Label(
            self.frame, text="Sections and Objects", fg="white", bg="#37483E"
        )
        self.detectionlabel.grid(row=3, column=0, columnspan=7, sticky="ew")

        self.listbox_detector = tk.Listbox(self.frame, height=8)
        self.listbox_detector.grid(row=4, column=0, columnspan=3, sticky="ew")
        self.listbox_detector.bind("<<ListboxSelect>>", self.curselected_detetector)

        self.listbox_tracks = tk.Listbox(
            self.frame, selectmode="multiple", exportselection=False, height=8
        )
        self.listbox_tracks.grid(row=4, column=3, columnspan=4, sticky="ew")
        self.listbox_tracks.bind("<<ListboxSelect>>", self.curselected_track)

        self.button_line = tk.Button(
            self.frame,
            text="Line",
            command=lambda: button_information_line(
                self.button_line, self.button_poly, self.statepanel
            ),
        )
        self.button_line.grid(row=5, column=0, sticky="ew")

        self.button_poly = tk.Button(
            self.frame,
            text="Polygon",
            command=lambda: button_information_polygon(
                self.button_poly, self.button_line, self.statepanel
            ),
        )
        self.button_poly.grid(row=5, column=1, sticky="ew")

        self.button_delete_detector = tk.Button(
            self.frame,
            text="Remove",
            command=lambda: MainWindow.delete_selected_detector(self),
        )
        self.button_delete_detector.grid(row=5, column=2, sticky="ew")

        self.button_display_tracks = tk.Button(
            self.frame,
            text="show tracks",
            command=lambda: [
                button_display_tracks_toggle(self.button_display_tracks),
                self.create_canvas_picture(),
            ],
        )

        self.button_display_tracks.grid(row=5, column=3, sticky="ew")

        self.button_display_boundingbox = tk.Button(
            self.frame,
            text="show bb",
            command=lambda: [
                button_display_bb(self.button_display_boundingbox),
                self.create_canvas_picture(),
            ],
        )

        self.button_display_boundingbox.grid(row=5, column=5, sticky="ew")

        self.button_display_livetracks = tk.Button(
            self.frame,
            text="Livetrack",
            command=lambda: [
                button_display_live_track(self.button_display_livetracks),
                self.create_canvas_picture(),
            ],
        )

        self.button_display_livetracks.grid(row=5, column=4, sticky="ew")

        self.button_add_to_movement = tk.Button(
            self.frame,
            text="Add to movement",
            command=lambda: add_to_movement(
                self.listbox_detector,
                self.listbox_movement,
                self.flow_dict["Detectors"],
                self.flow_dict["Movements"],
                self.listbox_movement_detector,
            ),
        )

        self.button_add_to_movement.grid(row=6, column=0, columnspan=3, sticky="ew")

        self.button_load_tracks = tk.Button(
            self.frame,
            text="Load tracks",
            command=lambda: [
                load_tracks(
                    self.object_dict,
                    self.object_live_track,
                    self.raw_detections,
                    self.listbox_tracks,
                ),
                self.create_canvas_picture(),
            ],
        )

        self.button_load_tracks.grid(row=2, column=4, columnspan=3, sticky="ew")

        self.button_autocount = tk.Button(
            self.frame,
            text="autocount",
            command=lambda: [
                create_setting_window(
                    self.videoobject.fps,
                    self.flow_dict["Movements"],
                    self.flow_dict["Detectors"],
                    self.object_dict,
                )
            ],
        )
        self.button_autocount.grid(row=6, column=3, columnspan=1, sticky="ew")

        self.button_manuel_count = tk.Button(
            self.frame,
            text="count",
            command=lambda: button_manuel_count(
                self.button_manuel_count,
            ),
        )

        self.button_manuel_count.grid(row=6, column=4, columnspan=2, sticky="ew")

        self.movementlabel = tk.Label(
            self.frame, text="Movements", fg="white", bg="#37483E"
        )
        self.movementlabel.grid(row=7, column=0, columnspan=7, sticky="ew")

        self.listbox_movement_detector = tk.Listbox(self.frame, width=25)
        self.listbox_movement_detector.grid(row=8, column=3, columnspan=4, sticky="ew")

        self.button_new_movement = tk.Button(
            self.frame,
            text="New",
            command=lambda: new_movement(
                self.listbox_movement, self.flow_dict["Movements"]
            ),
        )
        self.button_new_movement.grid(row=9, column=0, sticky="ew")

        self.button_rename = tk.Button(self.frame, text="Rename")
        self.button_rename.grid(row=9, column=1, sticky="ew")

        self.button_remove_movement = tk.Button(
            self.frame,
            text="Remove",
            command=lambda: MainWindow.delete_selected_movement(self),
        )
        self.button_remove_movement.grid(row=9, column=2, sticky="ew")

        self.button_remove = tk.Button(self.frame, text="Clear")
        self.button_remove.grid(row=9, column=3, sticky="ew")

        self.button_save_flow = tk.Button(
            self.frame,
            text="Save",
            command=lambda: save_file(self.flow_dict),
        )
        self.button_save_flow.grid(row=9, column=4, sticky="ew")

        self.button_load_flow = tk.Button(
            self.frame,
            text="Load",
            command=lambda: [
                load_file(
                    self.flow_dict["Detectors"],
                    self.flow_dict["Movements"],
                    self.listbox_detector,
                    self.listbox_movement,
                ),
                self.create_canvas_picture(),
            ],
        )

        self.button_load_flow.grid(row=9, column=5, sticky="ew")

        self.listbox_movement = tk.Listbox(self.frame, width=25, exportselection=False)
        self.listbox_movement.grid(row=8, column=0, columnspan=3, sticky="ew")
        self.listbox_movement.bind(
            "<<ListboxSelect>>",
            lambda event: curselected_movement(
                event,
                self.listbox_movement_detector,
                self.listbox_movement,
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

        self.statepanel = StatePanel(
            self.frame, 10, 0, sticky="nswe", rowspan=2, columnspan=6
        )
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
        self.canvas.bind("<MouseWheel>", lambda event: self.mouse_scroll_video(event))
        self.canvas.bind("<ButtonPress-2>", lambda event: self.draw_polygon(True))
        self.canvas.bind("<ButtonPress-3>", lambda event: self.undo_polygon_point())
        keyboard.add_hotkey("enter", lambda: self.finish_detector_creation())
        keyboard.add_hotkey("escape", lambda: self.kill_creation_process())

        self.canvas.grid(row=0, rowspan=15, column=7, sticky="n")

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
            ),  # event is the slided number/ gets triggered through mousescroll/
            # slows down videoplay
        )

        self.slider.grid(row=11, column=7, sticky="wen")

        # fills listbox with added video
        filename = self.videoobject.filename

        self.listbox_video.insert(0, filename)

    def scroll_video(self):
        if not gui_dict["play_video"] and not gui_dict["rewind_video"]:

            self.videoobject.cap.set(1, self.counter)

            _, frame = self.videoobject.cap.read()

            # self.framelist.append(frame)

            self.image_original = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            self.imagelist[0] = self.image_original

            self.create_canvas_picture()

    def slider_scroll(self, counter):
        if not gui_dict["play_video"] and not gui_dict["rewind_video"]:

            self.counter = counter

            self.scroll_video()

    def mouse_scroll_video(self, event):
        """Navigate through video with mousewheel.

        Args:
            event (mousewheel event): mousewheel up and mouswheel down
        """
        # deletes polypoint, if process of creating detector is aborted
        self.polypoints = []

        if not gui_dict["play_video"] and not gui_dict["rewind_video"]:

            # integer of mousewheel scroll event
            i = 1 * event.delta // 120

            if i > 0 and self.counter < (self.videoobject.totalframecount):

                self.value.set(self.counter)

                self.scroll_video()

                self.counter += 1

            if i < 0 and self.counter > 1:

                self.counter -= 1

                self.scroll_video()

                self.value.set(self.counter)

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
            event (event): click on canvas triggers event
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
            keyboard.remove_hotkey("enter")
            keyboard.remove_hotkey("escape")

            self.new_detector_creation.title("Create new section")
            self.detector_name_entry = tk.Entry(
                self.new_detector_creation, textvariable="Sectionname"
            )
            self.detector_name_entry.grid(row=1, column=0, sticky="w", pady=10, padx=10)
            self.detector_name_entry.delete(0, END)
            self.detector_name_entry.focus()

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

                self.flow_dict["Detectors"][detector_name]["color"] = (200, 0, 0)

            else:
                self.flow_dict["Detectors"][dict_key]["color"] = (200, 125, 125)

        self.create_canvas_picture()

    def on_close(self):
        """Deletes polygon or line on canvas if entered string is none."""
        # self.create_canvas_picture()

        keyboard.add_hotkey("enter", lambda: self.finish_detector_creation())
        keyboard.add_hotkey("escape", lambda: self.kill_creation_process())

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
                "color": (200, 125, 125),
            }

        if gui_dict["polygondetector_toggle"] is True:
            self.flow_dict["Detectors"][detector_name] = {
                "type": "polygon",
                "points": self.polypoints,
                "color": (200, 125, 125),
            }

        self.create_canvas_picture()

        self.listboxdetector.insert(0, detector_name)

        self.on_close()

    def delete_selected_detector(self):
        """Deletes in listbox selected detector."""
        # gets selection from listbox
        # delete from dict and re draw detectors on canvas
        detector_name = self.listbox_detector.get(self.listbox_detector.curselection())

        if gui_dict["linedetector_toggle"] is True:  # WRONG

            self.listbox_detector.delete(self.listbox_detector.curselection())

            del self.flow_dict["Detectors"][detector_name]

            # check if detetector is in movement and delete as well

            for movement in self.flow_dict["Movements"]:
                if detector_name in self.flow_dict["Movements"][movement]:
                    self.flow_dict["Movements"][movement].remove(detector_name)

        elif gui_dict["polygondetector_toggle"] is True:

            self.listbox_detector.delete(self.listbox_detector.curselection())

            del self.flow_dict["Detectors"][detector_name]

            # check if detetector is in movement and delete as well

            for movement in self.flow_dict["Movements"]:
                if detector_name in self.flow_dict["Movements"][movement]:
                    self.flow_dict["Movements"][movement].remove(detector_name)

        self.create_canvas_picture()

    def delete_selected_movement(self):
        movement_name = self.listbox_movement.get(self.listbox_movement.curselection())

        self.listbox_movement.delete(self.listbox_movement.curselection())

        del self.flow_dict["Movements"][movement_name]

    def curselected_video(self, event):
        """Selected video from listboxvideo-Listbox gets displayed on canvas.

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
        """Draws detectors on every frame.

        Args:
            np_image (array): image as numpy array

        Returns:
            np_image (array): returns manipulated image"""

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

                    np_image = cv2.fillPoly(overlay, [pts], (200, 125, 125))

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
        """UNUSED FUNCTION!"""

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
        """Takes manipulated np image and converts it into PIL and TKimage to plot on canvas.
        This functions represents last step of image alteration.

        Returns:
            np_image (array):
        """
        # TODO wsfsdf

        np_image = self.imagelist[0].copy()

        np_image = self.draw_detectors_from_dict(np_image)

        draw_tracks_live(
            self.object_dict,
            self.object_live_track,
            self.counter,
            self.raw_detections,
            np_image,
        )

        draw_bounding_box(self.raw_detections, str(self.counter + 1), np_image)

        draw_tracks(self.selectionlist, self.object_dict, np_image)

        # self.draw_vehicle_direction(np_image)

        self.image = Image.fromarray(np_image)  # to PIL format
        self.image = ImageTk.PhotoImage(self.image)  # to ImageTk format

        self.canvas.create_image(0, 0, image=self.image, anchor=tk.NW)

        finish_counting(self.mousclick_points, self.statepanel, self.canvas)

        return np_image

    def play_video(self):
        """Play video on button press."""
        frame_delay = 1 / self.videoobject.fps

        for object in list(self.object_dict.keys()):

            self.object_live_track[object] = []

        gui_dict["rewind_video"] = False

        while (
            gui_dict["play_video"] is True
            and self.counter < self.videoobject.totalframecount
        ):

            time.sleep(frame_delay)

            self.videoobject.cap.set(1, self.counter)

            _, frame = self.videoobject.cap.read()

            self.image_original = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            self.imagelist[0] = self.image_original

            self.create_canvas_picture()

            self.canvas.update()

            self.button_playvideo.update()

            if self.counter < self.videoobject.totalframecount - 1:
                self.counter += 1

            else:
                gui_dict["play_video"] = False

            self.slider.set(self.counter)

    def rewind_video(self):
        """Rewinds video framewise."""

        frame_delay = 1 / self.videoobject.fps

        gui_dict["play_video"] = False

        while gui_dict["rewind_video"] is True and self.counter > 1:

            time.sleep(frame_delay)

            self.videoobject.cap.set(1, self.counter)

            _, frame = self.videoobject.cap.read()

            self.image_original = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            self.imagelist[0] = self.image_original

            self.create_canvas_picture()

            self.canvas.update()

            self.buttonplayvideo.update()

            if self.counter >= 1:

                self.counter -= 1

                self.slider.set(self.counter)

    def draw_polygon(self, closing):
        """Draws a polygon on canvas.

        Args:
            closing (bool): if true create polygon else continue drawing
        """

        if not gui_dict["polygondetector_toggle"]:

            return

        image = self.create_canvas_picture()

        overlay = image.copy()

        list_of_tuples = [list(elem) for elem in self.polypoints]

        pts = np.array(list_of_tuples, np.int32)
        pts = pts.reshape((-1, 1, 2))

        if closing is not False:

            np_image = cv2.fillPoly(overlay, [pts], (200, 125, 125))
            opacity = 0.4
            np_image = cv2.addWeighted(overlay, opacity, image, 1 - opacity, 0, image)
        np_image = cv2.polylines(image, [pts], closing, (200, 125, 125), 2)

        image = Image.fromarray(np_image)  # to PIL format
        self.image = ImageTk.PhotoImage(image)  # to ImageTk format

        self.canvas.create_image(0, 0, image=self.image, anchor=tk.NW)

    def undo_polygon_point(self):
        """Deletes last point and redraws polygon"""

        del self.polypoints[-1]

        self.draw_polygon(False)

    def kill_creation_process(self):
        """Abort creation process and deletes list of points"""
        # empties list with points to create polygon
        self.polypoints = []

        self.create_canvas_picture()


class Video:
    """Videoclass that gets created on importing video."""

    # objekt which contains relevant information of the video
    def __init__(self, filepath):

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


class StatePanel:
    """Statepanel that contains usefull information."""

    # initialize StatePanel
    def __init__(self, window, row, column, sticky, rowspan, columnspan):
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
            rowspan=rowspan,
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
        """Scroll up and down statepaneltext.

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


class InfoWindow:
    def __init__(self, windowtitle, infotext):
        self.window = tk.Tk()
        self.window.title(windowtitle)
        self.window.geometry("300x200")
        self.label = tk.Label(self.window, text=infotext)
        self.label.grid(column=0, row=0)

        self.button = tk.Button(self.window)
        self.button.grid(column=0, row=1)


def main():
    """Main function."""
    root = tk.Tk()
    MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
