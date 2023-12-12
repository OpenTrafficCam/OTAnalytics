from argparse import ArgumentParser

from OTAnalytics.application.config import (
    DEFAULT_COUNTING_INTERVAL_IN_MINUTES,
    DEFAULT_NUM_PROCESSES,
)
from OTAnalytics.application.logger import DEFAULT_LOG_FILE
from OTAnalytics.application.parser.cli_parser import CliArguments, CliParser
from OTAnalytics.application.use_cases.export_events import EventListExporter
from OTAnalytics.plugin_prototypes.eventlist_exporter.eventlist_exporter import (
    AVAILABLE_EVENTLIST_EXPORTERS,
    OTC_CSV_FORMAT_NAME,
    OTC_EXCEL_FORMAT_NAME,
    OTC_OTEVENTS_FORMAT_NAME,
)
from OTAnalytics.plugin_ui.cli import EventFormat


class ArgparseCliParser(CliParser):
    """OTAnalytics command line interface argument parser.

    Acts as a wrapper to `argparse.ArgumentParser`.

    Args:
        arg_parser (ArgumentParser, optional): the argument parser.
            Defaults to ArgumentParser("OTAnalytics CLI").
    """

    def __init__(
        self, arg_parser: ArgumentParser = ArgumentParser("OTAnalytics CLI")
    ) -> None:
        self._parser = arg_parser
        self._setup()

    def _setup(self) -> None:
        """Sets up the argument parser by defining the command line arguments."""
        self._parser.add_argument(
            "--cli",
            action="store_true",
            help="Start OTAnalytics CLI. If ommitted OTAnalytics GUI will be started.",
            required=False,
        )
        self._parser.add_argument(
            "--ottrks",
            nargs="+",
            type=str,
            help="Paths of ottrk files containing tracks.",
            required=False,
        )
        self._parser.add_argument(
            "--otflow",
            type=str,
            help="Otflow file containing sections.",
            required=False,
        )
        self._parser.add_argument(
            "--save-name",
            default="",
            type=str,
            help="Name of the otevents file.",
            required=False,
        )
        self._parser.add_argument(
            "--save-suffix",
            default="",
            type=str,
            help="Name of the suffix to be appended to save name.",
            required=False,
        )
        self._parser.add_argument(
            "--debug",
            action="store_true",
            help="Set log level to DEBUG.",
            required=False,
        )
        self._parser.add_argument(
            "--event-format",
            default=EventFormat.OTEVENTS.value,
            type=str,
            help=(
                "Format to export the event list "
                "('otevents' (default), 'csv', 'xlsx')."
            ),
            required=False,
        )
        self._parser.add_argument(
            "--count-interval",
            default=DEFAULT_COUNTING_INTERVAL_IN_MINUTES,
            type=int,
            help="Count interval in minutes.",
            required=False,
        )
        self._parser.add_argument(
            "--num-processes",
            default=DEFAULT_NUM_PROCESSES,
            type=int,
            help="Number of processes to use in multi-processing.",
            required=False,
        )
        self._parser.add_argument(
            "--logfile",
            default=DEFAULT_LOG_FILE,
            type=str,
            help="Specify log file directory.",
            required=False,
        )
        self._parser.add_argument(
            "--logfile_overwrite",
            action="store_true",
            help="Overwrite log file if it already exists.",
            required=False,
        )

    def parse(self) -> CliArguments:
        """Parse and checks for cli arg

        Returns:
            CliArguments: _description_
        """
        args = self._parser.parse_args()
        return CliArguments(
            args.cli,
            args.debug,
            args.ottrks,
            args.otflow,
            args.save_name,
            args.save_suffix,
            self._parse_event_format(args.event_format),
            args.count_interval,
            args.num_processes,
            args.logfile,
            args.logfile_overwrite,
        )

    def _parse_event_format(self, event_format: str) -> EventListExporter:
        match event_format.lower():
            case EventFormat.CSV.value:
                return AVAILABLE_EVENTLIST_EXPORTERS[OTC_CSV_FORMAT_NAME]
            case EventFormat.EXCEL.value:
                return AVAILABLE_EVENTLIST_EXPORTERS[OTC_EXCEL_FORMAT_NAME]
            case _:
                return AVAILABLE_EVENTLIST_EXPORTERS[OTC_OTEVENTS_FORMAT_NAME]
