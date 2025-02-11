from typing import Self

from nicegui import ui
from OTCloud.adapter.nicegui_mapping.otvision_mapper import NiceguiOtvisionConfig
from OTCloud.plugin_webserver.nicegui.constants import Alignment
from OTCloud.plugin_webserver.nicegui.elements.forms import FormFieldCheckbox
from OTCloud.plugin_webserver.pages.create_job_config.otvision.convert import (
    OtvisionConvertForm,
)
from OTCloud.plugin_webserver.pages.create_job_config.otvision.detect import (
    OtvisionDetectForm,
)
from OTCloud.plugin_webserver.pages.create_job_config.otvision.track import (
    OtvisionTrackForm,
)

LABEL_RUN_CONVERT = "Run Convert"
LABEL_RUN_DETECT = "Run Detect"
LABEL_RUN_TRACK = "Run Track"
LABEL_OTVISION_SETTINGS = "OTVision Settings"
MARKER_RUN_CONVERT = "marker-run-convert"
MARKER_RUN_DETECT = "marker-run-detect"
MARKER_RUN_TRACK = "marker-run-track"


class OtvisionConfigSettings:
    """The OTVision config settings.

    Responsible to build OTVision convert, detect, and track form.

    Args:
        config (NiceguiOtvisionTrackConfig): the track config to prefill the fields.

    """

    def __init__(self, config: NiceguiOtvisionConfig) -> None:
        self._run_convert = FormFieldCheckbox(
            label_text=LABEL_RUN_CONVERT,
            initial_value=config.run_convert,
            marker=MARKER_RUN_CONVERT,
        )
        self._run_detect = FormFieldCheckbox(
            label_text=LABEL_RUN_DETECT,
            initial_value=config.run_detect,
            marker=MARKER_RUN_DETECT,
        )
        self._run_track = FormFieldCheckbox(
            label_text=LABEL_RUN_TRACK,
            initial_value=config.run_track,
            marker=MARKER_RUN_TRACK,
        )
        self._convert_form = OtvisionConvertForm(config.convert)
        self._detect_form = OtvisionDetectForm(config.detect)
        self._track_form = OtvisionTrackForm(config.track)

    def build(self) -> Self:
        """Builds the ui elements for OTVision config settings form."""
        with ui.card(align_items=Alignment.stretch):
            ui.label(LABEL_OTVISION_SETTINGS).classes("text-xl font-bold")
            with ui.row():
                with ui.column():
                    self._run_convert.build()
                    with ui.card(align_items=Alignment.stretch) as card_convert:
                        card_convert.bind_visibility_from(self._run_convert, "value")
                        self._convert_form.build()
                with ui.column():
                    self._run_detect.build()
                    with ui.card(align_items=Alignment.stretch) as card_detect:
                        card_detect.bind_visibility_from(self._run_detect, "value")
                        self._detect_form.build()
                with ui.column():
                    self._run_track.build()
                    with ui.card(align_items=Alignment.stretch) as card_track:
                        card_track.bind_visibility_from(self._run_track, "value")
                        self._track_form.build()
        return self

    def update(self, config: NiceguiOtvisionConfig) -> None:
        """Update the current fields in this form with config.

        This also refreshes the respective UI elements.

        Args:
            config (NiceguiOtvisionConfig): the config to update the fields with.

        """
        self._run_convert.set_value(config.run_convert)
        self._run_detect.set_value(config.run_detect)
        self._run_track.set_value(config.run_track)
        self._convert_form.update(config.convert)
        self._detect_form.update(config.detect)
        self._track_form.update(config.track)

    def validate(self) -> bool:
        """Validate the fields in this form for invalid inputs.

        Returns:
            bool: True if the form fields are valid, False otherwise.

        """
        return all(
            [
                not self._run_convert.value or self._convert_form.validate(),
                not self._run_detect.value or self._detect_form.validate(),
                not self._run_track.value or self._track_form.validate(),
            ]
        )

    def get_config(self) -> NiceguiOtvisionConfig:
        """Get the current OTVision config settings filled out by the user.

        Returns:
            NiceguiOtvisionConfig: The current config filled out by the
                user.

        """
        return NiceguiOtvisionConfig(
            run_convert=self._run_convert.value,
            run_detect=self._run_detect.value,
            run_track=self._run_track.value,
            convert=self._convert_form.get_config(),
            detect=self._detect_form.get_config(),
            track=self._track_form.get_config(),
        )
