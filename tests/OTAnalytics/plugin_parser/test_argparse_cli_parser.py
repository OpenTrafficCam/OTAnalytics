import sys
from unittest.mock import patch

from OTAnalytics.application.config import DEFAULT_TRACK_FILE_TYPE
from OTAnalytics.application.parser.cli_parser import CliArguments
from OTAnalytics.plugin_parser.argparse_cli_parser import ArgparseCliParser
from OTAnalytics.plugin_prototypes.eventlist_exporter.eventlist_exporter import (
    AVAILABLE_EVENTLIST_EXPORTERS,
    OTC_CSV_FORMAT_NAME,
)
from OTAnalytics.plugin_ui.cli import EventFormat


class TestArgparseCliParser:
    def test_parse_with_valid_cli_args(self) -> None:
        track_file_1 = f"track_file_1.{DEFAULT_TRACK_FILE_TYPE}"
        track_file_2 = f"track_file_2.{DEFAULT_TRACK_FILE_TYPE}"
        sections_file = "section_file.otflow"
        save_name = "stem"
        save_suffix = "suffix"
        log_file = "path/to/my_log.log"

        cli_args: list[str] = [
            "path",
            "--cli",
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
            EventFormat.CSV.value,
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
                [track_file_1, track_file_2],
                sections_file,
                save_name,
                save_suffix,
                AVAILABLE_EVENTLIST_EXPORTERS[OTC_CSV_FORMAT_NAME],
                15,
                3,
                log_file,
                True,
            )
