from typing import Self

from nicegui import ui
from OTCloud.adapter.nicegui_mapping.otvision_mapper import NiceguiOtvisionTrackConfig
from OTCloud.plugin_webserver.nicegui.elements.forms import (
    FormFieldCheckbox,
    FormFieldFloat,
    FormFieldInteger,
    FormFieldText,
)
from OTCloud.plugin_webserver.nicegui.validation import (
    VALIDATION_FILES,
    VALIDATION_NUMBER_POSITIVE,
    VALIDATION_NUMBER_RANGE_0_1,
)
from OTCloud.plugin_webserver.pages.create_job_config.config import (
    LABEL_FILES,
    LABEL_OVERWRITE,
)

LABEL_SIGMA_H = "Sigma H"
LABEL_SIGMA_IOU = "Sigma IOU"
LABEL_SIGMA_L = "Sigma L"
LABEL_T_MIN = "t_min"
LABEL_T_MISS_MAX = "t_miss_max"
LABEL_TRACK = "Track"
MARKER_TRACK_FILES = "marker-track-files"
MARKER_SIGMA_H = "marker-sigma-h"
MARKER_SIGMA_IOU = "marker-sigma-iou"
MARKER_SIGMA_L = "marker-sigma-l"
MARKER_T_MIN = "marker-t_min"
MARKER_T_MISS_MAX = "marker-t-miss-max"
MARKER_TRACK_OVERWRITE = "marker-track-overwrite"


class OtvisionTrackForm:
    """The OTVision detect form.

    Args:
        config (NiceguiOtvisionTrackConfig): the track config to prefill the fields.

    """

    def __init__(self, config: NiceguiOtvisionTrackConfig) -> None:
        self._files = FormFieldText(
            LABEL_FILES,
            config.paths,
            validation=VALIDATION_FILES,
            marker=MARKER_TRACK_FILES,
        )
        self._sigma_h = FormFieldFloat(
            LABEL_SIGMA_H,
            config.sigma_h,
            min_value=0,
            max_value=1,
            validation=VALIDATION_NUMBER_RANGE_0_1,
            marker=MARKER_SIGMA_H,
        )
        self._sigma_iou = FormFieldFloat(
            LABEL_SIGMA_IOU,
            config.sigma_iou,
            min_value=0,
            max_value=1,
            validation=VALIDATION_NUMBER_RANGE_0_1,
            marker=MARKER_SIGMA_IOU,
        )
        self._sigma_l = FormFieldFloat(
            LABEL_SIGMA_L,
            config.sigma_l,
            min_value=0,
            max_value=1,
            validation=VALIDATION_NUMBER_RANGE_0_1,
            marker=MARKER_SIGMA_L,
        )
        self._t_min = FormFieldInteger(
            LABEL_T_MIN,
            config.t_min,
            min_value=0,
            validation=VALIDATION_NUMBER_POSITIVE,
            marker=MARKER_T_MIN,
        )
        self._t_miss_max = FormFieldInteger(
            LABEL_T_MISS_MAX,
            config.t_miss_max,
            min_value=0,
            validation=VALIDATION_NUMBER_POSITIVE,
            marker=MARKER_T_MISS_MAX,
        )
        self._overwrite = FormFieldCheckbox(
            LABEL_OVERWRITE, config.overwrite, marker=MARKER_TRACK_OVERWRITE
        )

    def build(self) -> Self:
        """Builds the ui elements for OTVision track config form."""
        ui.label(LABEL_TRACK).classes("text-lg font-bold")
        self._files.build()
        self._sigma_h.build()
        self._sigma_iou.build()
        self._sigma_l.build()
        self._t_min.build()
        self._t_miss_max.build()
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
                self._sigma_h.validate(),
                self._sigma_iou.validate(),
                self._sigma_l.validate(),
                self._t_min.validate(),
                self._t_miss_max.validate(),
            ]
        )

    def update(self, config: NiceguiOtvisionTrackConfig) -> None:
        """Update the current fields in this form with config.

        This also refreshes the respective UI elements.

        Args:
            config (NiceguiOtvisionTrackConfig): the config to update the fields with.

        """

        self._files.set_value(config.paths)
        self._sigma_h.set_value(config.sigma_h)
        self._sigma_iou.set_value(config.sigma_iou)
        self._sigma_l.set_value(config.sigma_l)
        self._t_min.set_value(config.t_min)
        self._t_miss_max.set_value(config.t_miss_max)
        self._overwrite.set_value(config.overwrite)

    def get_config(self) -> NiceguiOtvisionTrackConfig:
        """Get the current OTVision convert config filled out by the user.

        Returns:
            NiceguiOtvisionConvertConfig: The current config filled out by the
                user.

        """
        return NiceguiOtvisionTrackConfig(
            paths=self._files.value,
            sigma_h=self._sigma_h.value,
            sigma_iou=self._sigma_iou.value,
            sigma_l=self._sigma_l.value,
            t_min=self._t_min.value,
            t_miss_max=self._t_miss_max.value,
            overwrite=self._overwrite.value,
        )
