import tkinter as tk
import tkinter.ttk as ttk


class FrameSection(tk.Frame):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.frame_tree = tk.Frame(master=self)
        self.frame_tree.pack(fill="x")

        # Files treeview
        self.tree_sections = ttk.Treeview(master=self.frame_tree, height=3)
        self.tree_sections.pack(fill="x")

        tree_files_cols = {
            "#0": "Section",
        }
        self.tree_sections["columns"] = tuple(
            {k: v for k, v in tree_files_cols.items() if k != "#0"}.keys()
        )
        self.tree_sections.column("#0", anchor="center")
        self.tree_sections.heading("#0", text=tree_files_cols["#0"], anchor="center")

        self.frame_control_section = tk.Frame(master=self)
        self.frame_control_section.pack()

        # Add Line-Section
        self.button_line = tk.Button(
            master=self.frame_control_section,
            text="Line",
        )
        self.button_line.grid(row=0, column=0)

        # Add Polygon-Section
        self.button_polygon = tk.Button(
            master=self.frame_control_section,
            text="Polygon",
        )
        self.button_polygon.grid(row=0, column=1)

        # Add Polygon-Section
        self.button_remove = tk.Button(
            master=self.frame_control_section,
            text="Remove",
        )
        self.button_remove.grid(row=0, column=2)

        # Add to movement
        self.button_add_movement = tk.Button(
            master=self.frame_control_section,
            text="Add to movement",
        )
        self.button_add_movement.grid(row=1, column=0, columnspan=3, sticky="ew")
