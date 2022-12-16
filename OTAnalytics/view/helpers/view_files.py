import time
import tkinter as tk
from tkinter import filedialog
import tkinter.ttk as ttk
import glob
import os

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
        self.tree_files.bind('<ButtonRelease-1>',self.video_selection, add="+")
        self.tree_files.bind('<ButtonRelease-1>',self.multi_video_selection, add="+")

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

        # Add folder
        self.button_add_folder = tk.Button(
            master=self.frame_control,
            width=15,
            text="Add folder"        
            
        )
        self.button_add_folder.grid(row=0, column=4, pady=(0, 10), sticky="ew")
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
        print(file_helper.list_of_analyses_index)
        file_helper.list_of_analyses_index = 0
        file_helper.list_of_analyses.insert(0,Analyse(video_source.name))


        self.update_tree_files()

    def add_folder(self):
        videpath_folder = filedialog.askdirectory()

        file_list = [videpath_folder + "/" + file for file in os.listdir(videpath_folder) if file.endswith('.mp4')]

        for video_path in file_list:
            file_helper.list_of_analyses.insert(0,Analyse(video_path))
            self.update_tree_files()

    def add_canvas_frame(self):

        np_image = file_helper.list_of_analyses[file_helper.list_of_analyses_index].videoobject.get_frame(np_image=True)


        helpers.config.maincanvas.configure(
            width=file_helper.list_of_analyses[file_helper.list_of_analyses_index].videoobject.width,
            height=file_helper.list_of_analyses[file_helper.list_of_analyses_index].videoobject.height,
        )
        #re intialisize Slider if already existed
        if helpers.config.sliderobject.slider is not None:
            helpers.config.sliderobject.destroy_slider()
        #creates slider and sets value to 0
        helpers.config.sliderobject.create_slider()
        view.image_alteration.manipulate_image(np_image=np_image)
        #helpers.config.maincanvas.create_image(0, 0, anchor=tk.NW, image=image)

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
        
        # always keep first row selected
        iid = self.tree_files.get_children()[0]
        self.tree_files.selection_set(iid)

    def video_selection(self, event):

            selected_iid = self.tree_files.selection()[0]
            current_idx = self.tree_files.index(selected_iid)

            if current_idx == file_helper.list_of_analyses_index:
                return
            
            #clear selected track
            file_helper.selectionlist_objects = []

            file_helper.list_of_analyses_index = current_idx

            self.add_canvas_frame()

            print('Current Row:',current_idx)

    def multi_video_selection(self, event):
        """Re draws detectors, where the selected detectors has different color

    Args:
        event (tkinter.event): Section selection from  listbox.
    """
        file_helper.selectionlist_videofiles = []

        for item in self.tree_files.selection():
            videofiles_index =self.tree_files.index(item)
            file_helper.selectionlist_videofiles.append(videofiles_index)
        print(file_helper.selectionlist_videofiles)
            

    def play_video(self):
        """Function to play video."""
        # TODO workaround to not use try except
        try:
            file_helper.list_of_analyses[file_helper.list_of_analyses_index].videoobject.stop_thread_backward()
        except Exception:
            print("No backwardthread alive")

        for object in list(file_helper.list_of_analyses[file_helper.list_of_analyses_index].tracks_dic.keys()):

            # tracks disappear when videoplaying is stopped
            file_helper.tracks_live[object] = []

        while (
            button_bool["play_video"]
            and file_helper.list_of_analyses[file_helper.list_of_analyses_index].videoobject.current_frame
            < file_helper.list_of_analyses[file_helper.list_of_analyses_index].videoobject.totalframecount
        ):

            if not file_helper.list_of_analyses[file_helper.list_of_analyses_index].videoobject.thread_forward.is_alive():
                file_helper.list_of_analyses[file_helper.list_of_analyses_index].videoobject.new_q()
                file_helper.list_of_analyses[file_helper.list_of_analyses_index].videoobject.new_thread_forward()
                file_helper.list_of_analyses[file_helper.list_of_analyses_index].videoobject.start_thread_forward()
                # time.sleep(0.1)


            time.sleep(file_helper.list_of_analyses[file_helper.list_of_analyses_index].videoobject.frame_delay)

            file_helper.list_of_analyses[file_helper.list_of_analyses_index].videoobject.current_frame += 1

            np_image = file_helper.list_of_analyses[file_helper.list_of_analyses_index].videoobject.get_frame(np_image=True).copy()

            view.image_alteration.manipulate_image(np_image=np_image)

            helpers.config.sliderobject.slider.set(
                file_helper.list_of_analyses[file_helper.list_of_analyses_index].videoobject.current_frame
            )

    def rewind_video(self):
        """Function  to rewind video."""

        # stop old thread

        file_helper.list_of_analyses[file_helper.list_of_analyses_index].videoobject.stop_thread_forward()

        while (
            button_bool["rewind_video"]
            and file_helper.list_of_analyses[file_helper.list_of_analyses_index].videoobject.current_frame
            < file_helper.list_of_analyses[file_helper.list_of_analyses_index].videoobject.totalframecount
            and file_helper.list_of_analyses[file_helper.list_of_analyses_index].videoobject.current_frame > 0
        ):
            if not file_helper.list_of_analyses[file_helper.list_of_analyses_index].videoobject.thread_backward.is_alive():
                file_helper.list_of_analyses[file_helper.list_of_analyses_index].videoobject.new_q()
                file_helper.list_of_analyses[file_helper.list_of_analyses_index].videoobject.new_thread_backward()
                file_helper.list_of_analyses[file_helper.list_of_analyses_index].videoobject.start_thread_backward()
                # time.sleep(0.1)

            time.sleep(file_helper.list_of_analyses[file_helper.list_of_analyses_index].videoobject.frame_delay)

            file_helper.list_of_analyses[file_helper.list_of_analyses_index].videoobject.current_frame -= 1

            np_image = file_helper.list_of_analyses[file_helper.list_of_analyses_index].videoobject.get_frame(np_image=True)

            view.image_alteration.manipulate_image(np_image=np_image)
            # slows down program
            helpers.config.sliderobject.slider.set(
                file_helper.list_of_analyses[file_helper.list_of_analyses_index].videoobject.current_frame
            )

    def remove_video(self):
        """removes videofile"""

        if not file_helper.selectionlist_videofiles:
            info_message("Warning", "Please select video you wish to delete!")

            return

        for index in file_helper.selectionlist_videofiles:
            iid = self.tree_files.get_children()[index]
            self.tree_files.delete(iid)
            del file_helper.list_of_analyses[index]

        helpers.config.maincanvas.configure(width=0, height=0)

        helpers.config.sliderobject.destroy_slider()

        if file_helper.list_of_analyses:

            file_helper.list_of_analyses_index = 0
            self.add_canvas_frame()






