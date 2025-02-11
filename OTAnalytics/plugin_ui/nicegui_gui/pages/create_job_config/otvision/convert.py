from typing import Self

from nicegui import ui
from OTCloud.adapter.nicegui_mapping.otvision_mapper import NiceguiOtvisionConvertConfig
from OTCloud.plugin_webserver.nicegui.elements.forms import (
    FormFieldCheckbox,
    FormFieldFloat,
    FormFieldInteger,
    FormFieldText,
)
from OTCloud.plugin_webserver.nicegui.validation import (
    VALIDATION_FILES,
    VALIDATION_NUMBER_POSITIVE,
)
from OTCloud.plugin_webserver.pages.create_job_config.config import (
    LABEL_FILES,
    LABEL_OVERWRITE,
)

LABEL_INPUT_FPS = "Input FPS"
LABEL_ROTATION = "Rotation"
LABEL_DELETE_INPUT = "Delete Input"
LABEL_FPS_FROM_FILENAME = "FPS from filename"

MARKER_CONVERT_FILES = "marker-convert-files"
MARKER_INPUT_FPS = "marker-input-fps"
MARKER_ROTATION = "marker-rotation"
MARKER_DELETE_INPUT = "marker-delete-input"
MARKER_FPS_FROM_FILENAME = "marker-fps-from-filename"
MARKER_CONVERT_OVERWRITE = "marker-convert-overwrite"


class OtvisionConvertForm:
    """The OTVision convert form.

    Args:
        config (NiceguiOtvisionConvertConfig): the convert config to prefill the fields.

    """

    def __init__(
        self,
        config: NiceguiOtvisionConvertConfig,
    ) -> None:
        self._files = FormFieldText(
            LABEL_FILES,
            config.paths,
            validation=VALIDATION_FILES,
            marker=MARKER_CONVERT_FILES,
        )
        self._input_fps = FormFieldFloat(
            LABEL_INPUT_FPS,
            config.input_fps,
            min_value=0,
            validation=VALIDATION_NUMBER_POSITIVE,
            marker=MARKER_INPUT_FPS,
        )
        self._rotation = FormFieldInteger(
            LABEL_ROTATION,
            config.rotation,
            min_value=0,
            validation=VALIDATION_NUMBER_POSITIVE,
            marker=MARKER_ROTATION,
        )
        self._delete_input = FormFieldCheckbox(
            LABEL_DELETE_INPUT, config.delete_input, marker=MARKER_DELETE_INPUT
        )
        self._fps_from_filename = FormFieldCheckbox(
            LABEL_FPS_FROM_FILENAME,
            config.fps_from_filename,
            marker=MARKER_FPS_FROM_FILENAME,
        )
        self._overwrite = FormFieldCheckbox(
            LABEL_OVERWRITE, config.overwrite, marker=MARKER_CONVERT_OVERWRITE
        )

    def build(self) -> Self:
        """Builds the ui elements for OTVision convert config form."""
        ui.label("Convert").classes("text-lg font-bold")
        self._files.build()
        self._input_fps.build()
        self._rotation.build()
        self._delete_input.build()
        self._fps_from_filename.build()
        self._overwrite.build()
        return self

    def validate(self) -> bool:
        """Validate the fields in this form for invalid inputs.

        Returns:
            bool: True if the form fields are valid, False otherwise.


        """
        return all(
            [
                self._files.validate(),
                self._input_fps.validate(),
                self._rotation.validate(),
            ]
        )

    def update(self, config: NiceguiOtvisionConvertConfig) -> None:
        """Update the current fields in this form with config.

        This also refreshes the respective UI elements.

        Args:
            config (NiceguiOtvisionConvertConfig): the config to update the fields with.

        """
        self._files.set_value(config.paths)
        self._input_fps.set_value(config.input_fps)
        self._rotation.set_value(config.rotation)

    def get_config(self) -> NiceguiOtvisionConvertConfig:
        """Get the current OTVision convert config filled out by the user.

        Returns:
            NiceguiOtvisionConvertConfig: The current config filled out by the
                user.

        """
        return NiceguiOtvisionConvertConfig(
            paths=self._files.value,
            input_fps=self._input_fps.value,
            rotation=self._rotation.value,
            delete_input=self._delete_input.value,
            fps_from_filename=self._fps_from_filename.value,
            overwrite=self._overwrite.value,
        )
