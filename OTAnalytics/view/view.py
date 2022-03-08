import tkinter as tk
from view_movements import FrameMovements
from view_helpers import FrameFiles
from canvas import CanvasFrame
from view_sections import FrameSection
from view_objects import FrameObject
from gui_helper import button_bool, info_message
import keyboard
import config
import file_helper
import image_alteration
import sections
import json


class test_gui(tk.Tk):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title("OTAnalytics")
        self.set_layout()

        self.title("OTAnalytics")

        # hotkeys
        keyboard.add_hotkey(
            "enter",
            lambda: self.create_section_entry_window(),
        )

    def set_layout(
        self,
    ):
        self.frame_controll_panel = tk.Frame(master=self)
        self.frame_controll_panel.pack(side="left", anchor="n")

        self.frame_canvas = tk.Frame(master=self)
        self.frame_canvas.pack(side="right")

        self.canvas = CanvasFrame(master=self.frame_canvas)
        self.canvas.pack()

        self.frame_files = FrameFiles(master=self.frame_controll_panel)
        self.frame_files.grid(
            **{"padx": 10, "pady": 10}, row=0, column=0, columnspan=2, sticky="ew"
        )

        self.videolabel = tk.Label(
            master=self.frame_controll_panel,
            text="Sections and Objects",
            fg="white",
            bg="#37483E",
        )
        self.videolabel.grid(
            **{"padx": 10, "pady": 10}, row=1, column=0, columnspan=2, sticky="ew"
        )

        self.frame_sections = FrameSection(master=self.frame_controll_panel)
        self.frame_sections.grid(
            **{"padx": 10, "pady": 0}, row=2, column=0, sticky="ew"
        )

        self.frame_objects = FrameObject(master=self.frame_controll_panel)
        self.frame_objects.grid(**{"padx": 10, "pady": 0}, row=2, column=1, sticky="ew")

        self.frame_movements = FrameMovements(master=self.frame_controll_panel)
        self.frame_movements.grid(
            **{"padx": 10, "pady": 10}, row=3, column=0, sticky="ew"
        )

        # Load flow_dict
        self.button_load_flowfile = tk.Button(
            master=self.frame_controll_panel, text="Load", command=self.import_flowfile
        )
        self.button_load_flowfile.grid(row=4, column=0, sticky="ew")

        # Add save flow_dict
        self.button_save_flowfile = tk.Button(
            master=self.frame_controll_panel,
            text="Save",
            command=sections.save_flowfile,
        )
        self.button_save_flowfile.grid(row=5, column=0, sticky="ew")

        # Add clear all
        self.button_save_flowfile = tk.Button(
            master=self.frame_controll_panel,
            text="Clear all",
            command=self.clear_treeviews,
        )
        self.button_save_flowfile.grid(row=6, column=0, sticky="ew")

        # bind function to button (function effects to treeview)
        self.frame_sections.button_add_section_to_movement.configure(
            command=self.add_section_to_movement
        )

    def create_section_entry_window(self):
        """Creates toplevel window to name sections."""

        # only if line or polygon creation is activate
        if button_bool["linedetector_toggle"] or button_bool["polygondetector_toggle"]:

            self.new_detector_creation = tk.Toplevel()

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

        config.maincanvas.delete_polygon_points()

        image_alteration.manipulate_image()

    def add_section(self, entrywidget):
        """Saves created section to flowfile.

        Args:
            maincanvas (tkinter.canvas): needed to hand over canvas coordinates.
            flow_dict (dictionary): Dictionary with sections and movements.
            entrywidget (tkinter.widget): Entrywidget to put in sectionname.
        """

        detector_name = entrywidget.get()

        if detector_name in file_helper.flow_dict["Detectors"].keys():
            tk.messagebox.showinfo(
                title="Warning", message="Sectionname already exists"
            )

        else:

            # TODO: #67 Prevent duplicate section names
            sections.dump_to_flowdictionary(detector_name)

            self.frame_sections.tree_sections.insert(
                parent="", index="end", text=detector_name
            )

            self.on_close(),

    def import_flowfile(self):
        """Calls load_flowfile-function and inserts sections to listboxwidget."""
        file_helper.flow_dict = sections.load_flowfile()

        image_alteration.manipulate_image()

        for movement in file_helper.flow_dict["Movements"]:
            self.frame_movements.tree_movements.insert(
                parent="", index="end", text=movement
            )

        for detector in file_helper.flow_dict["Detectors"]:
            self.frame_sections.tree_sections.insert(
                parent="", index="end", text=detector
            )

    def clear_treeviews(self):
        for i in self.frame_sections.tree_sections.get_children():
            self.frame_sections.tree_sections.delete(i)

        for i in self.frame_objects.tree_objects.get_children():
            self.frame_objects.tree_objects.delete(i)

        for i in self.frame_movements.tree_movements.get_children():
            self.frame_movements.tree_movements.delete(i)

        file_helper.re_initialize()

    def add_section_to_movement(self):
        """Adds selected section to selected movement."""
        item = self.frame_sections.tree_sections.selection()
        detector_name = self.frame_sections.tree_sections.item(item, "text")

        item = self.frame_movements.tree_movements.selection()
        movement_name = self.frame_movements.tree_movements.item(item, "text")

        if not detector_name or not movement_name:
            info_message("Warning", "Please select section and movements")

            return

        file_helper.flow_dict["Movements"][movement_name].append(detector_name)

        print(file_helper.flow_dict["Movements"])

        # detector_name = (
        #     detector_name
        #     + " #"
        #     + str(self.flow_dict["Movements"][movement_name].index(detector_name) + 1)
        # )

        self.frame_movements.tree_movements.insert(detector_name, "values")

    def ask_to_import(self, path, otflow_file, ottrk_file):
        if self.frame_files.files_dict[path]["otflow_file"] == "\u2705":

            response = tk.messagebox.askquestion(
                title="Files detected",
                message="Do you want to import existent flowfile?",
            )

            if response == "yes":

                filepath = f"{path}/{otflow_file}"

                files = open(filepath, "r")
                files = files.read()

                file_helper.flow_dict = json.loads(files)

            else:
                print("response was false")


def main():
    """Main function."""
    app = test_gui()
    app.mainloop()


if __name__ == "__main__":
    main()
