import tkinter as tk

from cv2 import FileNode_FLOW
from canvas_class import OtcCanvas
from video import load_video_and_frame
import time
from tracks2 import load_tracks
from tkinter.constants import END, HORIZONTAL
from image_alteration import manipulate_image
import keyboard
from sections import draw_polygon, draw_line, load_flowfile
from PIL import Image, ImageTk
from gui_helper import button_bool, button_play_video_toggle, button_rewind_video_toggle


class MainWindow(tk.Frame):
    """Mainwindow with initial dictionaries.

    Args:
        tk.frame (tkinterframe): important for the process of grouping and organizing
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
        self.tracks = []

        videolabel = tk.Label(
            master=self.frame, text="Videos and Tracks", fg="white", bg="#37483E"
        )
        videolabel.grid(row=0, column=0, columnspan=7, sticky="ew")
        self.listbox_video = tk.Listbox(self.frame, height=3)
        self.listbox_video.grid(row=1, column=0, columnspan=7, sticky="ew")
        self.listbox_video.bind("<<ListboxSelect>>")

        button_addvideo = tk.Button(
            self.frame, text="Add", command=lambda: self.create_canvas_and_videoobject()
        )

        button_addvideo.grid(row=2, column=0, sticky="ew")

        button_playvideo = tk.Button(
            self.frame,
            text="Play",
            command=lambda: [
                button_play_video_toggle(button_playvideo, button_rewindvideo),
                self.play_video(),
            ],
        )
        button_playvideo.grid(row=2, column=1, columnspan=1, sticky="ew")

        button_rewindvideo = tk.Button(
            self.frame,
            text="Rewind",
            command=lambda: [
                button_rewind_video_toggle(button_rewindvideo, button_playvideo),
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

        self.listbox_detector = tk.Listbox(self.frame, height=8)
        self.listbox_detector.grid(row=4, column=0, columnspan=3, sticky="ew")

        self.listbox_tracks = tk.Listbox(
            self.frame, selectmode="multiple", exportselection=False, height=8
        )
        self.listbox_tracks.grid(row=4, column=3, columnspan=4, sticky="ew")

        self.button_line = tk.Button(
            self.frame,
            text="Line",
        )
        self.button_line.grid(row=5, column=0, sticky="ew")

        self.button_poly = tk.Button(
            self.frame,
            text="Polygon",
        )
        self.button_poly.grid(row=5, column=1, sticky="ew")

        self.button_delete_detector = tk.Button(
            self.frame,
            text="Remove",
        )
        self.button_delete_detector.grid(row=5, column=2, sticky="ew")

        self.button_display_tracks = tk.Button(
            self.frame,
            text="Show tracks",
        )

        self.button_display_tracks.grid(row=5, column=3, sticky="ew")

        self.button_display_boundingbox = tk.Button(self.frame, text="Show bb")

        self.button_display_boundingbox.grid(row=5, column=5, sticky="ew")

        self.button_display_livetracks = tk.Button(
            self.frame,
            text="Livetrack",
        )

        self.button_display_livetracks.grid(row=5, column=4, sticky="ew")

    def create_canvas_and_videoobject(self):
        # load video object

        global videoobject
        global maincanvas

        videoobject = load_video_and_frame()

        first_frame = videoobject.get_frame(np_image=False)

        # hotkeys
        keyboard.add_hotkey(
            "enter",
            lambda: self.create_entry_window(
                maincanvas, videoobject, self.flow_dict, master=self.master
            ),
        )

        # create canvas from videoobect
        maincanvas = OtcCanvas(
            self.frame,
            width=videoobject.width,
            height=videoobject.height,
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
                maincanvas.click_recieve_coorinates(event, 0),
                draw_polygon(
                    event,
                    videoobject,
                    maincanvas,
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
                    undo=True,
                )
            ],
        )

        maincanvas.bind(
            "<B1-Motion>",
            lambda event: [
                maincanvas.click_recieve_coorinates(event, 1),
                draw_line(
                    event,
                    videoobject,
                    maincanvas,
                    self.flow_dict,
                    self.selectionlist,
                    self.tracks,
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
                    closing=True,
                )
            ],
        )
        self.listbox_tracks.bind(
            "<<ListboxSelect>>",
            lambda event: self.create_track_selection(
                event,
            ),
        )

        maincanvas.grid(row=0, rowspan=6, column=7, sticky="n")
        maincanvas.create_image(0, 0, anchor=tk.NW, image=first_frame)

        self.listbox_video.insert(0, videoobject.filename)

        # self.slider = tk.Scale(
        #     self.frame,
        #     variable=maincanvas.slider_value,
        #     from_=0,
        #     to=videoobject.totalframecount - 1,
        #     orient=HORIZONTAL,
        #     command=lambda event: maincanvas.slider_scroll(
        #         event, int(event), videoobject
        #     ),  # event is the slided number/ gets triggered through mousescroll/

        # )

        # self.slider.grid(row=11, column=7, sticky="wen")

    def play_video(self):
        # play and rewind

        while (
            button_bool["play_video"]
            and videoobject.current_frame < videoobject.totalframecount
        ):

            time.sleep(videoobject.frame_delay)

            videoobject.current_frame += 1

            np_image = videoobject.get_frame(np_image=True)

            manipulate_image(
                np_image,
                videoobject,
                maincanvas,
                self.flow_dict,
                self.selectionlist,
                self.tracks,
            )

            # slows down programm
            # self.slider.set(videoobject.current_frame)

    def rewind_video(self):
        # play and rewind

        while (
            button_bool["rewind_video"]
            and videoobject.current_frame < videoobject.totalframecount
        ):

            time.sleep(videoobject.frame_delay)

            videoobject.current_frame += -1

            np_image = videoobject.get_frame(np_image=True)

            manipulate_image(
                np_image,
                videoobject,
                maincanvas,
                self.flow_dict,
                self.selectionlist,
                self.tracks,
            )

            # slows down programm
            # self.slider.set(videoobject.current_frame)

    def scroll_through_video(self, event):

        i = 1 * event.delta // 120

        videoobject.current_frame += i

        np_image = videoobject.get_frame(np_image=True)

        manipulate_image(
            np_image,
            videoobject,
            maincanvas,
            self.flow_dict,
            self.selectionlist,
            self.tracks,
        )

    def get_tracks(self):

        self.rawdetection, self.tracks = load_tracks()

        for object in list(self.tracks.keys()):

            self.listbox_tracks.insert("end", object)
            # initialize Tracks to draw live
            # object_live_track[object] = []

    def get_detectors(self):

        self.flow_dict = load_flowfile()

        print(self.flow_dict)

        manipulate_image(
            videoobject.np_image.copy(),
            videoobject,
            maincanvas,
            self.flow_dict,
            self.selectionlist,
            self.tracks,
        )

    def create_track_selection(self, event):
        """Draws one or more selected tracks on canvas."""
        # self.draw_detectors_from_dict()
        self.widget = event.widget
        multiselection = self.widget.curselection()

        self.selectionlist = []

        for selection in multiselection:
            entry = self.widget.get(selection)
            self.selectionlist.append(entry)

        manipulate_image(
            videoobject.np_image.copy(),
            videoobject,
            maincanvas,
            self.flow_dict,
            self.selectionlist,
            self.tracks,
        )

    def create_entry_window(self, canvas, video, flow_dict, **kwargs):
        SectionEntryWindow(flow_dict, canvas, video, **kwargs)


class SectionEntryWindow(tk.Toplevel):
    def __init__(self, flow_dictionary, canvas, video, **kwargs):
        super().__init__(**kwargs)

        # keyboard.remove_hotkey("enter")

        self.detector_name_entry = tk.Entry(self)

        self.detector_name_entry.grid(row=1, column=0, sticky="w", pady=10, padx=10)
        self.detector_name_entry.focus()

        self.safe_section = tk.Button(
            self,
            text="Add section",
            command=lambda: [
                self.add_section(canvas, flow_dictionary, self.detector_name_entry),
                manipulate_image(video.np_image.copy(), video, canvas, flow_dictionary),
            ],
        )

        self.safe_section.grid(row=1, column=1, sticky="w", pady=10, padx=10)
        # makes the background window unavailable
        # self.protocol("WM_DELETE_WINDOW", MainWindow.on_close)
        self.grab_set()

    def add_section(self, maincanvas, flow_dict, entrywidget):

        if button_bool["linedetector_toggle"] is True:
            detector_name = entrywidget.get()

            print(maincanvas.points)

            flow_dict["Detectors"][detector_name] = {
                "type": "line",
                "start_x": maincanvas.points[0][0],
                "start_y": maincanvas.points[0][1],
                "end_x": maincanvas.points[1][0],
                "end_y": maincanvas.points[1][1],
                "color": (200, 125, 125),
            }

        if button_bool["polygondetector_toggle"] is True:
            flow_dict["Detectors"][detector_name] = {
                "type": "polygon",
                "points": maincanvas.poly_points,
                "color": (200, 125, 125),
            }

        print(flow_dict)


def main():
    """Main function."""
    root = tk.Tk()
    root.iconbitmap(r"OTAnalytics\gui\OTC.ico")
    MainWindow(master=root)
    root.mainloop()


if __name__ == "__main__":
    main()
