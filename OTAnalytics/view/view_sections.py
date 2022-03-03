import tkinter as tk
import tkinter.ttk as ttk
from gui_helper import button_line_switch, button_polygon_switch
import file_helper
import image_alteration


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
            text="Line",
            command=lambda: button_line_switch(self.button_line, self.button_polygon),
        )
        self.button_line.grid(row=0, column=0)

        # Add Polygon-Section
        self.button_polygon = tk.Button(
            master=self.frame_control_section,
            text="Polygon",
            command=lambda: button_polygon_switch(
                self.button_polygon, self.button_line
            ),
        )
        self.button_polygon.grid(row=0, column=1)

        # Add Polygon-Section
        self.button_remove = tk.Button(
            master=self.frame_control_section,
            text="Remove",
            command=self.delete_section,
        )
        self.button_remove.grid(row=0, column=2)

        # Add to movement
        self.button_add_movement = tk.Button(
            master=self.frame_control_section,
            text="Add to movement",
        )
        self.button_add_movement.grid(row=1, column=0, columnspan=3, sticky="ew")

    def tree_detector_selection(self, event):
        """Re draws detectors, where the selected detectors has different color

        Args:
            event (tkinter.event): Section selection from  listbox.
        """

        item = self.tree_sections.selection()
        detector_name = self.tree_sections.item(item, "text")

        for dict_key in file_helper.flow_dict["Detectors"].keys():

            if detector_name == dict_key:

                file_helper.flow_dict["Detectors"][detector_name]["color"] = (200, 0, 0)

            else:
                file_helper.flow_dict["Detectors"][dict_key]["color"] = (200, 125, 125)

        image_alteration.manipulate_image()

    def delete_section(self):
        """Deletes selected section  from flowfile and listboxwidget."""

        item = self.tree_sections.selection()
        detector_name = self.tree_sections.item(item, "text")

        self.tree_sections.delete(item)

        del file_helper.flow_dict["Detectors"][detector_name]

        for key in file_helper.flow_dict["Movements"]:
            for value in file_helper.flow_dict["Movements"][key]:
                print(file_helper.flow_dict["Movements"][key])
                if detector_name in file_helper.flow_dict["Movements"][key]:
                    file_helper.flow_dict["Movements"][key].remove(detector_name)

        image_alteration.manipulate_image()
