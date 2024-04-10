import contextlib
import tkinter
from datetime import datetime
from typing import Any, Optional

from customtkinter import CTkButton, CTkComboBox, CTkEntry, CTkLabel, ThemeManager

from OTAnalytics.adapter_ui.abstract_frame_project import AbstractFrameProject
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.project import (
    COORDINATE_X,
    COORDINATE_Y,
    COUNTING_LOCATION_NUMBER,
    DIRECTION,
    REMARK,
    TK_NUMBER,
)
from OTAnalytics.plugin_ui.customtkinter_gui.button_quick_save_config import (
    ButtonQuickSaveConfig,
)
from OTAnalytics.plugin_ui.customtkinter_gui.constants import (
    PADX,
    PADY,
    STATE_DISABLED,
    STATE_NORMAL,
    STICKY,
)
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
        self._title: str = "Project"
        self._get_widgets()
        self._place_widgets()
        self.disable_segmented_button()

    def _get_widgets(self) -> None:
        self.add(self._title)
        self.frame_project = FrameProject(
            master=self.tab(self._title), viewmodel=self._viewmodel
        )

    def _place_widgets(self) -> None:
        self.frame_project.pack(fill=tkinter.BOTH, expand=True)
        self.set(self._title)


class FrameProject(AbstractFrameProject, EmbeddedCTkFrame):
    def __init__(self, viewmodel: ViewModel, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._viewmodel = viewmodel
        self._project_name = tkinter.StringVar()
        self._get_widgets()
        self._place_widgets()
        self.introduce_to_viewmodel()
        self._wire_callbacks()

    def introduce_to_viewmodel(self) -> None:
        self._viewmodel.set_frame_project(self)
        self._viewmodel.set_button_quick_save_config(self.button_quick_save)

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
        self._button_frame = EmbeddedCTkFrame(master=self)
        self._button_new = CTkButton(
            master=self._button_frame,
            text="New",
            width=10,
            command=self._viewmodel.start_new_project,
        )
        self.button_open = CTkButton(
            master=self._button_frame,
            text="Open...",
            width=10,
            command=self._viewmodel.load_configuration,
        )
        self.button_save_as = CTkButton(
            master=self._button_frame,
            text="Save as...",
            width=10,
            command=self._viewmodel.save_configuration,
        )
        self.button_quick_save = ButtonQuickSaveConfig(
            master=self._button_frame,
            text="Save",
            width=10,
            command=self._viewmodel.quick_save_configuration,
        )
        self._svz_metadata = TabviewSvzMetadata(master=self, viewmodel=self._viewmodel)

    def _place_widgets(self) -> None:
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self._button_frame.grid(
            row=0, column=0, columnspan=2, padx=0, pady=0, sticky=STICKY
        )
        for column, button in enumerate(
            [
                self._button_new,
                self.button_open,
                self.button_save_as,
                self.button_quick_save,
            ]
        ):
            self._button_frame.grid_columnconfigure(column, weight=1)
            button.grid(row=0, column=column, padx=PADX, pady=PADY, sticky=STICKY)
        self._label_name.grid(row=1, column=0, padx=PADX, pady=PADY, sticky=STICKY)
        self._entry_name.grid(row=1, column=1, padx=PADX, pady=PADY, sticky=STICKY)
        self._start_date_row.grid(row=2, column=0, columnspan=2, sticky=STICKY_WEST)
        self._svz_metadata.grid(
            row=3, column=0, columnspan=2, padx=0, pady=0, sticky=STICKY
        )

    def _wire_callbacks(self) -> None:
        self._project_name.trace_add("write", callback=self._update_project_name)
        self._start_date_row.trace_add(callback=self._update_project_start_date)

    def _update_project_name(self, name: str, other: str, mode: str) -> None:
        self._viewmodel.update_project_name(self._project_name.get())

    def _update_project_start_date(self, name: str, other: str, mode: str) -> None:
        with contextlib.suppress(InvalidDatetimeFormatError):
            self._viewmodel.update_project_start_date(
                self._start_date_row.get_datetime(),
            )

    def update(self, name: str, start_date: Optional[datetime]) -> None:
        self._project_name.set(name)
        self._start_date_row.set_datetime(start_date)

    def set_enabled_general_buttons(self, enabled: bool) -> None:
        new_state = STATE_NORMAL if enabled else STATE_DISABLED
        for button in [
            self._button_new,
            self.button_save_as,
            self.button_open,
            self.button_quick_save,
        ]:
            button.configure(state=new_state)


class TabviewSvzMetadata(CustomCTkTabview):
    def __init__(
        self,
        viewmodel: ViewModel,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._viewmodel = viewmodel
        self._title: str = "SVZ Metadaten"
        self._get_widgets()
        self._place_widgets()
        self.disable_segmented_button()

    def _get_widgets(self) -> None:
        self.add(self._title)
        self.frame_project = FrameSvzMetadata(
            master=self.tab(self._title), viewmodel=self._viewmodel
        )

    def _place_widgets(self) -> None:
        self.frame_project.pack(fill=tkinter.BOTH, expand=True)
        self.set(self._title)


class FrameSvzMetadata(EmbeddedCTkFrame):

    def __init__(self, viewmodel: ViewModel, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._viewmodel = viewmodel
        self._directions = self._viewmodel.get_directions_of_stationing()
        self._tk_number = tkinter.StringVar()
        self._counting_location_number = tkinter.StringVar()
        self._coordinate_x = tkinter.StringVar()
        self._coordinate_y = tkinter.StringVar()
        self._direction = tkinter.StringVar()
        self._remark = tkinter.StringVar()
        self._get_widgets()
        self._place_widgets()
        self.introduce_to_viewmodel()
        self._wire_callbacks()

    def _get_widgets(self) -> None:
        self._label_tk_number = CTkLabel(master=self, text="TK-Nummer")
        self._entry_tk_number = CTkEntry(
            master=self,
            textvariable=self._tk_number,
            placeholder_text="TK-Nummer",
        )
        self._label_counting_location_number = CTkLabel(
            master=self, text="Zählstellennummer"
        )
        self._entry_counting_location_number = CTkEntry(
            master=self,
            textvariable=self._counting_location_number,
            placeholder_text="Zählstellennummer",
        )
        self._label_coordinate = CTkLabel(master=self, text="Geokoordinate")
        self._label_coordinate_x = CTkLabel(master=self, text="X")
        self._entry_coordinate_x = CTkEntry(
            master=self,
            textvariable=self._coordinate_x,
            placeholder_text="X Koordinate",
        )
        self._label_coordinate_y = CTkLabel(master=self, text="Y")
        self._entry_coordinate_y = CTkEntry(
            master=self,
            textvariable=self._coordinate_y,
            placeholder_text="Y Koordinate",
        )
        self._label_direction = CTkLabel(master=self, text="Ausrichtung")
        self._entry_direction = CTkComboBox(
            master=self,
            variable=self._direction,
            values=self._directions.names,
        )
        self._label_remark = CTkLabel(master=self, text="Bemerkung")
        self._entry_remark = CTkEntry(
            master=self,
            textvariable=self._remark,
            placeholder_text="Bemerkung",
        )

    def introduce_to_viewmodel(self) -> None:
        pass

    def _place_widgets(self) -> None:
        self.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self._label_tk_number.grid(
            row=0, column=0, columnspan=1, padx=PADX, pady=PADY, sticky=STICKY_WEST
        )
        self._entry_tk_number.grid(
            row=0, column=1, columnspan=1, padx=PADX, pady=PADY, sticky=STICKY
        )
        self._label_counting_location_number.grid(
            row=1, column=0, columnspan=1, padx=PADX, pady=PADY, sticky=STICKY_WEST
        )
        self._entry_counting_location_number.grid(
            row=1, column=1, columnspan=1, padx=PADX, pady=PADY, sticky=STICKY
        )
        self._label_direction.grid(
            row=2, column=0, columnspan=1, padx=PADX, pady=PADY, sticky=STICKY_WEST
        )
        self._entry_direction.grid(
            row=2, column=1, columnspan=1, padx=PADX, pady=PADY, sticky=STICKY
        )
        self._label_remark.grid(
            row=3, column=0, columnspan=1, padx=PADX, pady=PADY, sticky=STICKY_WEST
        )
        self._entry_remark.grid(
            row=3, column=1, columnspan=1, padx=PADX, pady=PADY, sticky=STICKY
        )
        self._label_coordinate.grid(
            row=4, column=0, columnspan=2, padx=PADX, pady=PADY, sticky=STICKY
        )
        self._label_coordinate_x.grid(
            row=5, column=0, columnspan=1, padx=PADX, pady=PADY, sticky=STICKY
        )
        self._entry_coordinate_x.grid(
            row=5, column=1, columnspan=1, padx=PADX, pady=PADY, sticky=STICKY
        )
        self._label_coordinate_y.grid(
            row=6, column=0, columnspan=1, padx=PADX, pady=PADY, sticky=STICKY
        )
        self._entry_coordinate_y.grid(
            row=6, column=1, columnspan=1, padx=PADX, pady=PADY, sticky=STICKY
        )

    def _wire_callbacks(self) -> None:
        self._tk_number.trace_add("write", callback=self._update_metadata)
        self._counting_location_number.trace_add(
            "write", callback=self._update_metadata
        )
        self._direction.trace_add("write", callback=self._update_metadata)
        self._remark.trace_add("write", callback=self._update_metadata)
        self._coordinate_x.trace_add("write", callback=self._update_metadata)
        self._coordinate_y.trace_add("write", callback=self._update_metadata)

    def _update_metadata(self, name: str, other: str, mode: str) -> None:
        self._viewmodel.update_svz_metadata(self.__build_metadata())

    def __build_metadata(self) -> dict:
        return {
            TK_NUMBER: self._tk_number.get(),
            COUNTING_LOCATION_NUMBER: self._counting_location_number.get(),
            DIRECTION: self._directions.get_id_for(self._direction.get()),
            REMARK: self._remark.get(),
            COORDINATE_X: self._coordinate_x.get(),
            COORDINATE_Y: self._coordinate_y.get(),
        }


def get_default_toplevel_fg_color() -> str:
    return ThemeManager.theme["CTkToplevel"]["fg_color"]
