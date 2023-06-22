from typing import Any

from customtkinter import CTkEntry, CTkLabel

from OTAnalytics.adapter_ui.default_values import RELATIVE_SECTION_OFFSET
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.application import CancelAddSection
from OTAnalytics.domain.section import ID, NAME, RELATIVE_OFFSET_COORDINATES
from OTAnalytics.domain.types import EventType
from OTAnalytics.plugin_ui.customtkinter_gui.constants import PADX, PADY, STICKY
from OTAnalytics.plugin_ui.customtkinter_gui.frame_bbox_offset import FrameBboxOffset
from OTAnalytics.plugin_ui.customtkinter_gui.messagebox import InfoBox
from OTAnalytics.plugin_ui.customtkinter_gui.toplevel_template import ToplevelTemplate


class ToplevelSections(ToplevelTemplate):
    def __init__(
        self,
        title: str,
        viewmodel: ViewModel,
        input_values: dict | None = None,
        show_offset: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.title(title)
        self._viewmodel = viewmodel
        # TODO: Get default values elsewhere!
        self.input_values: dict = (
            {
                ID: "",
                NAME: "",
                RELATIVE_OFFSET_COORDINATES: {
                    EventType.SECTION_ENTER.serialize(): {
                        "x": RELATIVE_SECTION_OFFSET.x,
                        "y": RELATIVE_SECTION_OFFSET.y,
                    },
                },
            }
            if input_values is None
            else input_values
        )
        self._show_offset = show_offset
        self._canceled = False
        self._get_widgets()
        self._place_widgets()

    def _get_widgets(self) -> None:
        self.label_name = CTkLabel(master=self, text="Name:")
        self.entry_name = CTkEntry(master=self, width=180)
        self.entry_name.insert(0, self.input_values[NAME])

        self.frame_bbox_offset = FrameBboxOffset(
            master=self,
            frame_heading="Bounding Box offset for enter-events:",
            relative_offset_coordinates=self.input_values[RELATIVE_OFFSET_COORDINATES][
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
        self.frame_ok_cancel.grid(
            row=3, column=0, columnspan=3, padx=PADX, pady=PADY, sticky=STICKY
        )

    def _set_focus(self) -> None:
        self.after(0, lambda: self.lift())
        self.after(0, lambda: self.entry_name.focus_set())

    def _on_ok(self, event: Any = None) -> None:
        if not self._name_is_valid():
            return
        self.input_values[NAME] = self.entry_name.get()
        self.input_values[RELATIVE_OFFSET_COORDINATES][
            EventType.SECTION_ENTER.serialize()
        ] = self.frame_bbox_offset.get_relative_offset_coordintes()
        self.destroy()
        self.update()

    def _on_cancel(self, event: Any = None) -> None:
        self._canceled = True
        self.destroy()
        self.update()

    def _name_is_valid(self) -> bool:
        new_entry_name = self.entry_name.get()
        if new_entry_name == self.input_values[NAME]:
            return True
        if not self._viewmodel.is_section_name_valid(new_entry_name):
            position = (self.winfo_x(), self.winfo_y())
            InfoBox(
                message="To add a section, a unique name is necessary!",
                initial_position=position,
            )
            return False
        return True

    def get_metadata(self) -> dict:
        self.wait_window()
        if self._canceled:
            raise CancelAddSection()
        return self.input_values
