import time
import tkinter as tk
from tkinter import filedialog
import tkinter.ttk as ttk

from view.helpers.gui_helper import (
    button_play_video_switch,
    button_rewind_switch,
    button_bool,
    info_message,
)
from view.video import Video
import helpers.file_helper as file_helper
import helpers.config
import view.image_alteration
import helpers.file_helper as file_helper
from analyse.analyse_class import Analyse



class FrameFiles(tk.LabelFrame):
    def __init__(self, **kwargs):
        super().__init__(text="Files", **kwargs)

        # File dict
        self.files_dict = {}

        self.tracks_live = {}

        # Frame for treeview
        self.frame_tree = tk.Frame(master=self)
        self.frame_tree.pack(
            fill="x",
            padx=10,
            pady=10,
        )

        # Files treeview
        self.tree_files = ttk.Treeview(master=self.frame_tree, height=3)
        self.tree_files.pack(fill="x", ipady=10)

        tree_files_cols = {
            "#0": "Video",
            "ottrk": "ottrk",
            "otflow": "otflow",
        }

        self.tree_files["columns"] = tuple(
            {k: v for k, v in tree_files_cols.items() if k != "#0"}.keys()
        )

        for tree_files_col_id, tree_files_col_text in tree_files_cols.items():
            if tree_files_col_id == "#0":
                anchor = "w"
                width = 300
            else:
                anchor = "center"
                width = 50
            self.tree_files.column(tree_files_col_id, width=width, anchor=anchor)
            self.tree_files.heading(
                tree_files_col_id, text=tree_files_col_text, anchor=anchor
            )

        # Button for add, play, rewind, clear
        self.frame_control = tk.Frame(master=self)
        self.frame_control.pack()

        # Add Video
        self.button_add_video = tk.Button(
            master=self.frame_control,
            width=12,
            text="Add Video",
        )
        self.button_add_video.grid(row=0, column=0, pady=(0, 10), sticky="ew")

        # Play Video
        self.button_play_video = tk.Button(
            master=self.frame_control,
            width=12,
            text="Play",
            command=lambda: [
                button_play_video_switch(
                    self.button_play_video, self.button_rewind_video
                ),
                helpers.config.maincanvas.delete_points(),
                self.play_video(),
            ],
        )
        self.button_play_video.grid(row=0, column=1, pady=(0, 10), sticky="ew")

        # Rewind Video
        self.button_rewind_video = tk.Button(
            master=self.frame_control,
            width=12,
            text="Rewind",
            command=lambda: [
                button_rewind_switch(self.button_rewind_video, self.button_play_video),
                helpers.config.maincanvas.delete_points(),
                self.rewind_video(),
            ],
        )

        self.button_rewind_video.grid(row=0, column=2, pady=(0, 10), sticky="ew")

        # Clear Video
        self.button_remove_video = tk.Button(
            master=self.frame_control,
            width=12,
            text="Remove Video",
            
        )
        self.button_remove_video.grid(row=0, column=3, pady=(0, 10), sticky="ew")

    def add_file(self):

        # load video object
        video_source = filedialog.askopenfile(
            filetypes=[("Videofiles", "*.mkv"), ("Videofiles", "*.mp4")]
        )
        #file_helper.list_of_analyses[-1] = Video(video_source.name)

        file_helper.list_of_analyses.append(Analyse(video_source.name))


        path = file_helper.get_dir(video_source.name)


        self.add_files_to_dict(path)

        self.files_dict[path]["video_name"] = file_helper.get_filename(
            video_source.name
        )

        self.update_files_dict_values(path)

        self.update_tree_files()

    def add_canvas_frame(self):

        image = file_helper.list_of_analyses[-1].videoobject.get_frame(np_image=False)

        helpers.config.maincanvas.configure(
            width=file_helper.list_of_analyses[-1].videoobject.width,
            height=file_helper.list_of_analyses[-1].videoobject.height,
        )

        helpers.config.sliderobject.create_slider()

        helpers.config.maincanvas.create_image(0, 0, anchor=tk.NW, image=image)

    def add_files_to_dict(self, path):
        self.files_dict[path] = {}

    def update_files_dict_values(self, path):

        otflow_pattern, ottrk_pattern = file_helper.create_pattern(
            self.files_dict[path]["video_name"]
        )

        if ottrk_pattern is not None:
            file_helper.check_fileexistence(path, otflow_pattern, ottrk_pattern)

        TRUE_SYMBOL = "\u2705"  # "\u2713"  # "\u2714"
        FALSE_SYMBOL = "\u274E"  # "\u2717"  # "\u2718"

        self.files_dict[path]["otflow_file"] = (
            TRUE_SYMBOL if bool(file_helper.otflow_file) else FALSE_SYMBOL
        )

        self.files_dict[path]["ottrk_file"] = (
            TRUE_SYMBOL if bool(file_helper.ottrk_file) else FALSE_SYMBOL
        )

    def update_tree_files(self):
        TRUE_SYMBOL = "\u2705"  # "\u2713"  # "\u2714"
        FALSE_SYMBOL = "\u274E"  # "\u2717"  # "\u2718"

        self.tree_files.delete(*self.tree_files.get_children())

        for analyses in file_helper.list_of_analyses:
            self.tree_files.insert(
                parent="",
                index="end",
                text=analyses.videoobject.filename,
                values=(
                    TRUE_SYMBOL if analyses.trackfile_existence else FALSE_SYMBOL,
                    TRUE_SYMBOL if analyses.flowfile_existence else FALSE_SYMBOL,
                ),)


    def play_video(self):
        """Function to play video."""
        # TODO workaround to not use try except
        try:
            file_helper.list_of_analyses[-1].videoobject.stop_thread_backward()
        except Exception:
            print("No backwardthread alive")

        for object in list(file_helper.tracks_dic.keys()):

            # tracks disappear when videoplaying is stopped
            file_helper.tracks_live[object] = []

        while (
            button_bool["play_video"]
            and file_helper.list_of_analyses[-1].videoobject.current_frame
            < file_helper.list_of_analyses[-1].videoobject.totalframecount
        ):

            if not file_helper.list_of_analyses[-1].videoobject.thread_forward.is_alive():
                file_helper.list_of_analyses[-1].videoobject.new_q()
                file_helper.list_of_analyses[-1].videoobject.new_thread_forward()
                file_helper.list_of_analyses[-1].videoobject.start_thread_forward()
                # time.sleep(0.1)


            time.sleep(file_helper.list_of_analyses[-1].videoobject.frame_delay)

            file_helper.list_of_analyses[-1].videoobject.current_frame += 1

            np_image = file_helper.list_of_analyses[-1].videoobject.get_frame(np_image=True).copy()

            view.image_alteration.manipulate_image(np_image=np_image)

            helpers.config.sliderobject.slider.set(
                file_helper.list_of_analyses[-1].videoobject.current_frame
            )

    def rewind_video(self):
        """Function  to rewind video."""

        # stop old thread

        file_helper.list_of_analyses[-1].videoobject.stop_thread_forward()

        while (
            button_bool["rewind_video"]
            and file_helper.list_of_analyses[-1].videoobject.current_frame
            < file_helper.list_of_analyses[-1].videoobject.totalframecount
            and file_helper.list_of_analyses[-1].videoobject.current_frame > 0
        ):
            if not file_helper.list_of_analyses[-1].videoobject.thread_backward.is_alive():
                file_helper.list_of_analyses[-1].videoobject.new_q()
                file_helper.list_of_analyses[-1].videoobject.new_thread_backward()
                file_helper.list_of_analyses[-1].videoobject.start_thread_backward()
                # time.sleep(0.1)

            time.sleep(file_helper.list_of_analyses[-1].videoobject.frame_delay)

            file_helper.list_of_analyses[-1].videoobject.current_frame -= 1

            np_image = file_helper.list_of_analyses[-1].videoobject.get_frame(np_image=True)

            view.image_alteration.manipulate_image(np_image=np_image)
            # slows down program
            helpers.config.sliderobject.slider.set(
                file_helper.list_of_analyses[-1].videoobject.current_frame
            )

    def remove_video(self):
        """removes videofile"""
        self.files_dict = {}
        item = self.tree_files.selection()
        video_name = self.tree_files.item(item, "text")

        if not video_name:
            info_message("Warning", "Please select video you wish to delete!")

            return

        for item in self.tree_files.selection():
            # item_text = self.tree_files.item(item, "values")

            self.tree_files.delete(item)

        self.file_values = []

        helpers.config.maincanvas.configure(width=0, height=0)

        helpers.config.sliderobject.destroy_slider()

        file_helper.list_of_analyses[-1] = None


