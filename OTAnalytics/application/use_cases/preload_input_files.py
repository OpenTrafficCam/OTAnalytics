from OTAnalytics.application.run_configuration import RunConfiguration
from OTAnalytics.application.use_cases.apply_cli_cuts import ApplyCliCuts
from OTAnalytics.application.use_cases.load_otflow import LoadOtflow
from OTAnalytics.application.use_cases.load_track_files import LoadTrackFiles


class PreloadInputFiles:
    def __init__(
        self,
        load_track_files: LoadTrackFiles,
        load_otflow: LoadOtflow,
        apply_cli_cuts: ApplyCliCuts,
    ):
        self._load_track_files = load_track_files
        self._load_otflow = load_otflow
        self._apply_cli_cuts = apply_cli_cuts

    def load(self, run_config: RunConfiguration) -> None:
        if run_config.otflow:
            self._load_otflow(run_config.otflow)
        if run_config.track_files:
            self._load_track_files(list(run_config.track_files))

        if run_config.sections:
            self._apply_cli_cuts.apply(
                run_config.sections, preserve_cutting_sections=True
            )
