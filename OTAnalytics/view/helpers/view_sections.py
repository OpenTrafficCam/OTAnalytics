import tkinter as tk
import tkinter.ttk as ttk
from view.helpers.gui_helper import (
    button_bool,
    button_line_switch,
    button_polygon_switch,
    info_message,
)
import helpers.file_helper as file_helper
import view.image_alteration
import keyboard
import helpers.config
import view.sections


class FrameSection(tk.LabelFrame):
    def __init__(self, **kwargs):
        super().__init__(text="Section", **kwargs)
        self.frame_tree = tk.Frame(master=self)
        self.frame_tree.pack(fill="x")

        # Files treeview
        self.tree_sections = ttk.Treeview(master=self.frame_tree, height=8)
        self.tree_sections.pack(
            fill=tk.BOTH, expand=True,
            padx=10,
            pady=10,
        )

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
            text="New",
            command=lambda: button_line_switch(self.button_line) #self.button_polygon),
        )
        self.button_line.grid(row=0, column=0, padx=10,pady=10 )

        # Add Polygon-Section
        
        # self.button_polygon = tk.Button(
        #     master=self.frame_control_section,
        #     width=12,
        #     text="Add Polygon",
        #     command=lambda: button_polygon_switch(
        #         self.button_polygon, self.button_line
        #     ),
        # )
        # self.button_polygon.grid(row=0, column=1)

        # Add Polygon-Section
        self.button_remove_section = tk.Button(
            master=self.frame_control_section,
            width=12,
            text="Remove",
        )
        self.button_remove_section.grid(row=0, column=2, padx=10,pady=10, sticky="ew")

        # Add to movement
        # self.button_add_section_to_movement = tk.Button(
        #     master=self.frame_control_section,
        #     text="Add to Movement",
        # )
        # self.button_add_section_to_movement.grid(
        #     row=1, column=0, columnspan=3, padx=(10, 10), pady=(0, 10), sticky="ew"
        # )

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

                file_helper.flow_dict["Detectors"][dict_key]["color"] = (200, 0, 0, 255)

            else:
                file_helper.flow_dict["Detectors"][dict_key]["color"] = (
                    200,
                    125,
                    125,
                    255,
                )

        view.image_alteration.manipulate_image()

    def delete_section(self):
        """Deletes selected section  from flowfile and listboxwidget."""

        itemlist = list(self.tree_sections.selection())

        if not itemlist:
            info_message("Warning", "Please select detector you wish to delete!")

            return

        for sectionitem in itemlist:

            detector_name = self.tree_sections.item(sectionitem, "text")

            self.tree_sections.delete(sectionitem)

            del file_helper.flow_dict["Detectors"][detector_name]

            # # deletes detector in all movements
            # for key in file_helper.flow_dict["Movements"]:
            #     for value in file_helper.flow_dict["Movements"][key]:
            #         if detector_name in file_helper.flow_dict["Movements"][key]:
            #             file_helper.flow_dict["Movements"][key].remove(detector_name)

            # # update whole treeview 
            # for i in treeview_movements.get_children():
            #     treeview_movements.delete(i)

            file_helper.fill_tree_views(
                2,
                tree_movements=None,
                tree_sections =self.tree_sections,
            )

        view.image_alteration.manipulate_image()

    def create_section_entry_window(self):
        """Creates toplevel window to name view.sections."""

        file_helper.selectionlist_objects = []             

        # only if line or polygon creation is activate
        if button_bool["linedetector_toggle"] or button_bool["polygondetector_toggle"]:

            self.new_detector_creation = tk.Toplevel()
            self.new_detector_creation.geometry("%dx%d+%d+%d" % (250, 50, 850, 350))

            # removes hotkey so "enter" won't trigger
            keyboard.remove_hotkey("enter")

            detector_name_entry = tk.Entry(master=self.new_detector_creation)

            detector_name_entry.grid(row=1, column=0, sticky="w", pady=10, padx=10)
            detector_name_entry.focus()

            safe_section = tk.Button(
                master=self.new_detector_creation,
                text="Add section",
                command=lambda: [
                    self.add_section(detector_name_entry),
                ],
            )

            safe_section.grid(row=1, column=1, sticky="w", pady=10, padx=10)
            self.new_detector_creation.protocol("WM_DELETE_WINDOW", self.on_close)
            # makes the background window unavailable
            self.new_detector_creation.grab_set()

    def on_close(self):
        # hotkeys
        keyboard.add_hotkey(
            "enter",
            lambda: self.create_section_entry_window(),
        )
        self.new_detector_creation.destroy()

        helpers.config.maincanvas.delete_points()

        view.image_alteration.manipulate_image()

    def add_section(self, entrywidget):
        """Saves created section to flowfile.

        Args:
            maincanvas (tkinter.canvas): needed to hand over canvas coordinates.
            flow_dict (dictionary): Dictionary with view.sections and movements.
            entrywidget (tkinter.widget): Entrywidget to put in sectionname.
        """

        detector_name = entrywidget.get()

        if detector_name in file_helper.flow_dict["Detectors"].keys():
            tk.messagebox.showinfo(
                title="Warning", message="Sectionname already exists!"
            )

        else:

            # TODO: #67 Prevent duplicate section names
            view.sections.dump_to_flowdictionary(detector_name)

            self.tree_sections.insert(parent="", index="end", text=detector_name)

            self.on_close(),

    def add_section_to_movement(self, treeview_movements):
        """Adds selected section to selected movement."""

        item_movement = treeview_movements.selection()
        movement_name = treeview_movements.item(item_movement, "text")

        for item in self.tree_sections.selection():
            detector_name = self.tree_sections.item(item, "text")
            print(detector_name)

            if not detector_name or not movement_name:
                info_message("Warning", "Please select section and movements!")

                continue

            if detector_name not in file_helper.flow_dict["Movements"][movement_name]:

                file_helper.flow_dict["Movements"][movement_name].append(detector_name)
                

            else:
                info_message("Warning", "Detector already part of movement!")
       
        treeview_movements.set(item_movement,0,file_helper.flow_dict["Movements"][movement_name])
