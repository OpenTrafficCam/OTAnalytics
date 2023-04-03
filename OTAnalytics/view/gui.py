import tkinter as tk
from view.helpers.view_movements import FrameMovements
from view.helpers.view_files import FrameFiles
from view.canvas import CanvasFrame
from view.helpers.view_sections import FrameSection
from view.helpers.view_tracks import FrameObject
from view.helpers.gui_helper import (
    info_message,
    button_bool,
    button_display_tracks_switch,
)
import keyboard
import helpers.config
import helpers.file_helper as file_helper
import view.image_alteration
import view.sections
import json
from view.tracks import load_and_convert, deload_trackfile


class gui(tk.Tk):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title("OTAnalytics")
        self.set_layout()

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

        self.frame_files.button_remove_video.configure(
            command=lambda: [
                deload_trackfile(),
                self.frame_objects.clear_treeview(),
                self.frame_files.remove_video(),
                
            ]
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
        self.frame_files.button_add_folder.configure(
            command = self.folder_load_video_add_frame

        )

        self.frame_sections.button_remove_section.configure(
            command=lambda: [
                self.frame_sections.delete_section(self.frame_movements.tree_movements)
            ]
        )
        self.frame_files.tree_files.bind('<ButtonRelease-1>',self.reupdate_tree_objects, add="+")
 
    def reupdate_tree_objects(self, event):

        print(f"index: {file_helper.list_of_analyses_index}")
        for item in self.frame_objects.tree_objects.get_children():
            self.frame_objects.tree_objects.delete(item)
        print(file_helper.list_of_analyses[file_helper.list_of_analyses_index].track_file)
        if bool(file_helper.list_of_analyses[file_helper.list_of_analyses_index].track_file):

            for object in file_helper.list_of_analyses[file_helper.list_of_analyses_index].tracks_df.index:
                    self.frame_objects.tree_objects.insert(
                    parent="",
                    index="end",
                    text=object,
                    values=file_helper.list_of_analyses[file_helper.list_of_analyses_index].tracks_dic[object]["Class"],
                )

    def load_video_and_add_frame(self):

        # if file_helper.list_of_analyses[file_helper.list_of_analyses_index]:
        #     info_message("Warning", "Please remove video before adding a new one!")

        #     return

        self.frame_files.add_file()
        self.frame_files.add_canvas_frame()
        self.ask_to_import()

        view.image_alteration.manipulate_image()

    def folder_load_video_add_frame(self):
        self.frame_files.add_folder()
        self.frame_files.add_canvas_frame()

        self.ask_to_import_all_trackfiles()
    

    def import_flowfile(self):
        """Calls load_flowfile-function and inserts view.sections to listboxwidget."""
        view.sections.load_flowfile()

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

            file_helper.list_of_analyses[file_helper.list_of_analyses_index].videoobject.initialize_empty_image()


            view.image_alteration.manipulate_image()

        else:
            info_message("Warning", "Nothing to clear!")

    def ask_to_import(self):

        path = file_helper.list_of_analyses[file_helper.list_of_analyses_index].folder_path

        if file_helper.list_of_analyses[file_helper.list_of_analyses_index].flowfile_existence and file_helper.ask_to_import_flowfile:

            response_flowfile = tk.messagebox.askquestion(
                title="otflowfile detected",
                message="Do you want to import existent flowfile?",
            )

            if response_flowfile == "yes":

                filepath = f"{path}/{file_helper.otflow_file}"

                files = open(filepath, "r")
                files = files.read()

                file_helper.flow_dict = json.loads(files)

            #stop asking
            file_helper.ask_to_import_flowfile = False
            file_helper.fill_tree_views(
            3,
            self.frame_movements.tree_movements,
            self.frame_sections.tree_sections,
        )

        if file_helper.list_of_analyses[file_helper.list_of_analyses_index].trackfile_existence and file_helper.ask_to_import_trackfile:

            response_track_file = tk.messagebox.askquestion(
                title="Ottrackfile detected",
                message="Do you want to import existent trackfile?",
            )

            if response_track_file == "yes":


                filepath = f"{path}/{file_helper.list_of_analyses[file_helper.list_of_analyses_index].track_file}"

     

                (
                file_helper.list_of_analyses[file_helper.list_of_analyses_index].raw_detections,
                file_helper.list_of_analyses[file_helper.list_of_analyses_index].tracks_dic,
                file_helper.list_of_analyses[file_helper.list_of_analyses_index].tracks_df,
                file_helper.list_of_analyses[file_helper.list_of_analyses_index].tracks_geoseries,
                ) = load_and_convert(
                    x_resize_factor=file_helper.list_of_analyses[file_helper.list_of_analyses_index].videoobject.x_resize_factor,
                    y_resize_factor=file_helper.list_of_analyses[file_helper.list_of_analyses_index].videoobject.y_resize_factor,
                    autoimport=True,
                    files=filepath,
                )
                button_display_tracks_switch(self.frame_objects.button_show_tracks)

                self.fill_track_treeview()
            else:
                # delete found trackfile from analyse class
                file_helper.list_of_analyses[file_helper.list_of_analyses_index].track_file = None

    def ask_to_import_all_trackfiles(self):
        response_track_file = tk.messagebox.askquestion(
                title="Ottrackfile",
                message="Do you want to import corresponding trackfiles if found in folder?",
            )
        if response_track_file == "yes":
            for analyse in file_helper.list_of_analyses:

                #use trackfile if existent
                if analyse.track_file:
                    path = file_helper.list_of_analyses[file_helper.list_of_analyses_index].folder_path
                    filepath = f"{path}/{analyse.track_file}"
                    files = open(filepath, "r")
                    files = files.read()    

                    (analyse.raw_detections,
                    analyse.tracks_dic,
                    analyse.tracks_df,
                    analyse.tracks_geoseries,
                    ) = load_and_convert(
                        x_resize_factor=analyse.videoobject.x_resize_factor,
                        y_resize_factor=analyse.videoobject.y_resize_factor,
                        autoimport=True,
                        files=files,)
            self.fill_track_treeview()       
            

    def fill_track_treeview(self):
        for object in file_helper.list_of_analyses[file_helper.list_of_analyses_index].tracks_df.index:
            self.frame_objects.tree_objects.insert(
                parent="",
                index="end",
                text=object,
                values=file_helper.list_of_analyses[file_helper.list_of_analyses_index].tracks_dic[object]["Class"],
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
