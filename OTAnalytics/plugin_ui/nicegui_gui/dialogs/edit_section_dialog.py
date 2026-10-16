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
from OTAnalytics.plugin_ui.nicegui_gui.forms.offset_slider_form import OffsetSliderForm
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.dialog import BaseDialog
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.forms import FormFieldText
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.validation import ERROR_MSG_REQUIRED
from OTAnalytics.plugin_ui.nicegui_gui.test_constants import TEST_ID

MARKER_NAME = "marker-name"
MARKER_START_SECTION = "marker-start-section"
MARKER_END_SECTION = "marker-end-section"
MARKER_DISTANCE = "marker-distance"
ERROR_MSG_NAME_NOT_UNIQUE = "Name is already used"


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
            validation={
                ERROR_MSG_REQUIRED: self._is_name_present,
                ERROR_MSG_NAME_NOT_UNIQUE: self._is_name_unique,
            },
            marker=MARKER_NAME,
        )
        self._offset = OffsetSliderForm(self.resource_manager)

    def build_content(self) -> None:
        self._name.build()
        self._name.element.props(f"{TEST_ID}={MARKER_NAME}")

        self._offset.build()

    def validate(self) -> bool:
        return self._name.validate()

    @staticmethod
    def _is_name_present(name: str) -> bool:
        return bool(name and name.strip())

    def _is_name_unique(self, name: str) -> bool:
        if not self._is_name_present(name):
            # Reported by the required check.
            return True
        if (self._input_values is not None) and (name == self._input_values.get(NAME)):
            return True
        return self._viewmodel.is_section_name_valid(name)

    def get_section(self) -> dict:
        self._check_section_name()
        return {
            NAME: self._name.value,
            RELATIVE_OFFSET_COORDINATES: {
                EventType.SECTION_ENTER.serialize(): self._offset.offset.to_dict()
            },
        }

    def _check_section_name(self) -> None:
        new_entry_name = self._name.value
        if not self._is_name_present(new_entry_name):
            raise NoUniqueNameException("Please choose a name for the section!")
        if not self._is_name_unique(new_entry_name):
            raise NoUniqueNameException(
                f"Please choose a unique name, {new_entry_name} is already used!"
            )
