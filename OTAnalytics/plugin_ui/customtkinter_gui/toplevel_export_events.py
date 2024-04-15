import contextlib
from typing import Any

from customtkinter import CTkLabel, CTkOptionMenu

from OTAnalytics.plugin_ui.customtkinter_gui.constants import PADX, PADY, STICKY
from OTAnalytics.plugin_ui.customtkinter_gui.helpers import ask_for_save_file_name
from OTAnalytics.plugin_ui.customtkinter_gui.toplevel_template import (
    FrameContent,
    ToplevelTemplate,
)

EXPORT_FORMAT = "export_format"
EXPORT_FILE = "export_file"
INITIAL_FILE_STEM = "events"


class CancelExportEvents(Exception):
    pass


class FileSelectionCancelledException(Exception):
    pass


class FrameConfigureExportEvents(FrameContent):
    def __init__(
        self,
        export_format_extensions: dict[str, str],
        input_values: dict,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._input_values = input_values
        self._export_format_extensions = export_format_extensions
        self._get_widgets()
        self._place_widgets()

    def _get_widgets(self) -> None:
        self.label_format = CTkLabel(master=self, text="Format")
        self.optionmenu_format = CTkOptionMenu(
            master=self, values=list(self._export_format_extensions.keys())
        )
        self.optionmenu_format.set(self._input_values[EXPORT_FORMAT])

    def _place_widgets(self) -> None:
        self.label_format.grid(row=0, column=0, padx=PADX, pady=PADY, sticky=STICKY)
        self.optionmenu_format.grid(
            row=0, column=1, columnspan=2, padx=PADX, pady=PADY, sticky=STICKY
        )

    def set_focus(self) -> None:
        self.after(0, lambda: self.optionmenu_format.focus_set())

    def _parse_input_values(self) -> None:
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


class ToplevelExportEvents(ToplevelTemplate):
    def __init__(
        self,
        export_format_extensions: dict[str, str],
        input_values: dict,
        initial_file_stem: str = INITIAL_FILE_STEM,
        **kwargs: Any,
    ) -> None:
        self._input_values = input_values
        self._export_format_extensions = export_format_extensions
        self._initial_file_stem = initial_file_stem
        super().__init__(**kwargs)

    def _create_frame_content(self, master: Any) -> FrameContent:
        return FrameConfigureExportEvents(
            master=master,
            export_format_extensions=self._export_format_extensions,
            input_values=self._input_values,
        )

    def _choose_file(self) -> None:
        export_format = self._input_values[EXPORT_FORMAT]  #
        export_extension = f"*{self._export_format_extensions[export_format]}"
        export_file = ask_for_save_file_name(
            title="Save counts as",
            filetypes=[(export_format, export_extension)],
            defaultextension=export_extension,
            initialfile=self._initial_file_stem,
        )
        self._input_values[EXPORT_FILE] = export_file
        if export_file == "":
            raise FileSelectionCancelledException

    def _on_ok(self, event: Any = None) -> None:
        self._input_values = self._frame_content.get_input_values()
        with contextlib.suppress(FileSelectionCancelledException):
            self._choose_file()
            self._close()

    def get_data(self) -> dict:
        self.wait_window()
        if self._canceled:
            raise CancelExportEvents()
        return self._input_values
