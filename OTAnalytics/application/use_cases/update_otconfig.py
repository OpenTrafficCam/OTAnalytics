from pathlib import Path

from OTAnalytics.application.parser.cli_parser import CliArguments
from OTAnalytics.application.parser.config_parser import (
    AnalysisConfig,
    ExportConfig,
    OtConfig,
)


class OtConfigUpdater:
    def with_cli_args(self, otconfig: OtConfig, cli_args: CliArguments) -> OtConfig:
        return OtConfig(
            project=otconfig.project,
            analysis=AnalysisConfig(
                do_events=otconfig.analysis.do_events,
                do_counting=otconfig.analysis.do_counting,
                track_files={Path(_track) for _track in cli_args.track_files},
                export_config=ExportConfig(
                    save_name=cli_args.save_name,
                    save_suffix=cli_args.save_suffix,
                    event_formats={cli_args.event_list_format},
                    count_intervals={cli_args.count_interval},
                ),
                num_processes=cli_args.num_processes,
                logfile=Path(cli_args.log_file),
                debug=cli_args.debug,
            ),
            videos=otconfig.videos,
            sections=otconfig.sections,
            flows=otconfig.flows,
        )
