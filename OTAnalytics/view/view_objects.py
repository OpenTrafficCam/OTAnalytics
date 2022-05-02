import tkinter as tk
import tkinter.ttk as ttk
from view.tracks import load_and_convert
import helpers.file_helper as file_helper
import view.image_alteration
from view.helpers.gui_helper import (
    button_display_tracks_switch,
    button_display_live_track_switch,
    button_display_bb_switch,
)

import count.auto_counting
import view.config


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

        # autocount
        self.button_autocount = tk.Button(
            master=self.frame_control_objects,
            text="Autocount",
            command=count.auto_counting.create_setting_window,
        )
        self.button_autocount.grid(
            row=1, column=0, columnspan=4, padx=(10, 25), pady=(0, 12), sticky="ew"
        )

    def add_tracks(self):
        """Calls load_tracks-function and inserts tracks into listboxwdidget."""
        (
            file_helper.raw_detections,
            file_helper.tracks,
            file_helper.tracks_df,
            file_helper.tracks_geoseries,
        ) = load_and_convert(
            x_factor=view.config.videoobject.x_resize_factor,
            y_factor=view.config.videoobject.y_resize_factor,
        )

        for object in list(file_helper.tracks.keys()):
            self.tree_objects.insert(
                parent="",
                index="end",
                text=object,
                values=file_helper.tracks[object]["Class"],
            )

        view.image_alteration.manipulate_image()

    def treeobject_selection(self, event):
        """Draws one or more selected tracks on canvas."""
        file_helper.selectionlist_objects = []

        for item in self.tree_objects.selection():
            item_text = self.tree_objects.item(item, "text")
            file_helper.selectionlist_objects.append(item_text)

        view.image_alteration.manipulate_image()
