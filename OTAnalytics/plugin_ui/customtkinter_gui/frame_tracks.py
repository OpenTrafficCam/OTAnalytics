import asyncio
from typing import Any

from customtkinter import CTkButton, ThemeManager

from OTAnalytics.adapter_ui.abstract_frame_offset import AbstractFrameOffset
from OTAnalytics.adapter_ui.default_values import RELATIVE_SECTION_OFFSET
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.plugin_ui.customtkinter_gui.abstract_ctk_frame import AbstractCTkFrame
from OTAnalytics.plugin_ui.customtkinter_gui.constants import (
    PADX,
    PADY,
    STATE_DISABLED,
    STATE_NORMAL,
    STICKY,
)
from OTAnalytics.plugin_ui.customtkinter_gui.frame_bbox_offset import FrameBboxOffset
from OTAnalytics.plugin_ui.customtkinter_gui.style import COLOR_ORANGE


def get_default_offset_button_color() -> str:
    return ThemeManager.theme["CTkButton"]["fg_color"]


class TracksFrame(AbstractFrameOffset, AbstractCTkFrame):
    def __init__(self, viewmodel: ViewModel, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._viewmodel = viewmodel
        self.grid_columnconfigure(1, weight=1)
        self._get_widgets()
        self._place_widgets()
        self._set_initial_button_states()
        self.introduce_to_viewmodel()

    def introduce_to_viewmodel(self) -> None:
        self._viewmodel.set_tracks_frame(self)
        self._viewmodel.set_offset_frame(self)

    def _get_widgets(self) -> None:
        self.button_load_tracks = CTkButton(
            master=self, text="Add tracks...", command=self._do_load_tracks
        )
        self._frame_bbox_offset = FrameBboxOffset(
            master=self,
            frame_heading="Offset",
            relative_offset_coordinates=RELATIVE_SECTION_OFFSET.to_dict(),
            notify_change=self._viewmodel.set_track_offset,
        )
        self.button_change_to_section_offset = CTkButton(
            master=self,
            text="Update with section offset",
            command=self._on_change_to_section_offset,
        )
        if current_track_offset := self._viewmodel.get_track_offset():
            self.update_offset(*current_track_offset)

    def _do_load_tracks(self) -> None:
        asyncio.run(self._viewmodel.load_tracks())

    def _place_widgets(self) -> None:
        self.button_load_tracks.grid(
            row=0, column=0, padx=PADX, pady=PADY, sticky=STICKY
        )
        self._frame_bbox_offset.grid(
            row=1, column=0, columnspan=2, padx=PADX, pady=PADY, sticky=STICKY
        )
        self.button_change_to_section_offset.grid(
            row=2, column=0, padx=PADX, pady=PADY, sticky=STICKY
        )

    def _set_initial_button_states(self) -> None:
        self.set_enabled_general_buttons(True)
        self.set_enabled_add_buttons(True)
        self.set_enabled_change_single_item_buttons(False)
        self.set_enabled_change_multiple_items_buttons(False)

    def update_offset(self, new_offset_x: float, new_offset_y: float) -> None:
        self._frame_bbox_offset.set_relative_offset_coordintes(
            x=new_offset_x, y=new_offset_y
        )

    def _on_change_to_section_offset(self) -> None:
        self._viewmodel.change_track_offset_to_section_offset()

    def get_general_buttons(self) -> list[CTkButton]:
        return [self.button_load_tracks]

    def get_single_item_buttons(self) -> list[CTkButton]:
        return [self.button_change_to_section_offset]

    def enable_update_offset_button(self, enabled: bool) -> None:
        if enabled:
            self.button_change_to_section_offset.configure(state=STATE_NORMAL)
            self.button_change_to_section_offset.configure(fg_color=COLOR_ORANGE)
        else:
            self.button_change_to_section_offset.configure(state=STATE_DISABLED)
            color = get_default_offset_button_color()
            self.button_change_to_section_offset.configure(fg_color=color)
