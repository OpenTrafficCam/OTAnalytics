from pathlib import Path
from unittest.mock import Mock

import pytest

from OTAnalytics.application.parser.cli_parser import CliArguments
from OTAnalytics.application.parser.config_parser import (
    AnalysisConfig,
    ExportConfig,
    OtConfig,
)
from OTAnalytics.application.use_cases.update_otconfig import OtConfigUpdater


@pytest.fixture
def cli_args() -> CliArguments:
    cli_track_files = [
        "path/to/first_track_cli.ottrk",
        "path/to/second_track_cli.ottrk",
    ]
    cli_otflow_file = "path/to/cli_otflow.otflow"
    return CliArguments(
        start_cli=True,
        debug=True,
        track_files=cli_track_files,
        sections_file=cli_otflow_file,
        save_name="cli_save_name",
        save_suffix="cli_save_suffix",
        event_list_format="csv",
        count_interval=6,
        num_processes=8,
        log_file="path/to/cli_log",
        logfile_overwrite=True,
    )


@pytest.fixture
def otconfig() -> OtConfig:
    export = ExportConfig(
        save_name="config_save_name",
        save_suffix="config_save_suffix",
        event_formats={"csv", "otevents"},
        count_intervals={2, 3},
    )

    track_files = {
        Path("path/to/first_track_config.ottrk"),
        Path("path/to/second_track_config.ottrk"),
    }
    analysis = AnalysisConfig(
        do_events=True,
        do_counting=True,
        track_files=track_files,
        export_config=export,
        num_processes=2,
        logfile=Path("path/to/config_log"),
        debug=False,
    )
    return OtConfig(
        project=Mock(),
        analysis=analysis,
        videos=Mock(),
        sections=Mock(),
        flows=Mock(),
    )


class TestOtConfigUpdater:
    def test_update(self, cli_args: CliArguments, otconfig: OtConfig) -> None:
        otconfig_updater = OtConfigUpdater()
        result = otconfig_updater.with_cli_args(otconfig, cli_args)

        assert result == OtConfig(
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
