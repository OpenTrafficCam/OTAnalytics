from dataclasses import dataclass
from typing import Self

from nicegui import ui
from OTCloud.adapter.nicegui_mapping.otcloud_mapper import NiceguiOtcloudJobConfig
from OTCloud.plugin_webserver.nicegui.constants import Alignment
from OTCloud.plugin_webserver.nicegui.elements.forms import (
    FormFieldCheckbox,
    FormFieldText,
)

LABEL_COPY_FILES_BEFORE_PROCESSING = "Copy Files Before Processing"
LABEL_PROJECT_NAME = "Project Name"
LABEL_OTCONFIG_FILE = "OTConfig File"
LABEL_OTCLOUD_SETTINGS = "OTCloud Settings"

MARKER_PROJECT_NAME = "marker-project-name"
MARKER_COPY_FILES_BEFORE_PROCESSING = "marker-copy-files_before_processing"
MARKER_OTCONFIG_FILE = "marker-otconfig-file"

VALIDATION_MSG_PROJECT_NAME = "Please enter a project name"


@dataclass(frozen=True)
class NiceguiOtcloudSettings:
    project_name: str
    copy_files_before_processing: bool
    otconfig: str


class OtcloudConfigSettings:
    """Responsible to build the UI components of the OTCloud job config settings form.

    Args:
        project_name (str): the project name.
        copy_files_before_processing (bool): whether to copy files to external
            environment before processing.

    """

    def __init__(
        self, project_name: str, copy_files_before_processing: bool, otconfig_file: str
    ) -> None:
        self._copy_files_before_processing = FormFieldCheckbox(
            label_text=LABEL_COPY_FILES_BEFORE_PROCESSING,
            initial_value=copy_files_before_processing,
            marker=MARKER_COPY_FILES_BEFORE_PROCESSING,
        )
        self._project_name = FormFieldText(
            LABEL_PROJECT_NAME,
            initial_value=project_name,
            validation={VALIDATION_MSG_PROJECT_NAME: lambda value: value},
            marker=MARKER_PROJECT_NAME,
        )
        self._otconfig_file = FormFieldText(
            LABEL_OTCONFIG_FILE,
            initial_value=otconfig_file,
            disabled=True,
            readonly=True,
            marker=MARKER_OTCONFIG_FILE,
        )

    def build(self) -> Self:
        """Builds the ui elements for OTCloud config settings form."""
        with ui.card(align_items=Alignment.stretch):
            with ui.grid():
                ui.label(LABEL_OTCLOUD_SETTINGS).classes("text-xl font-bold")
                self._project_name.build()
                self._otconfig_file.build()
                self._copy_files_before_processing.build()
        return self

    def validate(self) -> bool:
        """Validate the fields in this form for invalid inputs.

        Returns:
            bool: True if the form fields are valid, False otherwise.

        """
        return self._project_name.validate()

    def update(self, config: NiceguiOtcloudJobConfig) -> None:
        """Update the current fields in this form with config.

        This also refreshes the respective UI elements.

        Args:
            config (NiceguiOtcloudJobConfig): the config to update the fields with.

        """
        self._project_name.set_value(config.project_name)
        self._otconfig_file.set_value(config.otconfig_file)
        self._copy_files_before_processing.set_value(
            config.copy_files_before_processing
        )

    def get_config(self) -> NiceguiOtcloudSettings:
        """Get the current OTCloud config settings filled out by the user.

        Returns:
            NiceguiOtcloudSettings: The current config filled out by the
                user.

        """
        return NiceguiOtcloudSettings(
            project_name=self._project_name.value,
            copy_files_before_processing=self._copy_files_before_processing.value,
            otconfig=self._otconfig_file.value,
        )
