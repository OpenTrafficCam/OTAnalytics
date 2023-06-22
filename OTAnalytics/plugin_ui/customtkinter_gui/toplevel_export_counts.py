from typing import Any

from customtkinter import CTkEntry, CTkFrame, CTkLabel, CTkOptionMenu

from OTAnalytics.plugin_ui.customtkinter_gui.constants import PADX, PADY, STICKY
from OTAnalytics.plugin_ui.customtkinter_gui.toplevel_template import ToplevelTemplate
from OTAnalytics.plugin_ui.customtkinter_gui.utility_widgets import FrameOkCancel

INTERVAL = "interval"
EXPORT_FORMAT = "export_format"


class CancelExportCounts(Exception):
    pass


class FrameConfigureExportCounts(CTkFrame):
    def __init__(
        self,
        export_formats: list[str],
        input_values: dict,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._input_values = input_values
        self._export_formats = export_formats
        self._get_widgets()
        self._place_widgets()

    def _get_widgets(self) -> None:
        self.label_interval = CTkLabel(master=self, text="Interval")
        self.entry_interval = CTkEntry(
            master=self,
            validate="key",
            validatecommand=(self.register(self._is_int_above_zero), "%P"),
        )
        self.entry_interval.insert(0, str(self._input_values["interval"]))
        self.label_interval_unit = CTkLabel(master=self, text="min")
        self.label_format = CTkLabel(master=self, text="Format")
        self.optionmenu_format = CTkOptionMenu(master=self, values=self._export_formats)
        self.optionmenu_format.set(self._input_values[EXPORT_FORMAT])

    def _place_widgets(self) -> None:
        self.label_interval.grid(row=0, column=0, padx=PADX, pady=PADY, sticky=STICKY)
        self.entry_interval.grid(row=0, column=1, padx=PADX, pady=PADY, sticky=STICKY)
        self.label_interval_unit.grid(
            row=0, column=2, padx=PADX, pady=PADY, sticky=STICKY
        )
        self.label_format.grid(row=1, column=0, padx=PADX, pady=PADY, sticky=STICKY)
        self.optionmenu_format.grid(
            row=1, column=1, columnspan=2, padx=PADX, pady=PADY, sticky=STICKY
        )

    def set_focus(self) -> None:
        self.after(0, lambda: self.entry_interval.focus_set())

    def _parse_input_values(self) -> None:
        self._input_values["interval"] = int(self.entry_interval.get())
        self._input_values["export_format"] = self.optionmenu_format.get()

    def get_input_values(self) -> dict:
        self._parse_input_values()
        return self._input_values

    def _is_int_above_zero(self, entry_value: Any) -> bool:
        try:
            int_value = int(entry_value)
        except Exception:
            return False
        return int_value >= 0 if int_value else True


class ToplevelExportCounts(ToplevelTemplate):
    def __init__(
        self,
        export_formats: list[str],
        input_values: dict,
        **kwargs: Any,
    ) -> None:
        self._input_values = input_values
        self._export_formats = export_formats
        self._canceled: bool = False
        super().__init__(**kwargs)
        self._get_widgets()
        self._place_widgets()
        self._set_focus()

    def _get_widgets(self) -> None:
        self._frame_configure_export = FrameConfigureExportCounts(
            master=self,
            input_values=self._input_values,
            export_formats=self._export_formats,
        )
        self._frame_ok_cancel = FrameOkCancel(
            master=self, on_ok=self._on_ok, on_cancel=self._on_cancel, ok_text="Export"
        )

    def _place_widgets(self) -> None:
        self._frame_configure_export.pack(padx=PADX, pady=PADY)
        self._frame_ok_cancel.pack(padx=PADX, pady=PADY)

    def _set_focus(self) -> None:
        self.attributes("-topmost", 1)
        self._frame_configure_export.set_focus()

    def _on_ok(self, event: Any = None) -> None:
        self._frame_configure_export.get_input_values()
        self.destroy()
        self.update()

    def _on_cancel(self, event: Any = None) -> None:
        self._canceled = True
        self.destroy()
        self.update()

    def get_data(self) -> dict:
        self.wait_window()
        if self._canceled:
            raise CancelExportCounts()
        return self._input_values
