import tkinter as tk
from view_movements import FrameMovements
from view_helpers import FrameFiles
from canvas import CanvasFrame
from view_sections import FrameSection
from view_objects import FrameObject
from gui_helper import button_bool
import keyboard
import config
import file_helper
import image_alteration
import sections


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
                    self.on_close(),
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

        # TODO: #67 Prevent duplicate section names
        sections.dump_to_flowdictionary(detector_name)

        self.frame_sections.tree_sections.insert(
            parent="", index="end", text=detector_name
        )


def main():
    """Main function."""
    app = test_gui()
    app.mainloop()


if __name__ == "__main__":
    main()
