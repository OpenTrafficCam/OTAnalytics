import tkinter as tk
from view.view_movements import FrameMovements
from view.view_helpers import FrameFiles
from view.canvas import CanvasFrame
from view.view_sections import FrameSection
from view.view_objects import FrameObject
from view.helpers.gui_helper import (
    info_message,
    button_bool,
    button_display_tracks_switch,
)
import keyboard
import view.config as config
import helpers.file_helper as file_helper
import view.image_alteration
import view.sections
import json
from view.tracks import load_and_convert


class gui(tk.Tk):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title("OTAnalytics")
        self.set_layout()

        self.title("OTAnalytics")

        # hotkeys
        keyboard.add_hotkey(
            "enter",
            lambda: self.frame_sections.create_section_entry_window(),
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

        # self.videolabel = tk.Label(
        #     master=self.frame_controll_panel,
        #     text="Sections and Objects",
        #     fg="white",
        #     bg="#37483E",
        # )
        # self.videolabel.grid(
        #     **{"padx": 10, "pady": 10}, row=1, column=0, columnspan=2, sticky="ew"
        # )

        self.frame_sections = FrameSection(master=self.frame_controll_panel)
        self.frame_sections.grid(
            **{"padx": (10, 2.5), "pady": 0}, row=2, column=0, sticky="new"
        )

        self.frame_objects = FrameObject(master=self.frame_controll_panel)
        self.frame_objects.grid(
            **{"padx": (2.5, 10), "pady": 0}, row=2, column=1, sticky="new", rowspan=3
        )

        self.frame_movements = FrameMovements(master=self.frame_controll_panel)
        self.frame_movements.grid(
            **{"padx": (10, 2.5), "pady": 0}, row=3, column=0, sticky="new"
        )

        # # Load flow_dict
        # self.button_load_flowfile = tk.Button(
        #     master=self.frame_controll_panel,
        #     text="Load flowfile",
        #     command=self.import_flowfile,
        # )
        # self.button_load_flowfile.grid(row=4, column=0, sticky="ew")

        # # Add save flow_dict
        # self.button_save_flowfile = tk.Button(
        #     master=self.frame_controll_panel,
        #     text="Save sections and movements",
        #     command=view.sections.save_flowfile,
        # )
        # self.button_save_flowfile.grid(row=5, column=0, sticky="ew")

        # Add clear all
        self.button_clear_all = tk.Button(
            master=self.frame_controll_panel,
            text="Clear all",
            command=self.clear_treeviews,
        )
        # pixel alignment
        self.button_clear_all.grid(
            **{"padx": 10, "pady": 10}, row=4, column=0, columnspan=2, sticky="ew"
        )

        # bind function to button (function effects to treeview)
        self.frame_sections.button_add_section_to_movement.configure(
            command=lambda: [
                self.frame_sections.add_section_to_movement(
                    self.frame_movements.tree_movements
                )
            ]
        )

        self.frame_files.button_add_video.configure(
            command=self.load_video_and_add_frame
        )

        self.frame_sections.button_remove_section.configure(
            command=lambda: [
                self.frame_sections.delete_section(self.frame_movements.tree_movements)
            ]
        )
        # self.frame_movements.button_autocreate_movement.configure(
        #     command=self.autocreate_movements_from_sections
        # )

    def load_video_and_add_frame(self):

        if config.videoobject:
            info_message("Warning", "Please remove video before adding a new one!")

            return

        self.frame_files.add_file()
        self.frame_files.add_canvas_frame()
        self.ask_to_import()

        view.image_alteration.manipulate_image()

    def import_flowfile(self):
        """Calls load_flowfile-function and inserts view.sections to listboxwidget."""
        file_helper.flow_dict = view.sections.load_flowfile()

        view.image_alteration.manipulate_image()

        file_helper.fill_tree_views(
            3,
            self.frame_movements.tree_movements,
            self.frame_sections.tree_sections,
        )

    def clear_treeviews(self):
        if (
            self.frame_sections.tree_sections.get_children()
            or self.frame_objects.tree_objects.get_children()
            or self.frame_movements.tree_movements.get_children()
        ):
            for i in self.frame_sections.tree_sections.get_children():
                self.frame_sections.tree_sections.delete(i)

            for i in self.frame_objects.tree_objects.get_children():
                self.frame_objects.tree_objects.delete(i)

            for i in self.frame_movements.tree_movements.get_children():
                self.frame_movements.tree_movements.delete(i)

            file_helper.re_initialize()

            button_bool["tracks_imported"] = False

            view.image_alteration.manipulate_image()

        else:
            info_message("Warning", "Nothing to clear!")

    def autocreate_movements_from_sections(self):
        pass
        # itemlist = list(self.frame_sections.tree_sections.selection())

        # list_movements = list(file_helper.powerset(itemlist))

        # listmovements_reversed = list(file_helper.powerset(itemlist[::-1]))

    def ask_to_import(self):

        path = list(self.frame_files.files_dict.keys())[-1]

        if self.frame_files.files_dict[path]["otflow_file"] == "\u2705":

            response_flowfile = tk.messagebox.askquestion(
                title="Otflowfile detected",
                message="Do you want to import existent flowfile?",
            )

            if response_flowfile == "yes":

                filepath = f"{path}/{file_helper.otflow_file}"

                files = open(filepath, "r")
                files = files.read()

                file_helper.flow_dict = json.loads(files)

        if self.frame_files.files_dict[path]["ottrk_file"] == "\u2705":

            response_track_file = tk.messagebox.askquestion(
                title="Ottrackfile detected",
                message="Do you want to import existent trackfile?",
            )

            if response_track_file == "yes":

                filepath = f"{path}/{file_helper.ottrk_file}"

                files = open(filepath, "r")
                files = files.read()

                file_helper.raw_detections, file_helper.tracks = load_and_convert(
                    x_factor=config.videoobject.x_resize_factor,
                    y_factor=config.videoobject.y_resize_factor,
                    autoimport=True,
                    filepath=files,
                )
                button_display_tracks_switch(self.frame_objects.button_show_tracks)

            for object in list(file_helper.tracks.keys()):
                self.frame_objects.tree_objects.insert(
                    parent="",
                    index="end",
                    text=object,
                    values=file_helper.tracks[object]["Class"],
                )

        file_helper.fill_tree_views(
            3,
            self.frame_movements.tree_movements,
            self.frame_sections.tree_sections,
        )


def main():
    """Main function."""
    app = gui()
    try:
        app.iconbitmap("OTAnalytics\\gui\\OTC.ico")
    except tk.TclError:
        app.iconbitmap("OTC.ico")
    app.resizable(False, False)
    menubar = tk.Menu(app)
    file = tk.Menu(
        menubar,
        tearoff=1,
    )

    file.add_command(label="Import flowfile", command=app.import_flowfile)
    file.add_command(label="Save configuration", command=view.sections.save_flowfile)
    file.add_separator()
    file.add_command(label="Exit", command=app.quit)
    menubar.add_cascade(label="File", menu=file)
    app.config(menu=menubar)
    app.mainloop()


if __name__ == "__main__":
    main()
