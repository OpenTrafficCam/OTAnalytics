from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.resources.resource_manager import (
    EditFlowDialogKeys,
    ResourceManager,
)
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate
from OTAnalytics.domain.section import NAME, RELATIVE_OFFSET_COORDINATES
from OTAnalytics.domain.types import EventType
from OTAnalytics.plugin_ui.customtkinter_gui.toplevel_sections import (
    NoUniqueNameException,
)
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.dialog import BaseDialog
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.forms import FormFieldText

MARKER_NAME = "marker-name"
MARKER_START_SECTION = "marker-start-section"
MARKER_END_SECTION = "marker-end-section"
MARKER_DISTANCE = "marker-distance"


class EditSectionDialog(BaseDialog):
    def __init__(
        self,
        resource_manager: ResourceManager,
        viewmodel: ViewModel,
        title: str,
        section_offset: RelativeOffsetCoordinate,
        input_values: dict | None = None,
        show_offset: bool = True,
    ) -> None:
        super().__init__(resource_manager)
        self._viewmodel = viewmodel
        self._title = title
        self._section_offset = section_offset
        self._input_values = input_values
        self._show_offset = show_offset
        name = input_values.get(NAME, "") if input_values else ""
        self._name = FormFieldText(
            label_text=self.resource_manager.get(EditFlowDialogKeys.LABEL_NAME),
            initial_value=name,
            marker=MARKER_NAME,
        )
        # TODO add offset form

    async def build_content(self) -> None:
        self._name.build()

    def get_section(self) -> dict:
        self._check_section_name()
        offset = RelativeOffsetCoordinate(x=0, y=0)
        return {
            NAME: self._name.value,
            RELATIVE_OFFSET_COORDINATES: {
                EventType.SECTION_ENTER.serialize(): offset.to_dict()
            },
        }
        # self._input_values[RELATIVE_OFFSET_COORDINATES][
        #     EventType.SECTION_ENTER.serialize()
        # ] = self.frame_bbox_offset.get_relative_offset_coordintes()

    def _check_section_name(self) -> None:
        new_entry_name = self._name.value
        if (self._input_values is not None) and (
            new_entry_name == self._input_values.get(NAME)
        ):
            return
        if not self._viewmodel.is_section_name_valid(new_entry_name):
            raise NoUniqueNameException(
                f"Please choose a unique name, {new_entry_name} is already used!"
            )
