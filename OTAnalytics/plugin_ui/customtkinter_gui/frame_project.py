import asyncio
import contextlib
import tkinter
from datetime import datetime
from typing import Any, Optional

from customtkinter import (
    CTkButton,
    CTkCheckBox,
    CTkEntry,
    CTkLabel,
    CTkOptionMenu,
    ThemeManager,
)

from OTAnalytics.adapter_ui.abstract_frame_project import (
    AbstractFrameProject,
    AbstractFrameSvzMetadata,
)
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.project import (
    COORDINATE_X,
    COORDINATE_Y,
    COUNTING_DAY,
    COUNTING_LOCATION_NUMBER,
    DIRECTION,
    DIRECTION_DESCRIPTION,
    HAS_BICYCLE_LANE,
    IS_BICYCLE_COUNTING,
    REMARK,
    TK_NUMBER,
    WEATHER,
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
        self._project_title = "Project"
        self._svz_title = "SVZ"
        self._get_widgets()
        self._place_widgets()

    def _get_widgets(self) -> None:
        self.add(self._project_title)
        self.frame_project = FrameProject(
            master=self.tab(self._project_title), viewmodel=self._viewmodel
        )
        self.add(self._svz_title)
        self.frame_svz_metadata = FrameSvzMetadata(
            master=self.tab(self._svz_title), viewmodel=self._viewmodel
        )
        if not self._viewmodel.show_svz():
            self.delete(self._svz_title)

    def _place_widgets(self) -> None:
        self.frame_project.pack(fill=tkinter.BOTH, expand=True)
        self.frame_svz_metadata.pack(fill=tkinter.BOTH, expand=True)


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
        # self._button_new = CTkButton(
        #     master=self._button_frame,
        #     text="New",
        #     width=10,
        #     command=self._viewmodel.start_new_project,
        # )
        self.button_open = CTkButton(
            master=self._button_frame,
            text="Open...",
            width=10,
            command=self._do_open,
        )
        self.button_save_as = CTkButton(
            master=self._button_frame,
            text="Save as...",
            width=10,
            command=self._do_save_as,
        )
        self.button_quick_save = ButtonQuickSaveConfig(
            master=self._button_frame,
            text="Save",
            width=10,
            command=self._do_quick_save,
        )

    def _do_quick_save(self) -> None:
        asyncio.run(self._viewmodel.quick_save_configuration())

    def _do_save_as(self) -> None:
        asyncio.run(self._viewmodel.save_configuration())

    def _do_open(self) -> None:
        asyncio.run(self._viewmodel.load_configuration())

    def _place_widgets(self) -> None:
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self._button_frame.grid(
            row=0, column=0, columnspan=2, padx=0, pady=0, sticky=STICKY
        )
        for column, button in enumerate(
            [
                # self._button_new,
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
            # self._button_new,
            self.button_save_as,
            self.button_open,
            self.button_quick_save,
        ]:
            button.configure(state=new_state)


class FrameSvzMetadata(AbstractFrameSvzMetadata, EmbeddedCTkFrame):

    def __init__(self, viewmodel: ViewModel, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._viewmodel = viewmodel
        self._padding_multiplier = 4
        self._directions = self._viewmodel.get_directions_of_stationing()
        self._counting_day_types = self._viewmodel.get_counting_day_types()
        self._weather_types = self._viewmodel.get_weather_types()
        self._tk_number = tkinter.StringVar()
        self._counting_location_number = tkinter.StringVar()
        self._direction = tkinter.StringVar()
        self._direction_description = tkinter.StringVar()
        self._has_bicycle_lane = tkinter.BooleanVar()
        self._is_bicycle_counting = tkinter.BooleanVar()
        self._counting_day_type = tkinter.StringVar()
        self._weather = tkinter.StringVar()
        self._remark = tkinter.StringVar()
        self._coordinate_x = tkinter.StringVar()
        self._coordinate_y = tkinter.StringVar()
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
        self._label_direction = CTkLabel(master=self, text="Ausrichtung")
        self._entry_direction = CTkOptionMenu(
            master=self,
            variable=self._direction,
            values=self._directions.names,
        )
        self._label_direction_description = CTkLabel(
            master=self,
            text="Zählrichtung\n (Name aus ZV)",
            compound="left",
            justify="left",
            anchor="w",
        )
        self._entry_direction_description = CTkEntry(
            master=self,
            textvariable=self._direction_description,
            placeholder_text="Ausrichtung Beschreibung",
        )
        self._checkbox_has_bicycle_lane = CTkCheckBox(
            master=self,
            text="Seitlicher Radweg vorhanden",
            variable=self._has_bicycle_lane,
        )
        self._checkbox_is_bicycle_counting = CTkCheckBox(
            master=self,
            text="Fahrradzählung",
            variable=self._is_bicycle_counting,
        )
        self._label_counting_day_type = CTkLabel(master=self, text="Kategorie Zähltag")
        self._entry_counting_day_type = CTkOptionMenu(
            master=self,
            variable=self._counting_day_type,
            values=self._counting_day_types.names,
        )
        self._label_weather = CTkLabel(master=self, text="Wetter")
        self._entry_weather = CTkOptionMenu(
            master=self,
            variable=self._weather,
            values=self._weather_types.names,
        )
        self._label_remark = CTkLabel(master=self, text="Bemerkung")
        self._entry_remark = CTkEntry(
            master=self,
            textvariable=self._remark,
            placeholder_text="Bemerkung",
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

    def introduce_to_viewmodel(self) -> None:
        self._viewmodel.set_svz_metadata_frame(self)

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
        self._label_direction_description.grid(
            row=3,
            column=0,
            columnspan=1,
            padx=PADX,
            pady=(PADY, PADY * self._padding_multiplier),
            sticky=STICKY,
        )
        self._entry_direction_description.grid(
            row=3,
            column=1,
            columnspan=1,
            padx=PADX,
            pady=(PADY, PADY * self._padding_multiplier),
            sticky=STICKY,
        )
        self._checkbox_has_bicycle_lane.grid(
            row=4, column=0, columnspan=2, padx=PADX, pady=PADY, sticky=STICKY_WEST
        )
        self._checkbox_is_bicycle_counting.grid(
            row=5,
            column=0,
            columnspan=2,
            padx=PADX,
            pady=(PADY, PADY * self._padding_multiplier),
            sticky=STICKY_WEST,
        )
        self._label_counting_day_type.grid(
            row=6, column=0, columnspan=1, padx=PADX, pady=PADY, sticky=STICKY_WEST
        )
        self._entry_counting_day_type.grid(
            row=6, column=1, columnspan=1, padx=PADX, pady=PADY, sticky=STICKY
        )
        self._label_weather.grid(
            row=7, column=0, columnspan=1, padx=PADX, pady=PADY, sticky=STICKY_WEST
        )
        self._entry_weather.grid(
            row=7, column=1, columnspan=1, padx=PADX, pady=PADY, sticky=STICKY
        )
        self._label_remark.grid(
            row=8, column=0, columnspan=1, padx=PADX, pady=PADY, sticky=STICKY_WEST
        )
        self._entry_remark.grid(
            row=8, column=1, columnspan=1, padx=PADX, pady=PADY, sticky=STICKY
        )
        self._label_coordinate.grid(
            row=9, column=0, columnspan=2, padx=PADX, pady=PADY, sticky=STICKY
        )
        self._label_coordinate_x.grid(
            row=10, column=0, columnspan=1, padx=PADX, pady=PADY, sticky=STICKY
        )
        self._entry_coordinate_x.grid(
            row=10, column=1, columnspan=1, padx=PADX, pady=PADY, sticky=STICKY
        )
        self._label_coordinate_y.grid(
            row=11, column=0, columnspan=1, padx=PADX, pady=PADY, sticky=STICKY
        )
        self._entry_coordinate_y.grid(
            row=11, column=1, columnspan=1, padx=PADX, pady=PADY, sticky=STICKY
        )

    def _wire_callbacks(self) -> None:
        self._tk_number.trace_add("write", callback=self._update_metadata)
        self._counting_location_number.trace_add(
            "write", callback=self._update_metadata
        )
        self._direction.trace_add("write", callback=self._update_metadata)
        self._direction_description.trace_add("write", callback=self._update_metadata)
        self._has_bicycle_lane.trace_add("write", callback=self._update_metadata)
        self._is_bicycle_counting.trace_add("write", callback=self._update_metadata)
        self._counting_day_type.trace_add("write", callback=self._update_metadata)
        self._weather.trace_add("write", callback=self._update_metadata)
        self._remark.trace_add("write", callback=self._update_metadata)
        self._coordinate_x.trace_add("write", callback=self._update_metadata)
        self._coordinate_y.trace_add("write", callback=self._update_metadata)

        self._activate_update()

    def _activate_update(self) -> None:
        self._update = True

    def _deactivate_update(self) -> None:
        self._update = False

    def _update_metadata(self, name: str, other: str, mode: str) -> None:
        if self._update:
            self._viewmodel.update_svz_metadata(self.__build_metadata())

    def __build_metadata(self) -> dict:
        return {
            TK_NUMBER: self._tk_number.get(),
            COUNTING_LOCATION_NUMBER: self._counting_location_number.get(),
            DIRECTION: self._directions.get_id_for(self._direction.get()),
            DIRECTION_DESCRIPTION: self._direction_description.get(),
            HAS_BICYCLE_LANE: self._has_bicycle_lane.get(),
            IS_BICYCLE_COUNTING: self._is_bicycle_counting.get(),
            COUNTING_DAY: self._counting_day_types.get_id_for(
                self._counting_day_type.get()
            ),
            WEATHER: self._weather_types.get_id_for(self._weather.get()),
            REMARK: self._remark.get(),
            COORDINATE_X: self._coordinate_x.get(),
            COORDINATE_Y: self._coordinate_y.get(),
        }

    def update(self, metadata: dict) -> None:
        self._deactivate_update()
        if metadata:
            self._tk_number.set(self.__get_display_value(TK_NUMBER, metadata))
            self._counting_location_number.set(
                self.__get_display_value(COUNTING_LOCATION_NUMBER, metadata)
            )
            self._direction.set(
                self._directions.get_name_for(
                    self.__get_display_value(DIRECTION, metadata)
                )
            )
            self._direction_description.set(
                self.__get_display_value(DIRECTION_DESCRIPTION, metadata)
            )
            self._has_bicycle_lane.set(metadata[HAS_BICYCLE_LANE])
            self._is_bicycle_counting.set(metadata[IS_BICYCLE_COUNTING])
            self._counting_day_type.set(
                self._counting_day_types.get_name_for(
                    self.__get_display_value(COUNTING_DAY, metadata)
                )
            )
            self._weather.set(
                self._weather_types.get_name_for(
                    self.__get_display_value(WEATHER, metadata)
                )
            )
            self._remark.set(self.__get_display_value(REMARK, metadata))
            self._coordinate_x.set(self.__get_display_value(COORDINATE_X, metadata))
            self._coordinate_y.set(self.__get_display_value(COORDINATE_Y, metadata))
        else:
            self._tk_number.set("")
            self._counting_location_number.set("")
            self._direction.set("")
            self._direction_description.set("")
            self._has_bicycle_lane.set(False)
            self._is_bicycle_counting.set(False)
            self._counting_day_type.set("")
            self._weather.set("")
            self._remark.set("")
            self._coordinate_x.set("")
            self._coordinate_y.set("")
        self._activate_update()

    @staticmethod
    def __get_display_value(field: str, metadata: dict) -> str:
        return metadata[field] if metadata[field] else ""


def get_default_toplevel_fg_color() -> str:
    return ThemeManager.theme["CTkToplevel"]["fg_color"]
