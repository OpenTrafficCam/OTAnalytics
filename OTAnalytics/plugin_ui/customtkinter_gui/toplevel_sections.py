from typing import Any

from customtkinter import CTkEntry, CTkLabel

from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.application import CancelAddSection
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate
from OTAnalytics.domain.section import ID, NAME, RELATIVE_OFFSET_COORDINATES
from OTAnalytics.domain.types import EventType
from OTAnalytics.plugin_ui.customtkinter_gui.constants import PADX, PADY, STICKY
from OTAnalytics.plugin_ui.customtkinter_gui.frame_bbox_offset import FrameBboxOffset
from OTAnalytics.plugin_ui.customtkinter_gui.toplevel_template import (
    FrameContent,
    ToplevelTemplate,
)


class NoUniqueNameException(Exception):
    pass


class FrameConfigureSection(FrameContent):
    def __init__(
        self,
        viewmodel: ViewModel,
        section_offset: RelativeOffsetCoordinate,
        input_values: dict | None,
        show_offset: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._show_offset = show_offset
        self._viewmodel = viewmodel
        self._input_values: dict = (
            {
                ID: "",
                NAME: "",
                RELATIVE_OFFSET_COORDINATES: {
                    EventType.SECTION_ENTER.serialize(): {
                        "x": section_offset.x,
                        "y": section_offset.y,
                    },
                },
            }
            if input_values is None
            else input_values
        )
        self._get_widgets()
        self._place_widgets()

    def set_focus(self) -> None:
        self.after(0, lambda: self.entry_name.focus_set())

    def _get_widgets(self) -> None:
        self.label_name = CTkLabel(master=self, text="Name:")
        self.entry_name = CTkEntry(master=self, width=180)
        self.entry_name.insert(0, self._input_values[NAME])

        self.frame_bbox_offset = FrameBboxOffset(
            master=self,
            frame_heading="Bounding Box offset for enter-events:",
            relative_offset_coordinates=self._input_values[RELATIVE_OFFSET_COORDINATES][
                EventType.SECTION_ENTER.serialize()
            ],
        )

    def _place_widgets(self) -> None:
        self.label_name.grid(row=0, column=0, padx=PADX, pady=PADY, sticky="E")
        self.entry_name.grid(row=0, column=1, padx=PADX, pady=PADY, sticky="W")
        if self._show_offset:
            self.frame_bbox_offset.grid(
                row=1, column=0, columnspan=2, padx=PADX, sticky=STICKY
            )

    def get_input_values(self) -> dict:
        self._check_section_name()
        self._input_values[NAME] = self.entry_name.get()
        self._input_values[RELATIVE_OFFSET_COORDINATES][
            EventType.SECTION_ENTER.serialize()
        ] = self.frame_bbox_offset.get_relative_offset_coordintes()
        return self._input_values

    def _check_section_name(self) -> None:
        new_entry_name = self.entry_name.get()
        if new_entry_name == self._input_values[NAME]:
            return
        if not self._viewmodel.is_section_name_valid(new_entry_name):
            raise NoUniqueNameException(
                f"Please choose a unique name, {new_entry_name} is already used!"
            )


class ToplevelSections(ToplevelTemplate):
    def __init__(
        self,
        viewmodel: ViewModel,
        section_offset: RelativeOffsetCoordinate,
        input_values: dict | None = None,
        show_offset: bool = True,
        **kwargs: Any,
    ) -> None:
        self._viewmodel = viewmodel
        self._section_offset = section_offset
        self._input_values = input_values
        self._show_offset = show_offset
        super().__init__(**kwargs)

    def _create_frame_content(self, master: Any) -> FrameContent:
        return FrameConfigureSection(
            master=master,
            section_offset=self._section_offset,
            viewmodel=self._viewmodel,
            input_values=self._input_values,
            show_offset=self._show_offset,
        )

    def _on_ok(self, event: Any = None) -> None:
        self._input_values = self._frame_content.get_input_values()
        self._close()

    def get_metadata(self) -> dict:
        self.wait_window()
        if self._canceled:
            raise CancelAddSection()
        if self._input_values is None:
            raise ValueError("input values is None, but should be a dict")
        return self._input_values
