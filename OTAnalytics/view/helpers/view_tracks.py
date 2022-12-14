import tkinter as tk
import tkinter.ttk as ttk
from Data_Visualization.vizualisation import create_graphic_setting_window
from view.tracks import load_and_convert, deload_trackfile
import helpers.file_helper as file_helper
import view.image_alteration
from view.helpers.gui_helper import (
    button_display_tracks_switch,
    button_display_live_track_switch,
    button_display_bb_switch,
)

import autocount.auto_counting
import helpers.config


class FrameObject(tk.LabelFrame):
    def __init__(self, **kwargs):
        super().__init__(text="Road Users", **kwargs)
        self.frame_tree = tk.Frame(master=self)
        self.frame_tree.pack(fill="x")

        # Files treeview
        self.tree_objects = ttk.Treeview(master=self.frame_tree, height=11)
        self.vsb = ttk.Scrollbar(
            master=self.frame_tree, orient="vertical", command=self.tree_objects.yview
        )
        self.vsb.pack(side="right", fill="y")
        self.tree_objects.configure(yscrollcommand=self.vsb.set)
        self.tree_objects.pack(
            fill="x",
            padx=10,
            pady=10,
        )

        tree_files_cols = {"#0": "ID", "Class": "Class"}
        self.tree_objects["columns"] = tuple(
            {k: v for k, v in tree_files_cols.items() if k != "#0"}.keys()
        )
        self.tree_objects.column("#0", anchor="center", width=50)
        self.tree_objects.heading("#0", text=tree_files_cols["#0"], anchor="center")

        self.tree_objects.column("Class", anchor="center")
        self.tree_objects.heading(
            "Class", text=tree_files_cols["Class"], anchor="center"
        )

        self.frame_control_objects = tk.Frame(master=self)
        self.frame_control_objects.pack(fill="x")

        self.tree_objects.bind("<<TreeviewSelect>>", self.treeobject_selection)

        # Load tracks
        self.button_load_tracks = tk.Button(
            master=self.frame_control_objects,
            text="Load Tracks",
            command=self.add_tracks,
        )
        self.button_load_tracks.grid(row=0, column=0, padx=(10, 0), sticky="ew")

        # Show tracks
        self.button_show_tracks = tk.Button(
            master=self.frame_control_objects,
            width=12,
            text="Show all Tracks",
            command=lambda: [
                button_display_tracks_switch(self.button_show_tracks),
                view.image_alteration.manipulate_image(),
            ],
        )
        self.button_show_tracks.grid(row=0, column=1, sticky="ew")

        # Show Livetrack
        self.button_show_livetracks = tk.Button(
            master=self.frame_control_objects,
            width=12,
            text="Show Tracks",
            command=lambda: [
                button_display_live_track_switch(self.button_show_livetracks),
                view.image_alteration.manipulate_image(),
            ],
        )
        self.button_show_livetracks.grid(row=0, column=2, sticky="ew")

        # Show bounding boxes
        self.button_show_bounding_boxes = tk.Button(
            master=self.frame_control_objects,
            width=12,
            text="Show Bboxes",
            command=lambda: [
                button_display_bb_switch(self.button_show_bounding_boxes),
                view.image_alteration.manipulate_image(),
            ],
        )
        self.button_show_bounding_boxes.grid(row=0, column=3, padx=(0, 25), sticky="ew")

        # Show clear all tracks
        self.button_clear_tracks = tk.Button(
            master=self.frame_control_objects,
            width=12,
            text="Clear Tracks",
            command=lambda: [
                self.clear_treeview(),
                deload_trackfile(),
                file_helper.list_of_analyses[file_helper.list_of_analyses_index].initialize_empty_image(),
                self.button_show_tracks.configure(text="Show all Tracks"),
                view.image_alteration.manipulate_image()
                ]
            )
        self.button_clear_tracks.grid(row=0, column=4, padx=(0, 25), sticky="ew")

        # autocount
        self.button_autocount = tk.Button(
            master=self.frame_control_objects,
            text="Autocount",
            command=autocount.auto_counting.create_setting_window,
        )
        self.button_autocount.grid(
            row=1, column=0, columnspan=2, padx=(10, 0), pady=(0, 12), sticky="ew"
        )

        # graphic
        self.button_graphic = tk.Button(
            master=self.frame_control_objects,
            text="Display Graphics",
            command=create_graphic_setting_window,
        )
        self.button_graphic.grid(
            row=1, column=2, columnspan=2, padx=(0, 25), pady=(0, 12), sticky="ew"
        )

    def add_tracks(self):
        """Calls load_tracks-function and inserts tracks into listboxwdidget."""
        (
            file_helper.list_of_analyses[file_helper.list_of_analyses_index].raw_detections,
            file_helper.list_of_analyses[file_helper.list_of_analyses_index].tracks_dic, 
            file_helper.list_of_analyses[file_helper.list_of_analyses_index].tracks_df,
            file_helper.list_of_analyses[file_helper.list_of_analyses_index].tracks_geoseries,
        ) = load_and_convert(
            x_resize_factor=file_helper.list_of_analyses[file_helper.list_of_analyses_index].videoobject.x_resize_factor,
            y_resize_factor=file_helper.list_of_analyses[file_helper.list_of_analyses_index].videoobject.y_resize_factor,
        )
        if file_helper.list_of_analyses[file_helper.list_of_analyses_index].tracks_df.empty:
            print("Importing trackfile not possible, most likely du to missing trajectories")
            return
        for object in file_helper.list_of_analyses[file_helper.list_of_analyses_index].tracks_df.index:
            self.tree_objects.insert(
                parent="",
                index="end",
                text=object,
                values=file_helper.list_of_analyses[file_helper.list_of_analyses_index].tracks_dic[object]["Class"],
            )

        button_display_tracks_switch(self.button_show_tracks)
        view.image_alteration.manipulate_image()

    def treeobject_selection(self, event):
        """Draws one or more selected tracks on canvas."""
        file_helper.selectionlist_objects = []

        for item in self.tree_objects.selection():
            item_text = self.tree_objects.item(item, "text")
            file_helper.selectionlist_objects.append(item_text)

        view.image_alteration.manipulate_image()

    def clear_treeview(self):
        for i in self.tree_objects.get_children():
            self.tree_objects.delete(i)

        

