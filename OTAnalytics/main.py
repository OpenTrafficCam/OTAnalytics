import time
import tkinter as tk
from tkinter.constants import CENTER, END, HORIZONTAL
from tkinter import ttk

import keyboard

from auto_counting import create_setting_window
from canvas_class import OtcCanvas
from gui_helper import (
    button_bool,
    button_display_bb_switch,
    button_display_live_track_switch,
    button_display_tracks_switch,
    button_line_switch,
    button_play_video_switch,
    button_polygon_switch,
    button_rewind_switch,
    statepanel_txt,
)
from image_alteration import manipulate_image
from sections import (
    draw_line,
    draw_polygon,
    dump_to_flowdictionary,
    load_flowfile,
    save_flowfile,
)
from statepanel_class import StatePanel
from tracks import load_tracks
from video import load_video_and_frame


class MainWindow(tk.Frame):
    """Mainwindow with initial dictionaries.

    Args:
        tk.frame (tkinter.frame): important for the process of grouping and organizing
        other widgets in a somehow friendly way. It works like a container,
        which is responsible for arranging the position of other widgets.
    """

    def __init__(self, master, **kwargs):
        super().__init__(**kwargs)
        self.master = master
        self.frame = tk.Frame(self.master)
        self.frame.grid()
        self.master.title("OTAnalytics")

        self.flow_dict = {"Detectors": {}, "Movements": {}}
        self.selectionlist = []
        self.raw_detections = []
        self.tracks = {}
        self.tracks_live = {}

        self.slider_value = tk.DoubleVar

        self.statepanelobject = StatePanel(
            self.frame, 10, 0, sticky="nsew", rowspan=2, columnspan=6
        )

        videolabel = tk.Label(
            master=self.frame, text="Videos and Tracks", fg="white", bg="#37483E"
        )
        videolabel.grid(row=0, column=0, columnspan=7, sticky="ew")
        self.listbox_video = tk.Listbox(self.frame, height=3, exportselection=False)
        self.listbox_video.grid(row=1, column=0, columnspan=7, sticky="ew")

        button_addvideo = tk.Button(
            self.frame, text="Add", command=lambda: self.create_canvas_and_videoobject()
        )

        button_addvideo.grid(row=2, column=0, sticky="ew")

        button_playvideo = tk.Button(
            self.frame,
            text="Play",
            command=lambda: [
                button_play_video_switch(button_playvideo, button_rewindvideo),
                self.delete_polygon_points(),
                self.play_video(),
            ],
        )
        button_playvideo.grid(row=2, column=1, columnspan=1, sticky="ew")

        button_rewindvideo = tk.Button(
            self.frame,
            text="Rewind",
            command=lambda: [
                button_rewind_switch(button_rewindvideo, button_playvideo),
                self.delete_polygon_points(),
                self.rewind_video(),
            ],
        )

        button_rewindvideo.grid(row=2, column=2, columnspan=1, sticky="ew")

        button_clear = tk.Button(self.frame, text="Clear")
        button_clear.grid(row=2, column=3, sticky="ew")

        button_load_tracks = tk.Button(
            self.frame, text="Load tracks", command=lambda: self.get_tracks()
        )
        button_load_tracks.grid(row=2, column=4, columnspan=3, sticky="ew")

        detectionlabel = tk.Label(
            self.frame, text="Sections and Objects", fg="white", bg="#37483E"
        )
        detectionlabel.grid(row=3, column=0, columnspan=7, sticky="ew")

        self.style = ttk.Style()
        self.style.theme_use("default")
        self.style.configure(
            "Treeview", highlightthickness=0, bd=0, font=("Calibri", 11)
        )

        self.treeview_sections = ttk.Treeview(
            self.frame, style="Treeview", height=8, selectmode="browse"
        )

        self.treeview_sections["columns"] = "Section"
        self.treeview_sections.column("Section", anchor=CENTER, width=50)
        self.treeview_sections.heading("Section", text="Section", anchor=CENTER)
        self.treeview_sections["show"] = "headings"
        self.treeview_sections.grid(row=4, column=0, columnspan=3, sticky="nsew")

        self.treeview_tracks = ttk.Treeview(
            self.frame, style="Treeview", height=8, selectmode="extended"
        )

        self.treeview_tracks["columns"] = ("ID", "Class")

        self.treeview_tracks.column("ID", anchor=CENTER, width=25)
        self.treeview_tracks.column("Class", anchor="w", width=50)
        self.listbox_tree_scrollbar = ttk.Scrollbar(
            self.frame, orient="vertical", command=self.treeview_tracks.yview
        )

        self.treeview_tracks.heading("ID", text="ID", anchor=CENTER)
        self.treeview_tracks.heading("Class", text="Class", anchor=CENTER)

        self.treeview_tracks["show"] = "headings"
        self.treeview_tracks.grid(row=4, column=3, columnspan=3, sticky="ew")
        self.listbox_tree_scrollbar.grid(row=4, column=6, sticky="ns")

        self.treeview_tracks.configure(yscrollcommand=self.listbox_tree_scrollbar.set)

        button_line = tk.Button(
            self.frame,
            text="Line",
            command=lambda: button_line_switch(
                button_line, button_poly, self.statepanelobject
            ),
        )
        button_line.grid(row=5, column=0, sticky="ew")

        button_poly = tk.Button(
            self.frame,
            text="Polygon",
            command=lambda: button_polygon_switch(
                button_poly, button_line, self.statepanelobject
            ),
        )
        button_poly.grid(row=5, column=1, sticky="ew")

        button_delete_detector = tk.Button(
            self.frame, text="Remove", command=lambda: self.delete_section()
        )
        button_delete_detector.grid(row=5, column=2, sticky="ew")

        self.button_display_tracks = tk.Button(
            self.frame,
            text="Show tracks",
        )

        self.button_display_tracks.grid(row=5, column=3, sticky="ew")

        self.button_display_boundingbox = tk.Button(self.frame, text="Show bb")

        self.button_display_boundingbox.grid(row=5, columnspan=2, column=5, sticky="ew")

        self.button_display_livetracks = tk.Button(
            self.frame, text="Livetrack", command=lambda: self.display_tracks_live()
        )

        self.button_display_livetracks.grid(row=5, column=4, sticky="ew")

        self.button_add_to_movement = tk.Button(
            self.frame,
            text="Add to movement",
        )

        self.button_add_to_movement.grid(row=6, column=0, columnspan=3, sticky="ew")

        self.button_autocount = tk.Button(
            self.frame,
            text="autocount",
        )
        self.button_autocount.grid(row=6, column=3, columnspan=1, sticky="ew")

        movementlabel = tk.Label(self.frame, text="Movements", fg="white", bg="#37483E")
        movementlabel.grid(row=7, column=0, columnspan=7, sticky="ew")

        self.listbox_movement = tk.Listbox(self.frame, width=25, exportselection=False)
        self.listbox_movement.grid(row=8, column=0, columnspan=3, sticky="ew")

        self.listbox_movement_detector = tk.Listbox(
            self.frame, width=25, exportselection=False
        )
        self.listbox_movement_detector.grid(row=8, column=3, columnspan=4, sticky="ew")

        self.button_new_movement = tk.Button(
            self.frame,
            text="New",
        )
        self.button_new_movement.grid(row=9, column=0, sticky="ew")

        button_rename = tk.Button(self.frame, text="Rename")
        button_rename.grid(row=9, column=1, sticky="ew")

        button_remove_movement = tk.Button(
            self.frame,
            text="Remove",
        )
        button_remove_movement.grid(row=9, column=2, sticky="ew")

        button_remove = tk.Button(self.frame, text="Clear")
        button_remove.grid(row=9, column=3, sticky="ew")

        button_save_flow = tk.Button(
            self.frame, text="Save", command=lambda: save_flowfile(self.flow_dict)
        )
        button_save_flow.grid(row=9, column=4, sticky="ew")

        button_load_flow = tk.Button(
            self.frame, text="Load", command=lambda: self.get_detectors()
        )

        button_load_flow.grid(row=9, columnspan=2, column=5, sticky="ew")

    def create_canvas_and_videoobject(self):
        # load video object

        global videoobject
        global maincanvas

        videoobject = load_video_and_frame()

        first_frame = videoobject.get_frame(np_image=False)

        # hotkeys
        keyboard.add_hotkey(
            "enter",
            lambda: self.create_section_entry_window(),
        )

        # create canvas from videoobject
        maincanvas = OtcCanvas(
            width=videoobject.width, height=videoobject.height, master=self.frame
        )

        maincanvas.configure(scrollregion=(0, 0, videoobject.width, videoobject.height))

        maincanvas.bind(
            "<MouseWheel>",
            lambda event: [
                self.scroll_through_video(event),
            ],
        )

        maincanvas.bind(
            "<ButtonPress-1>",
            lambda event: [
                maincanvas.click_receive_coordinates(event, 0),
                draw_polygon(
                    event,
                    videoobject,
                    maincanvas,
                    self.flow_dict,
                    self.selectionlist,
                    self.tracks,
                    self.tracks_live,
                    self.raw_detections,
                    adding_points=True,
                ),
            ],
        )

        maincanvas.bind(
            "<ButtonPress-2>",
            lambda event: [
                draw_polygon(
                    event,
                    videoobject,
                    maincanvas,
                    self.flow_dict,
                    self.selectionlist,
                    self.tracks,
                    undo=True,
                )
            ],
        )

        maincanvas.bind(
            "<B1-Motion>",
            lambda event: [
                maincanvas.click_receive_coordinates(event, 1),
                draw_line(
                    event,
                    videoobject,
                    maincanvas,
                    self.flow_dict,
                    self.selectionlist,
                    self.tracks,
                    self.tracks_live,
                    self.raw_detections,
                ),
            ],
        )

        maincanvas.bind(
            "<ButtonPress-3>",
            lambda event: [
                draw_polygon(
                    event,
                    videoobject,
                    maincanvas,
                    self.flow_dict,
                    self.selectionlist,
                    self.tracks,
                    self.tracks_live,
                    self.raw_detections,
                    closing=True,
                )
            ],
        )
        self.treeview_tracks.bind("<<TreeviewSelect>>", self.listbox_track_selection)

        # self.treeview_tracks.bind(
        #     "Button-Release-3",
        #     lambda event: self.treeview_deselect(self.treeview_tracks),
        # )

        self.treeview_sections.bind(
            "<<TreeviewSelect>>", self.listbox_detector_selection
        )

        self.listbox_movement.bind(
            "<<ListboxSelect>>", lambda event: self.listbox_movement_selection(event)
        )

        self.button_display_tracks.bind(
            "<ButtonRelease-1>", lambda event: self.display_all_tracks()
        )
        self.button_display_boundingbox.bind(
            "<ButtonRelease-1>", lambda event: self.display_boundingbox()
        )

        self.button_new_movement.bind(
            "<ButtonRelease-1>", lambda event: self.create_movement_entry_window()
        )
        self.button_add_to_movement.bind(
            "<ButtonRelease-1>", lambda event: self.add_to_movement()
        )

        self.button_autocount.bind(
            "<ButtonRelease-1>",
            lambda event: [
                create_setting_window(videoobject.fps, self.flow_dict, self.tracks)
            ],
        )

        maincanvas.grid(row=0, rowspan=15, column=7, sticky="n")
        maincanvas.create_image(0, 0, anchor=tk.NW, image=first_frame)

        self.listbox_video.insert(0, videoobject.filename)

        self.slider = tk.Scale(
            self.frame,
            variable=maincanvas.slider_value,
            from_=0,
            to=videoobject.totalframecount - 1,
            orient=HORIZONTAL,
            command=lambda event: self.slider_scroll(int(event)),
        )

        self.slider.bind("<ButtonPress-1>", self.slider_pressed)
        self.slider.bind("<ButtonRelease-1>", self.slider_released)

        self.slider.grid(row=11, column=7, sticky="wen")

    def treeview_deselect(self, treeview):
        for item in treeview.selection():
            treeview.selection_remove(item)

    def slider_pressed(self, event):
        """
        Args:
            event (Sliderbutton is pressed): When slider is pressed, thread that updates
            queue with frames stops and gets terminated.
        """

        button_bool["slider"] = True

    def slider_released(self, event):
        """
        Args:
            event (Sliderbutton is pressed): When slider is pressed, thread that updates
            queue with frames stops and gets terminated.
        """
        self.delete_polygon_points()

        button_bool["slider"] = False

    def slider_scroll(self, slider_number):
        """Slides through video with tkinter slider.

        Args:
            slider_number (int): Represents current videoframe.
        """

        if (
            not button_bool["play_video"]
            and not button_bool["rewind_video"]
            and button_bool["slider"]
        ):
            videoobject.current_frame = slider_number

            np_image = videoobject.set_frame()

            self.manipulate_image_refactor(np_image=np_image)

    def play_video(self):
        """Function to play video."""
        # TODO workaround to not use try except
        try:
            videoobject.stop_thread_backward()
        except Exception:
            print("No backwardthread alive")

        for object in list(self.tracks.keys()):

            # tracks disappear when videoplaying is stopped
            self.tracks_live[object] = []

        while (
            button_bool["play_video"]
            and videoobject.current_frame < videoobject.totalframecount
        ):

            if not videoobject.thread_forward.is_alive():
                videoobject.new_q()
                videoobject.new_thread_forward()
                videoobject.start_thread_forward()
                # time.sleep(0.1)

            time.sleep(videoobject.frame_delay)

            videoobject.current_frame += 1

            np_image = videoobject.get_frame(np_image=True)

            self.manipulate_image_refactor(np_image=np_image)

            self.slider.set(videoobject.current_frame)

    def rewind_video(self):
        """Function  to rewind video."""

        # stop old thread

        videoobject.stop_thread_forward()

        while (
            button_bool["rewind_video"]
            and videoobject.current_frame < videoobject.totalframecount
            and videoobject.current_frame > 0
        ):
            if not videoobject.thread_backward.is_alive():
                videoobject.new_q()
                videoobject.new_thread_backward()
                videoobject.start_thread_backward()
                # time.sleep(0.1)

            time.sleep(videoobject.frame_delay)

            videoobject.current_frame -= 1

            np_image = videoobject.get_frame(np_image=True)

            self.manipulate_image_refactor(np_image=np_image)
            # slows down program
            self.slider.set(videoobject.current_frame)

    def scroll_through_video(self, event):  # sourcery skip: min-max-identity
        """Scroll through video with mousewheel.

        Args:
            event (tkinter.event): Mousewheelscroll.
        """
        i = 1 * event.delta // 120

        videoobject.current_frame += i

        videoobject.current_frame = max(videoobject.current_frame, 0)

        self.delete_polygon_points()

        print(videoobject.current_frame)

        np_image = videoobject.set_frame()

        self.manipulate_image_refactor(np_image=np_image)

    def get_tracks(self):
        """Calls load_tracks-function and inserts tracks into listboxwdidget."""
        self.raw_detections, self.tracks = load_tracks()

        for id, object in enumerate(list(self.tracks.keys())):
            self.treeview_tracks.insert(
                parent="", index=id, values=(object, (self.tracks[object]["Class"]))
            )

        # initialize Tracks to draw live
        # object_live_track[object] = []

    def get_detectors(self):
        """Calls load_flowfile-function and inserts sections to listboxwidget."""
        self.flow_dict = load_flowfile()

        self.manipulate_image_refactor()

        for movement in self.flow_dict["Movements"]:
            self.listbox_movement.insert(END, movement)

        for id, detector in enumerate(self.flow_dict["Detectors"]):
            self.treeview_sections.insert(parent="", index=id, values=detector)

    def listbox_track_selection(self, event):
        """Draws one or more selected tracks on canvas."""
        self.selectionlist = []

        for item in self.treeview_tracks.selection():
            item_text = self.treeview_tracks.item(item, "values")
            self.selectionlist.append(item_text[0])

        self.manipulate_image_refactor()

    def listbox_detector_selection(self, event):
        """Re draws detectors, where the selected detectors has different color

        Args:
            event (tkinter.event): Section selection from  listbox.
        """

        item = self.treeview_sections.selection()
        detector_name = self.treeview_sections.item(item, "values")[0]

        for dict_key in self.flow_dict["Detectors"].keys():

            if detector_name == dict_key:

                self.flow_dict["Detectors"][detector_name]["color"] = (200, 0, 0)

            else:
                self.flow_dict["Detectors"][dict_key]["color"] = (200, 125, 125)

        self.manipulate_image_refactor()

    def display_all_tracks(self):
        """Changes boolvalue and displays all tracks on canvas."""

        button_display_tracks_switch(self.button_display_tracks)

        self.manipulate_image_refactor()

    def display_boundingbox(self):
        """Changes boolvalue and displays boundingboxes on canvas."""
        button_display_bb_switch(self.button_display_boundingbox)

        self.manipulate_image_refactor()

    def display_tracks_live(self):
        """Changes boolvalue and displays tracks while playing video."""
        button_display_live_track_switch(self.button_display_livetracks)

    def create_section_entry_window(self):
        """Creates toplevel window to name sections."""

        # only if line or polygon creation is activate
        if button_bool["linedetector_toggle"] or button_bool["polygondetector_toggle"]:

            self.new_detector_creation = tk.Toplevel()

            # removes hotkey so "enter" won't trigger
            keyboard.remove_hotkey("enter")

            detector_name_entry = tk.Entry(master=self.new_detector_creation)

            detector_name_entry.grid(row=1, column=0, sticky="w", pady=10, padx=10)
            detector_name_entry.focus()

            safe_section = tk.Button(
                master=self.new_detector_creation,
                text="Add section",
                command=lambda: [
                    self.add_section(maincanvas, self.flow_dict, detector_name_entry),
                    self.on_close(),
                ],
            )

            safe_section.grid(row=1, column=1, sticky="w", pady=10, padx=10)
            self.new_detector_creation.protocol("WM_DELETE_WINDOW", self.on_close)
            # makes the background window unavailable
            self.new_detector_creation.grab_set()

    def create_movement_entry_window(self):
        """Creates toplevel window to name movements."""

        new_movement_creation = tk.Toplevel()

        new_movement_creation.title("Create new movement")
        movement_name_entry = tk.Entry(new_movement_creation, textvariable="Movement")
        movement_name_entry.grid(row=1, column=0, sticky="w", pady=10, padx=10)
        movement_name_entry.delete(0, END)
        movement_name_entry.focus()
        add_movement = tk.Button(
            new_movement_creation,
            text="Add movement",
            command=lambda: self.new_movement(self.flow_dict, movement_name_entry),
        )
        add_movement.grid(row=1, column=1, sticky="w", pady=10, padx=10)
        new_movement_creation.protocol("WM_DELETE_WINDOW")
        new_movement_creation.grab_set()

    def on_close(self):
        # hotkeys
        keyboard.add_hotkey(
            "enter",
            lambda: self.create_section_entry_window(),
        )
        self.new_detector_creation.destroy()

        self.delete_polygon_points()

        self.manipulate_image_refactor()

    def add_section(self, maincanvas, flow_dict, entrywidget):
        """Saves created section to flowfile.

        Args:
            maincanvas (tkinter.canvas): needed to hand over canvas coordinates.
            flow_dict (dictionary): Dictionary with sections and movements.
            entrywidget (tkinter.widget): Entrywidget to put in sectionname.
        """

        detector_name = entrywidget.get()

        dump_to_flowdictionary(maincanvas, flow_dict, detector_name)

        self.treeview_sections.insert(parent="", index="end", values=detector_name)

    def new_movement(self, flow_dict, entrywidget):
        """Saves created movement to flowfile.

        Args:
            flow_dict (dictionary): Dictionary with sections and movements.
            entrywidget (tkinter.widget): Entrywidget to put in movementname.
        """
        movement_name = entrywidget.get()

        flow_dict["Movements"][movement_name] = []

        self.listbox_movement.insert(0, movement_name)

        self.manipulate_image_refactor()

    def delete_section(self):
        """Deletes selected section  from flowfile and listboxwidget."""

        item = self.treeview_sections.selection()
        detector_name = self.treeview_sections.item(item, "values")[0]

        self.treeview_sections.delete(item)

        del self.flow_dict["Detectors"][detector_name]

        for key in self.flow_dict["Movements"]:
            for value in self.flow_dict["Movements"][key]:
                print(self.flow_dict["Movements"][key])
                if detector_name in self.flow_dict["Movements"][key]:
                    self.flow_dict["Movements"][key].remove(detector_name)

        self.manipulate_image_refactor()

    def delete_polygon_points(self):
        """delete list of polygon points after scrolling, sliding, playing, rewinding"""
        if maincanvas.polygon_points:
            maincanvas.polygon_points = []

    def add_to_movement(self):
        """Adds selected section to selected movement."""
        item = self.treeview_sections.selection()
        detector_name = self.treeview_sections.item(item, "values")[0]

        movement_name = self.listbox_movement.get(self.listbox_movement.curselection())

        self.flow_dict["Movements"][movement_name].append(detector_name)

        detector_name = (
            detector_name
            + " #"
            + str(self.flow_dict["Movements"][movement_name].index(detector_name) + 1)
        )

        self.listbox_movement_detector.insert(END, detector_name)

    def listbox_movement_selection(self, event):
        """Displays corresponding sections when movement is selected.

        Args:
            event (tkinter.event): Movement selection from listboxwidget.
        """
        # shows detectors and sections belonging to selected movement

        self.listbox_movement_detector.delete(0, "end")

        movement_name = self.listbox_movement.get(self.listbox_movement.curselection())

        for detector_name in self.flow_dict["Movements"][movement_name]:
            detector_name = (
                detector_name
                + " #"
                + str(
                    self.flow_dict["Movements"][movement_name].index(detector_name) + 1
                )
            )

            self.listbox_movement_detector.insert(END, detector_name)

        self.statepanelobject.update_statepanel(
            statepanel_txt["Add_movement_information"]
        )

    def manipulate_image_refactor(self, np_image=None):
        manipulate_image(
            np_image,
            videoobject,
            maincanvas,
            self.flow_dict,
            self.selectionlist,
            self.tracks,
            self.tracks_live,
            self.raw_detections,
        )


def main():
    """Main function."""
    root = tk.Tk()
    root.iconbitmap(r"OTAnalytics\gui\OTC.ico")
    MainWindow(master=root)
    root.mainloop()


if __name__ == "__main__":
    main()
