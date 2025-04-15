import asyncio
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Any, Iterable, Literal

from nicegui import ui
from nicegui.events import ValueChangeEventArguments

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
from OTAnalytics.application.resources.resource_manager import (
    EditFlowDialogKeys,
    GeneralKeys,
    ResourceManager,
)
from OTAnalytics.application.use_cases.generate_flows import FlowNameGenerator
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.forms import (
    FormFieldOptionalFloat,
    FormFieldSelect,
    FormFieldText,
)
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.validation import (
    VALIDATION_NUMBER_POSITIVE,
)


class NiceGuiMessageBox(MessageBox):

    def close(self) -> None:
        pass

    def update_message(self, message: str) -> None:
        pass


class NiceGuiInfoBox(InfoBox):
    @property
    def canceled(self) -> bool:
        return False


class DialogResult(StrEnum):
    APPLY = "Apply"
    CANCEL = "Cancel"


MARKER_NAME = "marker-name"
MARKER_START_SECTION = "marker-start-section"
MARKER_END_SECTION = "marker-end-section"
MARKER_DISTANCE = "marker-distance"


class EditFlowDialog(ui.dialog):
    def __init__(
        self,
        resource_manager: ResourceManager,
        section_ids: ColumnResources,
        name_generator: FlowNameGenerator,
        input_values: FlowDto | None = None,
        show_distance: bool = True,
    ) -> None:
        self._resource_manager = resource_manager
        self._name_generator = name_generator
        self._input_values = input_values
        self._show_distance = show_distance
        name = input_values.name if input_values else ""
        self._last_autofilled_name: str = name
        start_value = (
            section_ids.get_name_for(input_values.start_section)
            if input_values
            else None
        )
        end_value = (
            section_ids.get_name_for(input_values.end_section) if input_values else None
        )
        self._name = FormFieldText(
            label_text=resource_manager.get(EditFlowDialogKeys.LABEL_NAME),
            initial_value=name,
            on_value_change=self._update_name,
            marker=MARKER_NAME,
        )
        self._start_section = FormFieldSelect(
            label_text=resource_manager.get(EditFlowDialogKeys.LABEL_START_SECTION),
            options=section_ids.names,
            initial_value=start_value,
            on_value_change=self._update_name,
            marker=MARKER_START_SECTION,
        )
        self._end_section = FormFieldSelect(
            label_text=resource_manager.get(EditFlowDialogKeys.LABEL_END_SECTION),
            options=section_ids.names,
            initial_value=end_value,
            on_value_change=self._update_name,
            marker=MARKER_END_SECTION,
        )
        self._distance = FormFieldOptionalFloat(
            label_text=resource_manager.get(EditFlowDialogKeys.LABEL_DISTANCE),
            initial_value=input_values.distance if input_values else None,
            min_value=0,
            validation=VALIDATION_NUMBER_POSITIVE,
            marker=MARKER_DISTANCE,
        )

    async def build(self) -> Any:
        with ui.dialog() as dialog, ui.card():
            self._start_section.build()
            self._end_section.build()
            self._name.build()
            self._distance.build()
            with ui.row():
                ui.button(
                    self._resource_manager.get(GeneralKeys.LABEL_APPLY),
                    on_click=lambda: dialog.submit(DialogResult.APPLY),
                )
                ui.button(
                    self._resource_manager.get(GeneralKeys.LABEL_CANCEL),
                    on_click=lambda: dialog.submit(DialogResult.CANCEL),
                )
            self._do_update_name()
            return await dialog

    def _update_name(self, value: ValueChangeEventArguments) -> None:
        self._do_update_name()

    def _do_update_name(self) -> None:
        if self._last_autofilled_name == self._name.value:
            start_section = self._start_section.value
            end_section = self._end_section.value
            auto_name = self._name_generator.generate_from_string(
                start_section, end_section
            )
            self._name.set_value(auto_name)
            self._last_autofilled_name = auto_name

    def get_flow(self) -> FlowDto:
        return FlowDto(
            name=self._name.value,
            start_section=self._start_section.value,
            end_section=self._end_section.value,
            flow_id=self._input_values.flow_id if self._input_values else None,
            distance=self._distance.value,
        )


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

    def configure_section(
        self,
        title: str,
        section_offset: RelativeOffsetCoordinate,
        initial_position: tuple[int, int],
        input_values: dict | None,
        show_offset: bool,
        viewmodel: ViewModel,
    ) -> dict:
        # return asyncio.run(self._open_save_dialog())
        def create_dialog() -> ui.dialog:
            with ui.dialog() as dialog, ui.card():
                self.name = ui.input()
                ui.button("Yes", on_click=lambda: dialog.submit({"yes": "Yes"}))
                ui.button("No", on_click=lambda: dialog.submit("No"))
            return dialog

        async def show() -> Any:
            return await create_dialog()

        # result = asyncio.run(show())
        # result = async_to_sync(show())
        # result = ui.timer(0,show, once=True)
        result: dict = {}
        print(f"Result of async_to_sync is: {result}")

        return result

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
