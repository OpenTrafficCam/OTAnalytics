import tkinter as tk
import tkinter.ttk as ttk


class FrameObject(tk.Frame):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.frame_tree = tk.Frame(master=self)
        self.frame_tree.grid()

        # Files treeview
        self.tree_objects = ttk.Treeview(master=self.frame_tree, height=3)
        self.tree_objects.pack(fill="x")

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
        self.frame_control_objects.grid()

        # Show tracks
        self.button_show_tracks = tk.Button(
            master=self.frame_control_objects,
            text="Show tracks",
        )
        self.button_show_tracks.grid(row=0, column=0, sticky="ew")

        # Show Livetrack
        self.button_show_livetracks = tk.Button(
            master=self.frame_control_objects,
            text="Show livetrack",
        )
        self.button_show_livetracks.grid(row=0, column=1, sticky="ew")

        # Show bounding boxes
        self.button_show_bounding_boxes = tk.Button(
            master=self.frame_control_objects,
            text="Show bounding boxes",
        )
        self.button_show_bounding_boxes.grid(row=0, column=2, sticky="ew")

        # autocount
        self.button_autocount = tk.Button(
            master=self.frame_control_objects,
            text="autocount",
        )
        self.button_autocount.grid(row=1, column=0, columnspan=3, sticky="ew")
