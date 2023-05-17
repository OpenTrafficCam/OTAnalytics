from abc import ABC, abstractmethod
from datetime import datetime
from tkinter import END, IntVar
from typing import Any, Optional

from customtkinter import (
    CTkButton,
    CTkCheckBox,
    CTkEntry,
    CTkFrame,
    CTkLabel,
    CTkToplevel,
    ThemeManager,
)

from OTAnalytics.adapter_ui.abstract_frame_filter import AbstractFrameFilter
from OTAnalytics.adapter_ui.default_values import (
    DATE_FORMAT,
    DATE_FORMAT_PLACEHOLDER,
    DATETIME_FORMAT,
)
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.domain.date import DateRange
from OTAnalytics.plugin_ui.customtkinter_gui.constants import (
    PADX,
    PADY,
    STICKY,
    tk_events,
)
from OTAnalytics.plugin_ui.customtkinter_gui.messagebox import InfoBox
from OTAnalytics.plugin_ui.customtkinter_gui.style import (
    ANCHOR_WEST,
    COLOR_GRAY,
    COLOR_GREEN,
    COLOR_ORANGE,
    COLOR_RED,
    STICKY_WEST,
)

HOUR = "Hour"
MINUTE = "Minute"
SECOND = "Second"
ON_VALUE = 1
OFF_VALUE = 0

STATE_DISABLED = "disabled"
STATE_NORMAL = "normal"


class InvalidDatetimeFormatError(Exception):
    pass


class FrameFilter(AbstractFrameFilter, CTkFrame):
    def __init__(self, viewmodel: ViewModel, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._viewmodel = viewmodel
        self._get_widgets()
        self._place_widgets()
        self._introduce_to_viewmodel()

    def _get_widgets(self) -> None:
        self.label = CTkLabel(master=self, text="Visualization Filters")
        self.filter_by_date_button = FilterTracksByDateFilterButton(
            master=self,
            name="Filter By Date",
            button_width=60,
            button_default_state=STATE_DISABLED,
            button_default_color=COLOR_GRAY,
            viewmodel=self._viewmodel,
        )

    def _place_widgets(self) -> None:
        self.label.grid(row=0, column=0, padx=PADX, pady=PADY, sticky=STICKY_WEST)
        self.filter_by_date_button.grid(
            row=1, column=0, padx=PADX, pady=PADY, sticky=STICKY
        )

    def _introduce_to_viewmodel(self) -> None:
        self._viewmodel.set_filter_frame(self)

    def set_active_color_on_filter_by_date_button(self) -> None:
        self.filter_by_date_button.set_color(COLOR_ORANGE)

    def set_inactive_color_on_filter_by_date_button(self) -> None:
        self.filter_by_date_button.reset_color()

    def enable_filter_by_date_button(self) -> None:
        self.filter_by_date_button.enable_button()

    def disable_filter_by_date_button(self) -> None:
        self.filter_by_date_button.disable_button()


class FilterButton(ABC, CTkFrame):
    def __init__(
        self,
        name: str,
        button_width: int,
        button_default_state: str,
        button_default_color: str,
        viewmodel: ViewModel,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._viewmodel = viewmodel
        self._name = name
        self._button_width = button_width
        self._button_default_state = button_default_state
        self._button_default_color = button_default_color
        self._check_var = IntVar(value=0)

        self._get_widgets()
        self._place_widgets()

    def _get_widgets(self) -> None:
        self.checkbox = CTkCheckBox(
            master=self,
            text="",
            variable=self._check_var,
            command=self.on_checkbox_clicked,
            onvalue=ON_VALUE,
            offvalue=OFF_VALUE,
            width=5,
        )
        self.button = CTkButton(
            master=self,
            text=self._name,
            command=self._show_popup,
            width=self._button_width,
            state=self._button_default_state,
            fg_color=self._button_default_color,
        )

    def _place_widgets(self) -> None:
        self.checkbox.grid(row=0, column=0, sticky=STICKY_WEST)
        self.button.grid(row=0, column=1, sticky=STICKY_WEST)

    @abstractmethod
    def _show_popup(self) -> None:
        pass

    @abstractmethod
    def _enable_filter(self) -> None:
        pass

    @abstractmethod
    def _disable_filter(self) -> None:
        pass

    def on_checkbox_clicked(self) -> None:
        if self._check_var.get() == ON_VALUE:
            self._enable_filter()
        else:
            self._disable_filter()

    def set_color(self, color: str) -> None:
        self.button.configure(fg_color=color)

    def reset_color(self) -> None:
        self.button.configure(fg_color=ThemeManager.theme["CTkButton"]["fg_color"])


class FilterTracksByDateFilterButton(FilterButton):
    def __init__(
        self,
        name: str,
        button_width: int,
        button_default_state: str,
        button_default_color: str,
        viewmodel: ViewModel,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            name,
            button_width,
            button_default_state,
            button_default_color,
            viewmodel,
            **kwargs,
        )

    def _show_popup(self) -> None:
        current_date_range = self._viewmodel.get_filter_tracks_by_date_setting()

        FilterTracksByDatePopup(
            viewmodel=self._viewmodel,
            title="Filter tracks by date",
            default_start_date=current_date_range.start_date,
            default_end_date=current_date_range.end_date,
        )

    def _enable_filter(self) -> None:
        self._viewmodel.enable_filter_track_by_date()

    def _disable_filter(self) -> None:
        self._viewmodel.disable_filter_track_by_date()

    def enable_button(self) -> None:
        self.button.configure(state=STATE_NORMAL)

    def disable_button(self) -> None:
        self.button.configure(state=STATE_DISABLED, fg_color=COLOR_GRAY)


class FilterTracksByDatePopup(CTkToplevel):
    def __init__(
        self,
        viewmodel: ViewModel,
        title: str,
        default_start_date: Optional[datetime],
        default_end_date: Optional[datetime],
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._viewmodel = viewmodel

        self.title(title)
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self._get_widgets()
        self._place_widgets()
        self._bind_events()

        self._set_default_date_range(default_start_date, default_end_date)

    def _get_widgets(self) -> None:
        self.label = CTkLabel(master=self, text="Choose date range")

        self.from_date_row = DateRow(
            master=self,
            viewmodel=self._viewmodel,
            name="From",
            fg_color=get_default_toplevel_fg_color(),
        )
        self.to_date_row = DateRow(
            master=self,
            viewmodel=self._viewmodel,
            name="To",
            fg_color=get_default_toplevel_fg_color(),
        )
        self._get_detection_info_label()
        self._button_frame = CTkFrame(
            master=self, fg_color=get_default_toplevel_fg_color()
        )
        self.apply_button = CTkButton(
            master=self._button_frame,
            text="Apply",
            command=self._on_apply_button_clicked,
            width=60,
        )
        self.reset_button = CTkButton(
            master=self._button_frame,
            text="Reset",
            command=self._on_reset_button_clicked,
            width=60,
        )

    def _get_detection_info_label(self) -> None:
        first_occurrence_info_text = "First detection occurrence: "
        last_occurrence_info_text = "Last detection occurrence: "
        if first_occurrence := self._viewmodel.get_first_detection_occurrence():
            first_occurrence_info_text += first_occurrence.strftime(DATETIME_FORMAT)

        if last_occurrence := self._viewmodel.get_last_detection_occurrence():
            last_occurrence_info_text += last_occurrence.strftime(DATETIME_FORMAT)

        self.first_occurrence_info_label = CTkLabel(
            master=self, text=first_occurrence_info_text, padx=PADX, pady=PADY
        )
        self.last_occurrence_info_label = CTkLabel(
            master=self, text=last_occurrence_info_text, padx=PADX, pady=PADY
        )

    def _place_widgets(self) -> None:
        self.label.grid(row=0, column=0, padx=PADX, pady=PADY, sticky=STICKY_WEST)

        self.from_date_row.grid(row=1, sticky=STICKY_WEST)
        self.to_date_row.grid(row=2, sticky=STICKY_WEST)
        self.first_occurrence_info_label.grid(row=3, sticky=STICKY_WEST)
        self.last_occurrence_info_label.grid(row=4, sticky=STICKY_WEST)

        self._button_frame.grid(
            row=5, column=0, padx=PADX, pady=PADY, sticky=STICKY_WEST
        )

        self.apply_button.grid(row=0, column=0, sticky=STICKY_WEST)
        self.reset_button.grid(row=0, column=1, padx=(PADX, 0), sticky=STICKY_WEST)

    def _bind_events(self) -> None:
        self.bind(tk_events.ESCAPE_KEY, self._close)

    def _close(self, _: Any = None) -> None:
        self.destroy()
        self.update()

    def get_start_date(self) -> Optional[datetime]:
        return self.from_date_row.get_datetime()

    def get_end_date(self) -> Optional[datetime]:
        return self.to_date_row.get_datetime()

    def _set_default_date_range(
        self, start_date: Optional[datetime], end_date: Optional[datetime]
    ) -> None:
        self._set_current_start_date(start_date)
        self._set_current_end_date(end_date)

    def _set_current_start_date(self, start_date: Optional[datetime]) -> None:
        if start_date:
            self.from_date_row.set_datetime(start_date)
        else:
            first_detection_occurrence = (
                self._viewmodel.get_first_detection_occurrence()
            )
            self.from_date_row.set_datetime(first_detection_occurrence)

    def _set_current_end_date(self, end_date: Optional[datetime]) -> None:
        if end_date:
            self.to_date_row.set_datetime(end_date)
        else:
            last_detection_occurrence = self._viewmodel.get_last_detection_occurrence()
            self.to_date_row.set_datetime(last_detection_occurrence)

    def _get_position(self) -> tuple[int, int]:
        return self.winfo_rootx(), self.winfo_rooty()

    def _on_apply_button_clicked(self) -> None:
        try:
            date_range = DateRange(self.get_start_date(), self.get_end_date())

            self._viewmodel.apply_filter_tracks_by_date(date_range)
            print("Filter tracks by date applied.")
            self._close()
        except InvalidDatetimeFormatError as e:
            InfoBox(message=str(e), initial_position=self._get_position())

    def _on_reset_button_clicked(self) -> None:
        self._viewmodel.reset_filter_tracks_by_date()
        self._close()


class DateRow(CTkFrame):
    def __init__(self, viewmodel: ViewModel, name: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._name = name
        self._viewmodel = viewmodel

        self._get_widgets()
        self._place_widgets()
        self._reset_all_border_colors()
        self._clear_validation_info()

    @property
    def date(self) -> str:
        return self.date_entry.get()

    @property
    def hour(self) -> str:
        return self.hour_entry.get()

    @property
    def minute(self) -> str:
        return self.minute_entry.get()

    @property
    def second(self) -> str:
        return self.second_entry.get()

    def set_datetime(self, date_time: Optional[datetime]) -> None:
        if date_time:
            self._display_text_on_entry_widget(self.date_entry, f"{date_time.date()}")
            self._display_text_on_entry_widget(self.hour_entry, f"{date_time.hour}")
            self._display_text_on_entry_widget(self.minute_entry, f"{date_time.minute}")
            self._display_text_on_entry_widget(self.second_entry, f"{date_time.second}")

    def get_datetime(self) -> Optional[datetime]:
        try:
            date = datetime.strptime(self.date, DATE_FORMAT)
            return datetime(
                year=date.year,
                month=date.month,
                day=date.day,
                hour=int(self.hour),
                minute=int(self.minute),
                second=int(self.second),
            )
        except ValueError:
            raise InvalidDatetimeFormatError(f"{self._name} datetime is not valid.")

    def _get_widgets(self) -> None:
        self.validation_info_label = CTkLabel(
            master=self, text="", width=400, anchor=ANCHOR_WEST
        )
        self.name_label = CTkLabel(
            master=self, text=self._name, anchor=ANCHOR_WEST, width=40
        )
        self.date_entry = CTkEntry(
            master=self,
            placeholder_text=DATE_FORMAT_PLACEHOLDER,
            width=95,
            validate="key",
            validatecommand=(self.register(self._validate_date_format), "%P", "%W"),
        )
        self.hour_entry = CTkEntry(
            master=self,
            placeholder_text="HH",
            width=35,
            validate="key",
            validatecommand=(
                self.register(self._validate_time_format),
                HOUR,
                "%P",
                "%W",
            ),
        )
        self.minute_entry = CTkEntry(
            master=self,
            placeholder_text="MM",
            width=35,
            validate="key",
            validatecommand=(
                self.register(self._validate_time_format),
                MINUTE,
                "%P",
                "%W",
            ),
        )
        self.second_entry = CTkEntry(
            master=self,
            placeholder_text="SS",
            width=35,
            validate="key",
            validatecommand=(
                self.register(self._validate_time_format),
                SECOND,
                "%P",
                "%W",
            ),
        )

    def _place_widgets(self) -> None:
        self.name_label.grid(row=0, column=0, padx=PADX, pady=PADY, sticky=STICKY_WEST)
        self.date_entry.grid(row=0, column=1, padx=PADX, pady=PADY, stick=STICKY)
        self.hour_entry.grid(row=0, column=2, padx=PADX, pady=PADY, stick=STICKY)
        ColonLabel(master=self).grid(row=0, column=3)
        self.minute_entry.grid(row=0, column=4, padx=PADX, pady=PADY, stick=STICKY)
        ColonLabel(master=self).grid(row=0, column=5)
        self.second_entry.grid(row=0, column=6, padx=PADX, pady=PADY, stick=STICKY)
        self.validation_info_label.grid(
            row=0, column=7, padx=PADX, pady=PADY, sticky=STICKY
        )

    def _display_text_on_entry_widget(self, widget: CTkEntry, text: str) -> None:
        widget.delete(0, END)
        widget.insert(0, text)

    def _validate_date_format(self, value: str, widget_name: str) -> bool:
        widget: CTkEntry = self.nametowidget(widget_name).master
        if self._viewmodel.validate_date(value):
            widget.configure(border_color=COLOR_GREEN)
            self._clear_validation_info()
        else:
            widget.configure(border_color=COLOR_RED)
            self._display_invalid_validation_info(
                f"Date must be of format: '{DATE_FORMAT_PLACEHOLDER}'"
            )
        return True

    def _validate_time_format(self, name: str, value: str, widget_name: str) -> bool:
        widget: CTkEntry = self.nametowidget(widget_name).master

        if self._has_valid_time_format(name, value):
            widget.configure(border_color=COLOR_GREEN)
            self._clear_validation_info()
        else:
            self._display_invalid_validation_info(self._build_error_message_for(name))
            widget.configure(border_color=COLOR_RED)
        return True

    def _has_valid_time_format(self, name: str, value: str) -> bool:
        if name == HOUR:
            return self._viewmodel.validate_hour(value)

        if name == MINUTE:
            return self._viewmodel.validate_minute(value)

        if name == SECOND:
            return self._viewmodel.validate_second(value)

        raise ValueError(f"Key does not exist. Must be {HOUR}, {MINUTE} or {SECOND}.")

    def _clear_validation_info(self) -> None:
        self.validation_info_label.configure(text="")

    def _display_invalid_validation_info(self, msg: str) -> None:
        self.validation_info_label.configure(text=msg, text_color=COLOR_RED)

    def _build_error_message_for(self, name: str) -> str:
        if name == HOUR:
            return self._build_time_error_message(name, 0, 23)
        if name in [MINUTE, SECOND]:
            return self._build_time_error_message(name, 0, 59)
        raise ValueError(f"Key does not exist. Must be {HOUR}, {MINUTE} or {SECOND}")

    def _build_time_error_message(
        self, name: str, start_range: int, end_range: int
    ) -> str:
        return f"{name} must be a digit in range [{start_range},{end_range}]"

    def _reset_all_border_colors(self) -> None:
        default_border_color = ThemeManager.theme["CTkEntry"]["border_color"]

        self.date_entry.configure(border_color=default_border_color)
        self.hour_entry.configure(border_color=default_border_color)
        self.minute_entry.configure(border_color=default_border_color)
        self.second_entry.configure(border_color=default_border_color)

    def _get_entry_widget_by_name(self, name: str) -> CTkEntry:
        return self.nametowidget(name).master


class ColonLabel(CTkLabel):
    def __init__(self, **kwargs: Any):
        super().__init__(text=":", **kwargs)


def get_default_toplevel_fg_color() -> str:
    return ThemeManager.theme["CTkToplevel"]["fg_color"]
