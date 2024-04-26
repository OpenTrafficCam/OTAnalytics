import tkinter
from pathlib import Path
from typing import Any

from customtkinter import CTkButton, CTkFrame, CTkScrollbar

from OTAnalytics.adapter_ui.text_resources import ColumnResource, ColumnResources
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.plugin_ui.customtkinter_gui.constants import PADX, PADY, STICKY
from OTAnalytics.plugin_ui.customtkinter_gui.custom_containers import EmbeddedCTkFrame
from OTAnalytics.plugin_ui.customtkinter_gui.treeview_template import TreeviewTemplate


class FrameFiles(EmbeddedCTkFrame):
    def __init__(self, viewmodel: ViewModel, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._viewmodel = viewmodel
        self._get_widgets()
        self._place_widgets()
        self.introduce_to_viewmodel()

    def introduce_to_viewmodel(self) -> None:
        pass

    def _get_widgets(self) -> None:
        self._frame_tree = CTkFrame(master=self)
        self.treeview = TreeviewFiles(
            viewmodel=self._viewmodel, master=self._frame_tree
        )
        self._treeview_scrollbar = CTkScrollbar(
            master=self._frame_tree, command=self.treeview.yview
        )
        self.treeview.configure(yscrollcommand=self._treeview_scrollbar.set)
        self.button_add_files = CTkButton(
            master=self, text="Load", command=self._viewmodel.load_tracks
        )

    def _place_widgets(self) -> None:
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.treeview.pack(side=tkinter.LEFT, expand=True, fill=tkinter.BOTH)
        self._treeview_scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self._frame_tree.grid(
            row=0, column=0, columnspan=2, padx=PADX, pady=PADY, sticky=STICKY
        )
        self.button_add_files.grid(row=1, column=0, padx=PADX, pady=PADY, sticky=STICKY)


COLUMN_FILE = "File"
COLUMN_TRACKS = "Tracks"
COLUMN_VIDEO = "Video"


class TreeviewFiles(TreeviewTemplate):
    def __init__(self, viewmodel: ViewModel, **kwargs: Any) -> None:
        self._viewmodel = viewmodel
        super().__init__(show="tree headings", **kwargs)
        self._introduce_to_viewmodel()
        self.update_items()

    def _define_columns(self) -> None:
        columns = [COLUMN_FILE, COLUMN_TRACKS, COLUMN_VIDEO]
        self["columns"] = columns
        self.column(column="#0", width=0, stretch=False)
        self.column(column=COLUMN_FILE, anchor=tkinter.CENTER, width=150, minwidth=40)
        self.column(
            column=COLUMN_TRACKS,
            anchor=tkinter.CENTER,
            width=50,
            minwidth=50,
            stretch=False,
        )
        self.column(
            column=COLUMN_VIDEO,
            anchor=tkinter.CENTER,
            width=50,
            minwidth=50,
            stretch=False,
        )
        self["displaycolumns"] = columns
        for column in columns:
            self.heading(column=column, text=column)

    def _introduce_to_viewmodel(self) -> None:
        self._viewmodel.set_treeview_files(self)

    def _notify_viewmodel_about_selected_item_ids(self, ids: list[str]) -> None:
        pass

    def _on_double_click(self, event: Any) -> None:
        pass

    def update_items(self) -> None:
        self.delete(*self.get_children())
        track_files = self._viewmodel.get_all_track_files()
        videos = self._viewmodel.get_all_videos()
        track_files_have_videos = []
        for file in track_files:
            if file.stem in [video.get_path().stem for video in videos]:
                track_files_have_videos.append(True)
            else:
                track_files_have_videos.append(False)

        item_ids = ColumnResources(
            [
                self.__to_resource(file=file, video_loaded=video_loaded)
                for file, video_loaded in zip(track_files, track_files_have_videos)
            ],
            lookup_column=COLUMN_FILE,
        )
        self.add_items(item_ids=item_ids)

    @staticmethod
    def __to_resource(
        file: Path, video_loaded: bool, tracks_loaded: bool = True
    ) -> ColumnResource:
        values = {
            COLUMN_FILE: file.stem,
            COLUMN_TRACKS: "x" if tracks_loaded else "",
            COLUMN_VIDEO: "x" if video_loaded else "",
        }
        return ColumnResource(id=str(file), values=values)
