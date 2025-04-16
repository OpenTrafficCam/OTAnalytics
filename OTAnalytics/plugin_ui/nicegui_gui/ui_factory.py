import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Literal

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
from OTAnalytics.application.application import CancelAddFlow
from OTAnalytics.application.resources.resource_manager import ResourceManager
from OTAnalytics.application.use_cases.generate_flows import FlowNameGenerator
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate
from OTAnalytics.plugin_ui.nicegui_gui.dialogs.edit_flow_dialog import EditFlowDialog
from OTAnalytics.plugin_ui.nicegui_gui.dialogs.edit_section_dialog import (
    EditSectionDialog,
)
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.dialog import DialogResult


class NiceGuiMessageBox(MessageBox):

    def close(self) -> None:
        pass

    def update_message(self, message: str) -> None:
        pass


class NiceGuiInfoBox(InfoBox):
    @property
    def canceled(self) -> bool:
        return False


class NiceGuiUiFactory(UiFactory):

    def __init__(self, resource_manager: ResourceManager) -> None:
        self._resource_manager = resource_manager

    def info_box(
        self, message: str, initial_position: tuple[int, int], show_cancel: bool = False
    ) -> InfoBox:
        return NiceGuiInfoBox()

    def minimal_info_box(
        self, message: str, initial_position: tuple[int, int]
    ) -> MessageBox:
        return NiceGuiMessageBox()

    def askopenfilename(
        self, title: str, filetypes: list[tuple[str, str]], defaultextension: str
    ) -> str:
        return ""

    def askopenfilenames(
        self,
        title: str,
        filetypes: Iterable[tuple[str, str | list[str] | tuple[str, ...]]],
    ) -> Literal[""] | tuple[str, ...]:
        return tuple([""])

    def ask_for_save_file_path(
        self,
        title: str,
        filetypes: list[tuple[str, str]],
        defaultextension: str,
        initialfile: str,
        initialdir: Path,
    ) -> Path:
        return Path("")

    def configure_export_file(
        self,
        title: str,
        export_format_extensions: dict[str, str],
        initial_file_stem: str,
        viewmodel: ViewModel,
    ) -> ExportFileDto:
        raise NotImplementedError

    def configure_export_counts(
        self,
        start: datetime | None,
        end: datetime | None,
        default_format: str,
        modes: list,
        export_formats: dict[str, str],
        viewmodel: ViewModel,
    ) -> CountingSpecificationDto:
        raise NotImplementedError

    async def configure_section(
        self,
        title: str,
        section_offset: RelativeOffsetCoordinate,
        initial_position: tuple[int, int],
        input_values: dict | None,
        show_offset: bool,
        viewmodel: ViewModel,
    ) -> dict:
        dialog = EditSectionDialog(
            resource_manager=self._resource_manager,
            viewmodel=viewmodel,
            title=title,
            section_offset=section_offset,
            input_values=input_values,
            show_offset=show_offset,
        )
        result = await dialog.build()
        if result == DialogResult.APPLY:
            return dialog.get_section()
        raise CancelAddFlow()

    async def configure_flow(
        self,
        title: str,
        initial_position: tuple[int, int],
        section_ids: ColumnResources,
        input_values: FlowDto | None,
        name_generator: FlowNameGenerator,
        show_distance: bool,
    ) -> FlowDto:
        dialog = EditFlowDialog(
            resource_manager=self._resource_manager,
            section_ids=section_ids,
            name_generator=name_generator,
            input_values=input_values,
            show_distance=show_distance,
        )
        result = await dialog.build()
        if result == DialogResult.APPLY:
            return dialog.get_flow()
        raise CancelAddFlow()


def async_to_sync(awaitable: Any) -> None:
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(awaitable)
