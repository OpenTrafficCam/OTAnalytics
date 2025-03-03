from pathlib import Path
from tkinter.filedialog import askopenfilename, askopenfilenames
from typing import Iterable, Literal

from OTAnalytics.adapter_ui.file_export_dto import EventFileDto
from OTAnalytics.adapter_ui.message_box import MessageBox
from OTAnalytics.adapter_ui.ui_factory import UiFactory
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.plugin_ui.customtkinter_gui import toplevel_export_events
from OTAnalytics.plugin_ui.customtkinter_gui.helpers import ask_for_save_file_path
from OTAnalytics.plugin_ui.customtkinter_gui.messagebox import MinimalInfoBox
from OTAnalytics.plugin_ui.customtkinter_gui.toplevel_export_events import (
    ToplevelExportEvents,
)


class CtkUiFactory(UiFactory):
    def minimal_info_box(
        self, message: str, initial_position: tuple[int, int]
    ) -> MessageBox:
        return MinimalInfoBox(message=message, initial_position=initial_position)

    def askopenfilenames(
        self,
        title: str,
        filetypes: Iterable[tuple[str, str | list[str] | tuple[str, ...]]],
    ) -> Literal[""] | tuple[str, ...]:
        return askopenfilenames(title=title, filetypes=filetypes)

    def askopenfilename(
        self,
        title: str,
        filetypes: list[tuple[str, str]],
        defaultextension: str,
    ) -> str:
        return askopenfilename(
            title=title, filetypes=filetypes, defaultextension=defaultextension
        )

    def ask_for_save_file_path(
        self,
        title: str,
        filetypes: list[tuple[str, str]],
        defaultextension: str,
        initialfile: str,
        initialdir: Path,
    ) -> Path:
        return ask_for_save_file_path(
            title=title,
            filetypes=filetypes,
            defaultextension=defaultextension,
            initialfile=initialfile,
            initialdir=initialdir,
        )

    def configure_export_file(
        self,
        title: str,
        default_values: dict[str, str],
        export_format_extensions: dict[str, str],
        viewmodel: ViewModel,
    ) -> EventFileDto:
        input_values = ToplevelExportEvents(
            title=title,
            initial_position=(50, 50),
            input_values=default_values,
            export_format_extensions=export_format_extensions,
            viewmodel=viewmodel,
        ).get_data()
        file = input_values[toplevel_export_events.EXPORT_FILE]
        export_format = input_values[toplevel_export_events.EXPORT_FORMAT]
        return EventFileDto(file=file, export_format=export_format)
