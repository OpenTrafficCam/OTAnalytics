import contextlib
import tkinter
from datetime import datetime
from typing import Any, Optional

from customtkinter import CTkEntry, CTkLabel, ThemeManager

from OTAnalytics.adapter_ui.abstract_frame_project import AbstractFrameProject
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.plugin_ui.customtkinter_gui.constants import PADX, PADY, STICKY
from OTAnalytics.plugin_ui.customtkinter_gui.custom_containers import (
    CustomCTkTabview,
    EmbeddedCTkFrame,
)
from OTAnalytics.plugin_ui.customtkinter_gui.frame_filter import (
    DateRow,
    InvalidDatetimeFormatError,
)
from OTAnalytics.plugin_ui.customtkinter_gui.style import STICKY_WEST


class TabviewProject(CustomCTkTabview):
    def __init__(
        self,
        viewmodel: ViewModel,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._viewmodel = viewmodel
        self.PROJECT: str = "Project"
        self._get_widgets()
        self._place_widgets()
        self.disable_segmented_button()

    def _get_widgets(self) -> None:
        self.add(self.PROJECT)
        self.frame_project = FrameProject(
            master=self.tab(self.PROJECT), viewmodel=self._viewmodel
        )

    def _place_widgets(self) -> None:
        self.frame_project.pack(fill=tkinter.BOTH, expand=True)
        self.set(self.PROJECT)


class FrameProject(AbstractFrameProject, EmbeddedCTkFrame):
    def __init__(self, viewmodel: ViewModel, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._viewmodel = viewmodel
        self._project_name = tkinter.StringVar()
        self._get_widgets()
        self._place_widgets()
        self.introduce_to_viewmodel()
        self._wire_callbacks()

    def introduce_to_viewmodel(self) -> None:
        self._viewmodel.set_frame_project(self)

    def _get_widgets(self) -> None:
        self._label_name = CTkLabel(master=self, text="Name")
        self._entry_name = CTkEntry(
            master=self,
            textvariable=self._project_name,
            placeholder_text="Project name",
        )
        self._start_date_row = DateRow(
            master=self,
            viewmodel=self._viewmodel,
            name="Start date",
            place_validation_below=True,
        )

    def _place_widgets(self) -> None:
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self._label_name.grid(row=0, column=0, padx=PADX, pady=PADY, sticky=STICKY)
        self._entry_name.grid(row=0, column=1, padx=PADX, pady=PADY, sticky=STICKY)
        self._start_date_row.grid(row=1, column=0, columnspan=2, sticky=STICKY_WEST)

    def _wire_callbacks(self) -> None:
        self._project_name.trace_add("write", callback=self._update_project)
        self._start_date_row.trace_add(callback=self._update_project)

    def _update_project(self, name: str, other: str, mode: str) -> None:
        with contextlib.suppress(InvalidDatetimeFormatError):
            self._viewmodel.update_project(
                name=self._project_name.get(),
                start_date=self._start_date_row.get_datetime(),
            )

    def update(self, name: str, start_date: Optional[datetime]) -> None:
        self._project_name.set(name)
        self._start_date_row.set_datetime(start_date)


def get_default_toplevel_fg_color() -> str:
    return ThemeManager.theme["CTkToplevel"]["fg_color"]
