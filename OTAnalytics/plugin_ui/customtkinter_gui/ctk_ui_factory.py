from datetime import datetime
from pathlib import Path
from tkinter.filedialog import askopenfilename, askopenfilenames
from typing import Iterable, Literal

from OTAnalytics.adapter_ui.file_export_dto import ExportFileDto
from OTAnalytics.adapter_ui.flow_dto import FlowDto
from OTAnalytics.adapter_ui.info_box import InfoBox
from OTAnalytics.adapter_ui.message_box import MessageBox
from OTAnalytics.adapter_ui.text_resources import ColumnResources
from OTAnalytics.adapter_ui.ui_factory import UiFactory
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.analysis.traffic_counting_specification import (
    CountingSpecificationDto,
)
from OTAnalytics.application.config import DEFAULT_COUNTING_INTERVAL_IN_MINUTES
from OTAnalytics.application.export_formats.export_mode import OVERWRITE
from OTAnalytics.application.logger import logger
from OTAnalytics.application.use_cases.generate_flows import FlowNameGenerator
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate
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
from OTAnalytics.plugin_ui.customtkinter_gui.toplevel_flows import ToplevelFlows
from OTAnalytics.plugin_ui.customtkinter_gui.toplevel_sections import ToplevelSections


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

    async def askopenfilenames(
        self,
        title: str,
        filetypes: Iterable[tuple[str, str | list[str] | tuple[str, ...]]],
    ) -> Literal[""] | tuple[str, ...]:
        return askopenfilenames(title=title, filetypes=filetypes)

    async def askopenfilename(
        self,
        title: str,
        filetypes: list[tuple[str, str]],
        defaultextension: str,
    ) -> str:
        return askopenfilename(
            title=title, filetypes=filetypes, defaultextension=defaultextension
        )

    async def ask_for_save_file_path(
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

    async def configure_export_file(
        self,
        title: str,
        export_format_extensions: dict[str, str],
        initial_file_stem: str,
        viewmodel: ViewModel,
    ) -> ExportFileDto:
        default_format = next(iter(export_format_extensions.keys()))
        default_values: dict = {
            EXPORT_FORMAT: default_format,
        }
        export_config = ToplevelExportFile(
            title=title,
            initial_position=(50, 50),
            input_values=default_values,
            export_format_extensions=export_format_extensions,
            initial_file_stem=initial_file_stem,
            viewmodel=viewmodel,
        ).get_data()
        file = export_config[toplevel_export_file.EXPORT_FILE]
        export_format = export_config[toplevel_export_file.EXPORT_FORMAT]
        return ExportFileDto(file=file, export_format=export_format)

    async def configure_export_counts(
        self,
        start: datetime | None,
        end: datetime | None,
        default_format: str,
        modes: list,
        export_formats: dict[str, str],
        viewmodel: ViewModel,
    ) -> CountingSpecificationDto:
        default_values: dict = {
            INTERVAL: DEFAULT_COUNTING_INTERVAL_IN_MINUTES,
            START: start,
            END: end,
            EXPORT_FORMAT: default_format,
        }
        export_values: dict = ToplevelExportCounts(
            title="Export counts",
            initial_position=(50, 50),
            input_values=default_values,
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

    async def configure_section(
        self,
        title: str,
        section_offset: RelativeOffsetCoordinate,
        initial_position: tuple[int, int],
        input_values: dict | None,
        show_offset: bool,
        viewmodel: ViewModel,
    ) -> dict:
        return ToplevelSections(
            title=title,
            viewmodel=viewmodel,
            section_offset=section_offset,
            initial_position=initial_position,
            input_values=input_values,
            show_offset=show_offset,
        ).get_metadata()

    async def configure_flow(
        self,
        title: str,
        initial_position: tuple[int, int],
        section_ids: ColumnResources,
        input_values: FlowDto | None,
        name_generator: FlowNameGenerator,
        show_distance: bool,
    ) -> FlowDto:
        return ToplevelFlows(
            title=title,
            initial_position=initial_position,
            section_ids=section_ids,
            name_generator=name_generator,
            input_values=input_values,
            show_distance=show_distance,
        ).get_data()
