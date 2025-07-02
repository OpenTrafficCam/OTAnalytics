import asyncio
import tkinter
from typing import Any

from customtkinter import CTkButton, CTkFrame, CTkScrollbar

from OTAnalytics.adapter_ui.text_resources import ColumnResource, ColumnResources
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.domain.video import Video
from OTAnalytics.plugin_ui.customtkinter_gui.abstract_ctk_frame import AbstractCTkFrame
from OTAnalytics.plugin_ui.customtkinter_gui.constants import PADX, PADY, STICKY
from OTAnalytics.plugin_ui.customtkinter_gui.treeview_template import TreeviewTemplate


class FrameVideos(AbstractCTkFrame):
    def __init__(self, viewmodel: ViewModel, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._viewmodel = viewmodel
        self._get_widgets()
        self._place_widgets()
        self._set_initial_button_states()
        self.introduce_to_viewmodel()

    def introduce_to_viewmodel(self) -> None:
        self._viewmodel.set_video_frame(self)

    def _get_widgets(self) -> None:
        self._frame_tree = CTkFrame(master=self)
        self.treeview = TreeviewVideos(
            viewmodel=self._viewmodel, master=self._frame_tree
        )
        self._treeview_scrollbar = CTkScrollbar(
            master=self._frame_tree, command=self.treeview.yview
        )
        self.treeview.configure(yscrollcommand=self._treeview_scrollbar.set)
        self.button_add_videos = CTkButton(
            master=self, text="Add...", command=self._do_add_video
        )
        self.button_remove_videos = CTkButton(
            master=self, text="Remove", command=self._do_remove_videos
        )

    def _do_remove_videos(self) -> None:
        self._viewmodel.remove_videos()

    def _do_add_video(self) -> None:
        asyncio.run(self._viewmodel.add_video())

    def _place_widgets(self) -> None:
        self.treeview.pack(side=tkinter.LEFT, expand=True, fill=tkinter.BOTH)
        self._treeview_scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self._frame_tree.grid(
            row=0, column=0, columnspan=2, padx=PADX, pady=PADY, sticky=STICKY
        )
        self.button_add_videos.grid(
            row=1, column=0, padx=PADX, pady=PADY, sticky=STICKY
        )
        self.button_remove_videos.grid(
            row=1, column=1, padx=PADX, pady=PADY, sticky=STICKY
        )

    def _set_initial_button_states(self) -> None:
        self.set_enabled_general_buttons(True)
        self.set_enabled_add_buttons(True)
        self.set_enabled_change_single_item_buttons(False)
        self.set_enabled_change_multiple_items_buttons(False)

    def get_general_buttons(self) -> list[CTkButton]:
        return [self.button_add_videos]

    def get_multiple_items_buttons(self) -> list[CTkButton]:
        return [self.button_remove_videos]


COLUMN_VIDEO = "Video files"


class TreeviewVideos(TreeviewTemplate):
    def __init__(self, viewmodel: ViewModel, **kwargs: Any) -> None:
        self._viewmodel = viewmodel
        super().__init__(**kwargs)
        self._introduce_to_viewmodel()
        self.update_items()

    def _define_columns(self) -> None:
        columns = [COLUMN_VIDEO]
        self["columns"] = columns
        self.column(column="#0", width=0, stretch=False)
        self.column(column=COLUMN_VIDEO, anchor=tkinter.CENTER, width=150, minwidth=40)
        self["displaycolumns"] = columns

    def _introduce_to_viewmodel(self) -> None:
        self._viewmodel.set_treeview_videos(self)

    def _notify_viewmodel_about_selected_item_ids(self, ids: list[str]) -> None:
        self._viewmodel.set_selected_videos(ids)

    def _on_double_click(self, event: Any) -> None:
        pass

    def update_items(self) -> None:
        self.delete(*self.get_children())
        item_ids = ColumnResources(
            [self.__to_resource(video) for video in self._viewmodel.get_all_videos()],
            lookup_column=COLUMN_VIDEO,
        )
        self.add_items(item_ids=item_ids)

    @staticmethod
    def __to_resource(video: Video) -> ColumnResource:
        values = {COLUMN_VIDEO: video.get_path().name}
        return ColumnResource(id=str(video.get_path()), values=values)
