import sys
from unittest.mock import patch

from OTAnalytics.application.config import DEFAULT_TRACK_FILE_TYPE
from OTAnalytics.application.parser.cli_parser import CliArguments, CliMode
from OTAnalytics.plugin_parser.argparse_cli_parser import ArgparseCliParser


class TestArgparseCliParser:
    def test_parse_with_valid_cli_args(self) -> None:
        track_file_1 = f"track_file_1.{DEFAULT_TRACK_FILE_TYPE}"
        track_file_2 = f"track_file_2.{DEFAULT_TRACK_FILE_TYPE}"
        sections_file = "section_file.otflow"
        save_name = "stem"
        save_suffix = "suffix"
        log_file = "path/to/my_log.log"
        csv_format = "csv"
        otevents_format = "otevents"
        config_file = "path/to/config.otconfig"

        cli_args: list[str] = [
            "path",
            "--cli",
            "--cli-mode",
            "bulk",
            "--cli-chunk-size",
            "5",
            "--config",
            config_file,
            "--ottrks",
            track_file_1,
            track_file_2,
            "--otflow",
            sections_file,
            "--save-name",
            save_name,
            "--save-suffix",
            save_suffix,
            "--event-format",
            csv_format,
            otevents_format,
            "--count-intervals",
            "1",
            "15",
            "--num-processes",
            "3",
            "--no-track-statistics-export",
            "--logfile",
            log_file,
            "--logfile_overwrite",
            "--include-classes",
            "truck",
            "car",
            "--exclude-classes",
            "pedestrian",
        ]
        with patch.object(sys, "argv", cli_args):
            parser = ArgparseCliParser()
            args = parser.parse()
            assert args == CliArguments(
                start_cli=True,
                cli_mode=CliMode.BULK,
                cli_chunk_size=5,
                debug=False,
                logfile_overwrite=True,
                track_export=True,
                track_statistics_export=False,
                config_file=config_file,
                track_files=[track_file_1, track_file_2],
                otflow_file=sections_file,
                save_dir=None,
                save_name=save_name,
                save_suffix=save_suffix,
                event_formats=[csv_format, otevents_format],
                count_intervals=[1, 15],
                num_processes=3,
                log_file=log_file,
                include_classes=["truck", "car"],
                exclude_classes=["pedestrian"],
            )
