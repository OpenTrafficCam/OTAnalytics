from typing import Self

from nicegui import ui
from OTCloud.adapter.nicegui_mapping.otvision_mapper import NiceguiOtvisionDetectConfig
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

LABEL_EXPECTED_DURATION = "Expected Duration"
LABEL_TORCH_HUB_CACHE_FORCE_RELOAD = "Force Reload PyTorch Hub Cache"
LABEL_HALF_PRECISION = "Half Precision"
LABEL_DETECTION_CONFIDENCE = "Detection Confidence"
LABEL_DETECTION_IMAGE_SIZE = "Detection Image Size"
LABEL_DETECTION_IOU = "Detection IOU"
LABEL_DETECTION_WEIGHTS = "Detection Weights"
MARKER_DETECT_FILES = "marker-detect-files"
MARKER_EXPECTED_DURATION = "marker-expected-duration"
MARKER_FORCE_RELOAD_TORCH_HUB_CACHE = "marker-force-reload-torch-hub-cache"
MARKER_HALF_PRECISION = "marker-half-precision"
MARKER_DETECTION_CONFIDENCE = "marker-detect-confidence"
MARKER_DETECTION_IMAGE_SIZE = "marker-detect-image-size"
MARKER_DETECTION_IOU = "marker-detect-iou"
MARKER_DETECT_WEIGHTS = "marker-detect-weights"
MARKER_DETECT_OVERWRITE = "marker-detect-overwrite"


class OtvisionDetectForm:
    """The OTVision detect form.

    Args:
        config (NiceguiOtvisionDetectConfig): the detect config to prefill the fields.

    """

    def __init__(self, config: NiceguiOtvisionDetectConfig) -> None:
        self._files = FormFieldText(
            LABEL_FILES,
            config.paths,
            validation=VALIDATION_FILES,
            marker=MARKER_DETECT_FILES,
        )
        self._expected_duration = FormFieldInteger(
            LABEL_EXPECTED_DURATION,
            config.expected_duration,
            min_value=0,
            validation=VALIDATION_NUMBER_POSITIVE,
            marker=MARKER_EXPECTED_DURATION,
        )
        self._force_reload_torch_hub_cache = FormFieldCheckbox(
            LABEL_TORCH_HUB_CACHE_FORCE_RELOAD,
            config.force_reload_torch_hub_cache,
            marker=MARKER_FORCE_RELOAD_TORCH_HUB_CACHE,
        )
        self._half_precision = FormFieldCheckbox(
            LABEL_HALF_PRECISION,
            config.half_precision,
            marker=MARKER_HALF_PRECISION,
        )
        self._detection_confidence = FormFieldFloat(
            LABEL_DETECTION_CONFIDENCE,
            config.confidence,
            min_value=0,
            max_value=1,
            validation=VALIDATION_NUMBER_RANGE_0_1,
            marker=MARKER_DETECTION_CONFIDENCE,
        )
        self._detection_image_size = FormFieldInteger(
            LABEL_DETECTION_IMAGE_SIZE,
            config.img_size,
            min_value=0,
            validation=VALIDATION_NUMBER_POSITIVE,
            marker=MARKER_DETECTION_IMAGE_SIZE,
        )
        self._detection_iou = FormFieldFloat(
            LABEL_DETECTION_IOU,
            config.iou,
            min_value=0,
            max_value=1,
            validation=VALIDATION_NUMBER_RANGE_0_1,
            marker=MARKER_DETECTION_IOU,
        )

        self._detection_weights = FormFieldText(
            LABEL_DETECTION_WEIGHTS, config.weights, marker=MARKER_DETECT_WEIGHTS
        )
        self._overwrite = FormFieldCheckbox(
            LABEL_OVERWRITE, config.overwrite, marker=MARKER_DETECT_OVERWRITE
        )

    def build(self) -> Self:
        """Builds the ui elements for OTVision detect config form."""
        ui.label("Detect").classes("text-lg font-bold")
        self._files.build()
        self._expected_duration.build()
        self._detection_confidence.build()
        self._detection_image_size.build()
        self._detection_iou.build()
        self._detection_weights.build()
        self._force_reload_torch_hub_cache.build()
        self._half_precision.build()
        self._overwrite.build()
        return self

    def validate(self) -> bool:
        """Validate the fields in this form for invalid inputs."""
        return all(
            [
                self._files.validate(),
                self._expected_duration.validate(),
                self._detection_confidence.validate(),
                self._detection_image_size.validate(),
                self._detection_iou.validate(),
            ]
        )

    def update(self, config: NiceguiOtvisionDetectConfig) -> None:
        """Update the current fields in this form with config.

        This also refreshes the respective UI elements.

        Args:
            config (NiceguiOtvisionDetectConfig): the config to update the fields with.

        """
        self._files.set_value(config.paths)
        self._expected_duration.set_value(config.expected_duration)
        self._detection_confidence.set_value(config.confidence)
        self._detection_image_size.set_value(config.img_size)
        self._detection_iou.set_value(config.iou)
        self._detection_weights.set_value(config.weights)
        self._force_reload_torch_hub_cache.set_value(
            config.force_reload_torch_hub_cache
        )
        self._half_precision.set_value(config.half_precision)
        self._overwrite.set_value(config.overwrite)

    def get_config(self) -> NiceguiOtvisionDetectConfig:
        """Get the current OTVision detect config filled out by the user.

        Returns:
            NiceguiOtvisionDetectConfig: The current config filled out by the
                user.

        """
        return NiceguiOtvisionDetectConfig(
            paths=self._files.value,
            expected_duration=self._expected_duration.value,
            confidence=self._detection_confidence.value,
            img_size=self._detection_image_size.value,
            iou=self._detection_iou.value,
            weights=self._detection_weights.value,
            force_reload_torch_hub_cache=self._force_reload_torch_hub_cache.value,
            half_precision=self._half_precision.value,
            overwrite=self._overwrite.value,
        )
