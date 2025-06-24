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
from OTAnalytics.plugin_ui.nicegui_gui.dialogs.export_counts_dialog import (
    ExportCountsDialog,
)
from OTAnalytics.plugin_ui.nicegui_gui.dialogs.file_chooser_dialog import (
    FileChooserDialog,
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

    async def askopenfilename(
        self, title: str, filetypes: list[tuple[str, str]], defaultextension: str
    ) -> str:
        # Convert filetypes to the format expected by FileChooserDialog
        file_extensions = {desc: ext.replace(".", "") for desc, ext in filetypes}

        dialog = FileChooserDialog(
            resource_manager=self._resource_manager,
            title=title,
            file_extensions=file_extensions,
            initial_file_stem="",
        )

        result = await dialog.result
        if result == DialogResult.APPLY:
            return str(dialog.get_file_path())
        return ""

    async def askopenfilenames(
        self,
        title: str,
        filetypes: Iterable[tuple[str, str | list[str] | tuple[str, ...]]],
    ) -> Literal[""] | tuple[str, ...]:
        # For now, we'll just support selecting a single file
        # In a real implementation, this would allow selecting multiple files
        # Convert list/tuple of extensions to individual (desc, ext) pairs
        converted_filetypes = []
        for desc, ext in filetypes:
            if isinstance(ext, str):
                converted_filetypes.append((desc, ext))
            elif isinstance(ext, (list, tuple)) and ext:
                # Use the first extension from the list/tuple
                converted_filetypes.append((desc, ext[0]))

        file_path = await self.askopenfilename(title, converted_filetypes, "")
        if file_path:
            return (file_path,)
        return ""

    async def ask_for_save_file_path(
        self,
        title: str,
        filetypes: list[tuple[str, str]],
        defaultextension: str,
        initialfile: str,
        initialdir: Path,
    ) -> Path:
        # Convert filetypes to the format expected by FileChooserDialog
        file_extensions = {desc: ext.replace(".", "") for desc, ext in filetypes}

        dialog = FileChooserDialog(
            resource_manager=self._resource_manager,
            title=title,
            file_extensions=file_extensions,
            initial_file_stem=Path(initialfile).stem,
            initial_dir=initialdir,
        )

        result = await dialog.result
        if result == DialogResult.APPLY:
            return dialog.get_file_path()
        return Path("")

    async def configure_export_file(
        self,
        title: str,
        export_format_extensions: dict[str, str],
        initial_file_stem: str,
        viewmodel: ViewModel,
    ) -> ExportFileDto:
        dialog = FileChooserDialog(
            resource_manager=self._resource_manager,
            title=title,
            file_extensions=export_format_extensions,
            initial_file_stem=initial_file_stem,
        )

        result = await dialog.result
        if result == DialogResult.APPLY:
            return ExportFileDto(
                file=dialog.get_file_path(),
                export_format=dialog.get_format(),
            )
        raise CancelAddFlow()

    async def configure_export_counts(
        self,
        start: datetime | None,
        end: datetime | None,
        default_format: str,
        modes: list,
        export_formats: dict[str, str],
        viewmodel: ViewModel,
    ) -> CountingSpecificationDto:
        dialog = ExportCountsDialog(
            resource_manager=self._resource_manager,
            viewmodel=viewmodel,
            start=start,
            end=end,
            default_format=default_format,
            modes=modes,
            export_formats=export_formats,
        )

        result = await dialog.result
        if result == DialogResult.APPLY:
            return dialog.get_specification()
        raise CancelAddFlow()

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
        result = await dialog.result
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
        result = await dialog.result
        if result == DialogResult.APPLY:
            return dialog.get_flow()
        raise CancelAddFlow()


def async_to_sync(awaitable: Any) -> Any:
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(awaitable)
