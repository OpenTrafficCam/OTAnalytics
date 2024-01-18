import sys
from unittest.mock import patch

from OTAnalytics.application.config import DEFAULT_TRACK_FILE_TYPE
from OTAnalytics.application.parser.cli_parser import CliArguments
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
            "--count-interval",
            "15",
            "--num-processes",
            "3",
            "--logfile",
            log_file,
            "--logfile_overwrite",
        ]
        with patch.object(sys, "argv", cli_args):
            parser = ArgparseCliParser()
            args = parser.parse()
            assert args == CliArguments(
                True,
                False,
                True,
                config_file,
                [track_file_1, track_file_2],
                sections_file,
                None,
                save_name,
                save_suffix,
                [csv_format, otevents_format],
                15,
                3,
                log_file,
            )
