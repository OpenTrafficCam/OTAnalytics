from pathlib import Path
from tkinter.filedialog import askopenfilename, askopenfilenames
from typing import Iterable, Literal

from OTAnalytics.adapter_ui.file_export_dto import EventFileDto
from OTAnalytics.adapter_ui.info_box import InfoBox
from OTAnalytics.adapter_ui.message_box import MessageBox
from OTAnalytics.adapter_ui.ui_factory import UiFactory
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.analysis.traffic_counting_specification import (
    CountingSpecificationDto,
)
from OTAnalytics.application.export_formats.export_mode import OVERWRITE
from OTAnalytics.application.logger import logger
from OTAnalytics.plugin_ui.customtkinter_gui import toplevel_export_file
from OTAnalytics.plugin_ui.customtkinter_gui.helpers import ask_for_save_file_path
from OTAnalytics.plugin_ui.customtkinter_gui.messagebox import (
    CtkInfoBox,
    MinimalInfoBox,
)
from OTAnalytics.plugin_ui.customtkinter_gui.toplevel_export_counts import (
    END,
    EXPORT_FILE,
    EXPORT_FORMAT,
    INTERVAL,
    START,
    ToplevelExportCounts,
)
from OTAnalytics.plugin_ui.customtkinter_gui.toplevel_export_file import (
    ToplevelExportFile,
)


class CtkUiFactory(UiFactory):
    def info_box(
        self, message: str, initial_position: tuple[int, int], show_cancel: bool = False
    ) -> InfoBox:
        return CtkInfoBox(
            message=message, initial_position=initial_position, show_cancel=show_cancel
        )

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
        initial_file_stem: str,
        viewmodel: ViewModel,
    ) -> EventFileDto:
        input_values = ToplevelExportFile(
            title=title,
            initial_position=(50, 50),
            input_values=default_values,
            export_format_extensions=export_format_extensions,
            initial_file_stem=initial_file_stem,
            viewmodel=viewmodel,
        ).get_data()
        file = input_values[toplevel_export_file.EXPORT_FILE]
        export_format = input_values[toplevel_export_file.EXPORT_FORMAT]
        return EventFileDto(file=file, export_format=export_format)

    def configure_export_counts(
        self,
        input_values: dict,
        modes: list,
        export_formats: dict[str, str],
        viewmodel: ViewModel,
    ) -> CountingSpecificationDto:
        export_values: dict = ToplevelExportCounts(
            title="Export counts",
            initial_position=(50, 50),
            input_values=input_values,
            export_formats=export_formats,
            viewmodel=viewmodel,
        ).get_data()
        logger().debug(export_values)
        return CountingSpecificationDto(
            interval_in_minutes=export_values[INTERVAL],
            start=export_values[START],
            end=export_values[END],
            modes=modes,
            output_format=export_values[EXPORT_FORMAT],
            output_file=export_values[EXPORT_FILE],
            export_mode=OVERWRITE,
        )
