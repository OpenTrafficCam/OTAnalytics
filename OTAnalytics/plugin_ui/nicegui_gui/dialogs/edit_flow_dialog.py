from nicegui.events import ValueChangeEventArguments

from OTAnalytics.adapter_ui.flow_dto import FlowDto
from OTAnalytics.adapter_ui.text_resources import ColumnResources
from OTAnalytics.application.resources.resource_manager import (
    EditFlowDialogKeys,
    ResourceManager,
)
from OTAnalytics.application.use_cases.generate_flows import FlowNameGenerator
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.dialog import BaseDialog
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.forms import (
    FormFieldOptionalFloat,
    FormFieldSelect,
    FormFieldText,
)
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.validation import (
    VALIDATION_NUMBER_POSITIVE,
)

MARKER_NAME = "marker-name"
MARKER_START_SECTION = "marker-start-section"
MARKER_END_SECTION = "marker-end-section"
MARKER_DISTANCE = "marker-distance"


class EditFlowDialog(BaseDialog):
    def __init__(
        self,
        resource_manager: ResourceManager,
        section_ids: ColumnResources,
        name_generator: FlowNameGenerator,
        input_values: FlowDto | None = None,
        show_distance: bool = True,
    ) -> None:
        super().__init__(resource_manager)
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
            label_text=self.resource_manager.get(EditFlowDialogKeys.LABEL_NAME),
            initial_value=name,
            on_value_change=self._update_name,
            marker=MARKER_NAME,
        )
        self._start_section = FormFieldSelect(
            label_text=self.resource_manager.get(
                EditFlowDialogKeys.LABEL_START_SECTION
            ),
            options=section_ids.names,
            initial_value=start_value,
            on_value_change=self._update_name,
            marker=MARKER_START_SECTION,
        )
        self._end_section = FormFieldSelect(
            label_text=self.resource_manager.get(EditFlowDialogKeys.LABEL_END_SECTION),
            options=section_ids.names,
            initial_value=end_value,
            on_value_change=self._update_name,
            marker=MARKER_END_SECTION,
        )
        self._distance = FormFieldOptionalFloat(
            label_text=self.resource_manager.get(EditFlowDialogKeys.LABEL_DISTANCE),
            initial_value=input_values.distance if input_values else None,
            min_value=0,
            validation=VALIDATION_NUMBER_POSITIVE,
            marker=MARKER_DISTANCE,
        )

    def build_content(self) -> None:
        self._start_section.build()
        self._end_section.build()
        self._name.build()
        self._distance.build()
        self._do_update_name()

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
