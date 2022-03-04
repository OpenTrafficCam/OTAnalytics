import time
import tkinter as tk
from tkinter import filedialog
import tkinter.ttk as ttk

from gui_helper import button_play_video_switch, button_rewind_switch, button_bool
from video import Video
from file_helper import *
import config
import file_helper


import image_alteration


class FrameFiles(tk.Frame):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # File dict
        self.files_dict = {}

        self.tracks_live = {}

        # Frame for treeview
        self.frame_tree = tk.Frame(master=self)
        self.frame_tree.pack(fill="x")

        self.videolabel = tk.Label(
            master=self.frame_tree, text="Videos and Tracks", fg="white", bg="#37483E"
        )
        self.videolabel.pack(fill="x")

        # Files treeview
        self.tree_files = ttk.Treeview(master=self.frame_tree, height=3)
        self.tree_files.pack(fill="x")

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
            text="Add video",
            command=self.load_video_and_add_frame,
        )
        self.button_add_video.grid(row=0, column=0, sticky="ew")

        # Play Video
        self.button_play_video = tk.Button(
            master=self.frame_control,
            text="Play video",
            command=lambda: [
                button_play_video_switch(
                    self.button_play_video, self.button_rewind_video
                ),
                config.maincanvas.delete_polygon_points(),
                self.play_video(),
            ],
        )
        self.button_play_video.grid(row=0, column=1, sticky="ew")

        # Rewind Video
        self.button_rewind_video = tk.Button(
            master=self.frame_control,
            text="Rewind video",
            command=lambda: [
                button_rewind_switch(self.button_rewind_video, self.button_play_video),
                config.maincanvas.delete_polygon_points(),
                self.rewind_video(),
            ],
        )

        self.button_rewind_video.grid(row=0, column=2, sticky="ew")

        # Clear Video
        self.button_remove_video = tk.Button(
            master=self.frame_control,
            text="Remove video",
            command=lambda: [self.remove_video()],
        )
        self.button_remove_video.grid(row=0, column=3, sticky="ew")

    def _add_file(self):

        # load video object
        video_source = filedialog.askopenfile(
            filetypes=[("Videofiles", "*.mkv"), ("Videofiles", "*.mp4")]
        )
        config.videoobject = Video(video_source.name)

        path = get_dir(video_source.name)

        self.add_files_to_dict(path)

        self.files_dict[path]["video_name"] = get_filename(video_source.name)

        self.update_files_dict_values(path)

        self.update_tree_files()

    def _add_canvas_frame(self):

        image = config.videoobject.get_frame(np_image=False)

        config.maincanvas.configure(
            width=config.videoobject.width, height=config.videoobject.height
        )

        config.sliderobject.create_slider()

        config.maincanvas.create_image(0, 0, anchor=tk.NW, image=image)

    def load_video_and_add_frame(self):

        self._add_file()
        self._add_canvas_frame()

    def add_files_to_dict(self, path):
        self.files_dict[path] = {}

    def update_files_dict_values(self, path):

        otflow_pattern, ottrk_pattern = create_pattern(
            self.files_dict[path]["video_name"]
        )

        otflow_file, ottrk_file = check_fileexistence(
            path, otflow_pattern, ottrk_pattern
        )
        TRUE_SYMBOL = "\u2705"  # "\u2713"  # "\u2714"
        FALSE_SYMBOL = "\u274E"  # "\u2717"  # "\u2718"

        self.files_dict[path]["otflow_file"] = (
            TRUE_SYMBOL if otflow_file else FALSE_SYMBOL
        )

        self.files_dict[path]["ottrk_file"] = (
            TRUE_SYMBOL if ottrk_file else FALSE_SYMBOL
        )

    def update_tree_files(self):
        for path, file_values in self.files_dict.items():
            self.tree_files.insert(
                parent="",
                index="end",
                text=file_values["video_name"],
                values=(
                    file_values["otflow_file"],
                    file_values["ottrk_file"],
                ),
            )

    def play_video(self):
        """Function to play video."""
        # TODO workaround to not use try except
        try:
            config.videoobject.stop_thread_backward()
        except Exception:
            print("No backwardthread alive")

        for object in list(file_helper.tracks.keys()):

            # tracks disappear when videoplaying is stopped
            file_helper.tracks_live[object] = []

        while (
            button_bool["play_video"]
            and config.videoobject.current_frame < config.videoobject.totalframecount
        ):

            if not config.videoobject.thread_forward.is_alive():
                config.videoobject.new_q()
                config.videoobject.new_thread_forward()
                config.videoobject.start_thread_forward()
                # time.sleep(0.1)

            time.sleep(config.videoobject.frame_delay)

            config.videoobject.current_frame += 1

            np_image = config.videoobject.get_frame(np_image=True).copy()

            image_alteration.manipulate_image(np_image=np_image)

            config.sliderobject.slider.set(config.videoobject.current_frame)

    # TODO: Ask to autload ottrak and otflow if found!

    def rewind_video(self):
        """Function  to rewind video."""

        # stop old thread

        config.videoobject.stop_thread_forward()

        while (
            button_bool["rewind_video"]
            and config.videoobject.current_frame < config.videoobject.totalframecount
            and config.videoobject.current_frame > 0
        ):
            if not config.videoobject.thread_backward.is_alive():
                config.videoobject.new_q()
                config.videoobject.new_thread_backward()
                config.videoobject.start_thread_backward()
                # time.sleep(0.1)

            time.sleep(config.videoobject.frame_delay)

            config.videoobject.current_frame -= 1

            np_image = config.videoobject.get_frame(np_image=True)

            image_alteration.manipulate_image(np_image=np_image)
            # slows down program
            config.sliderobject.slider.set(config.videoobject.current_frame)

    def remove_video(self):
        for item in self.tree_files.selection():
            # item_text = self.tree_files.item(item, "values")

            self.tree_files.delete(item)

        config.maincanvas.configure(width=0, height=0)

        config.sliderobject.destroy_slider()
