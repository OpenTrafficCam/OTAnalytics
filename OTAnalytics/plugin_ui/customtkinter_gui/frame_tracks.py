from typing import Any

from customtkinter import CTkButton

from OTAnalytics.adapter_ui.abstract_frame_tracks import AbstractFrameTracks
from OTAnalytics.adapter_ui.default_values import RELATIVE_SECTION_OFFSET
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.domain import geometry
from OTAnalytics.plugin_ui.customtkinter_gui.constants import PADX, PADY, STICKY
from OTAnalytics.plugin_ui.customtkinter_gui.frame_bbox_offset import FrameBboxOffset


class TracksFrame(AbstractFrameTracks):
    def __init__(self, viewmodel: ViewModel, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._viewmodel = viewmodel
        self._get_widgets()
        self._place_widgets()
        self.introduce_to_viewmodel()

    def introduce_to_viewmodel(self) -> None:
        self._viewmodel.set_tracks_frame(self)

    def _get_widgets(self) -> None:
        # self.label = CTkLabel(master=self, text="Tracks")
        self.button_load_tracks = CTkButton(
            master=self, text="Load", command=self._viewmodel.load_tracks
        )
        self._frame_bbox_offset = FrameBboxOffset(
            master=self,
            frame_heading="Offset",
            relative_offset_coordinates=RELATIVE_SECTION_OFFSET.to_dict(),
        )
        self.button_update_offset = CTkButton(
            master=self,
            text="Update plot",
            command=self._on_change_offset,
        )
        self.button_change_to_section_offset = CTkButton(
            master=self,
            text="Update with section offset",
            command=self._on_change_to_section_offset,
        )
        if current_track_offset := self._viewmodel.get_track_offset():
            self.update_offset(*current_track_offset)

    def _place_widgets(self) -> None:
        # self.label.grid(
        #     row=0, column=0, columnspan=2, padx=PADX, pady=PADY, sticky=STICKY
        # )
        self.button_load_tracks.grid(
            row=1, column=0, padx=PADX, pady=PADY, sticky=STICKY
        )
        self._frame_bbox_offset.grid(
            row=2, column=0, padx=PADX, pady=PADY, sticky=STICKY
        )
        self.button_update_offset.grid(
            row=3, column=0, padx=PADX, pady=PADY, sticky=STICKY
        )
        self.button_change_to_section_offset.grid(
            row=4, column=0, padx=PADX, pady=PADY, sticky=STICKY
        )

    def update_offset(self, new_offset_x: float, new_offset_y: float) -> None:
        self._frame_bbox_offset.set_relative_offset_coordintes(
            x=new_offset_x, y=new_offset_y
        )

    def _on_change_offset(self) -> None:
        offset_coordinates = self._frame_bbox_offset.get_relative_offset_coordintes()
        self._viewmodel.set_track_offset(
            offset_coordinates[geometry.X], offset_coordinates[geometry.Y]
        )

    def _on_change_to_section_offset(self) -> None:
        self._viewmodel.change_track_offset_to_section_offset()
