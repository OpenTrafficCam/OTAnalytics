from OTAnalytics.application.parser.config_parser import AnalysisConfig
from OTAnalytics.application.state import CurrentStaticAnalysisConfigState
from OTAnalytics.application.use_cases.track_repository import GetAllTrackFiles


class GetCurrentAnalysisConfig:
    """Provide the analysis configuration currently held by the application.

    Args:
        static_analysis_config_state (CurrentStaticAnalysisConfigState): the state
            holding the analysis settings that are not derived from repositories.
        get_all_track_files (GetAllTrackFiles): use case to retrieve all track files.
    """

    def __init__(
        self,
        static_analysis_config_state: CurrentStaticAnalysisConfigState,
        get_all_track_files: GetAllTrackFiles,
    ) -> None:
        self._static_analysis_config_state = static_analysis_config_state
        self._get_all_track_files = get_all_track_files

    def get(self) -> AnalysisConfig:
        """Get the current analysis configuration.

        Returns:
            AnalysisConfig: The current analysis configuration.
        """
        return AnalysisConfig(
            do_events=self._static_analysis_config_state.do_events,
            do_counting=self._static_analysis_config_state.do_counting,
            track_files=self._get_all_track_files(),
            export_config=self._static_analysis_config_state.export_config.get(),
            num_processes=self._static_analysis_config_state.num_processes,
            logfile=self._static_analysis_config_state.logfile,
        )
