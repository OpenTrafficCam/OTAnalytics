import tkinter
from pathlib import Path
from typing import Any

from customtkinter import CTkFrame, CTkScrollbar

from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.plugin_ui.customtkinter_gui.constants import PADX, PADY, STICKY
from OTAnalytics.plugin_ui.customtkinter_gui.custom_containers import EmbeddedCTkFrame
from OTAnalytics.plugin_ui.customtkinter_gui.treeview_template import (
    IdResource,
    TreeviewTemplate,
)


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
        # self.button_add_videos = CTkButton(
        #     master=self, text="Load", command=self._viewmodel.add_video
        # )
        # self.button_remove_videos = CTkButton(
        #     master=self, text="Remove", command=self._viewmodel.remove_videos
        # )

    def _place_widgets(self) -> None:
        self.treeview.pack(side=tkinter.LEFT, expand=True, fill=tkinter.BOTH)
        self._treeview_scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self._frame_tree.grid(
            row=0, column=0, columnspan=2, padx=PADX, pady=PADY, sticky=STICKY
        )
        # self.button_add_videos.grid(
        #     row=1, column=0, padx=PADX, pady=PADY, sticky=STICKY
        # )
        # self.button_remove_videos.grid(
        #     row=1, column=1, padx=PADX, pady=PADY, sticky=STICKY
        # )


COLUMN_FILE = "File"
COLUMN_TRACKS = "Tracks"
COLUMN_VIDEO = "Video"


class TreeviewFiles(TreeviewTemplate):
    def __init__(self, viewmodel: ViewModel, **kwargs: Any) -> None:
        self._viewmodel = viewmodel
        super().__init__(**kwargs)
        self._define_columns()
        self._introduce_to_viewmodel()
        self.update_items()

    def _define_columns(self) -> None:
        columns = [COLUMN_FILE, COLUMN_TRACKS, COLUMN_VIDEO]
        self["columns"] = columns
        self.column(column="#0", width=0, stretch=False)
        self.column(column=COLUMN_FILE, anchor=tkinter.CENTER, width=150, minwidth=40)
        self.column(column=COLUMN_TRACKS, anchor=tkinter.CENTER, width=20, minwidth=20)
        self.column(column=COLUMN_VIDEO, anchor=tkinter.CENTER, width=20, minwidth=20)
        self["displaycolumns"] = columns
        for column in columns:
            self.heading(column=column, text=column)

    def _introduce_to_viewmodel(self) -> None:
        self._viewmodel.set_treeview_files(self)

    def _notify_viewmodel_about_selected_item_ids(self, ids: list[str]) -> None:
        # TODO
        pass

    def _on_double_click(self, event: Any) -> None:
        # TODO
        pass

    def update_items(self) -> None:
        self.delete(*self.get_children())
        track_files = self._viewmodel.get_all_track_files()
        videos = self._viewmodel.get_all_videos()
        track_files_have_videos = []
        for file in track_files:
            if file.stem in [video.get_path().stem for video in videos]:
                track_files_have_videos.append("Yes")
            else:
                track_files_have_videos.append("No")

        item_ids = [self.__to_id_resource(file) for file in track_files]
        self.add_items(item_ids=item_ids)

    def __to_id_resource(self, file: Path) -> IdResource:
        return IdResource(id=str(file), name=file.stem)
