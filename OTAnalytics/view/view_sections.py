import tkinter as tk
import tkinter.ttk as ttk
from view.helpers.gui_helper import (
    button_line_switch,
    button_polygon_switch,
)
import helpers.file_helper as file_helper
import view.image_alteration


class FrameSection(tk.Frame):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.frame_tree = tk.Frame(master=self)
        self.frame_tree.pack(fill="x")

        # Files treeview
        self.tree_sections = ttk.Treeview(master=self.frame_tree, height=3)
        self.tree_sections.pack(fill="x")

        self.tree_sections.bind("<<TreeviewSelect>>", self.tree_detector_selection)

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
            width=12,
            text="Line",
            command=lambda: button_line_switch(self.button_line, self.button_polygon),
        )
        self.button_line.grid(row=0, column=0)

        # Add Polygon-Section
        self.button_polygon = tk.Button(
            master=self.frame_control_section,
            width=12,
            text="Polygon",
            command=lambda: button_polygon_switch(
                self.button_polygon, self.button_line
            ),
        )
        self.button_polygon.grid(row=0, column=1)

        # Add Polygon-Section
        self.button_remove_section = tk.Button(
            master=self.frame_control_section,
            width=12,
            text="Remove",
        )
        self.button_remove_section.grid(row=0, column=2)

        # Add to movement
        self.button_add_section_to_movement = tk.Button(
            master=self.frame_control_section,
            text="Add to movement",
        )
        self.button_add_section_to_movement.grid(
            row=1, column=0, columnspan=3, sticky="ew"
        )

    def tree_detector_selection(self, event):
        """Re draws detectors, where the selected detectors has different color

        Args:
            event (tkinter.event): Section selection from  listbox.
        """

        file_helper.selectionlist_sections = []

        for item in self.tree_sections.selection():
            detector_name = self.tree_sections.item(item, "text")
            file_helper.selectionlist_sections.append(detector_name)

        for dict_key in file_helper.flow_dict["Detectors"].keys():

            if dict_key in file_helper.selectionlist_sections:

                file_helper.flow_dict["Detectors"][dict_key]["color"] = (
                    200,
                    0,
                    0,
                )

            else:
                file_helper.flow_dict["Detectors"][dict_key]["color"] = (
                    200,
                    125,
                    125,
                )

        view.image_alteration.manipulate_image()
