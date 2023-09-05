from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from OTAnalytics.application.analysis.traffic_counting import ExportCounts
from OTAnalytics.application.analysis.traffic_counting_specification import (
    CountingSpecificationDto,
)
from OTAnalytics.application.config import (
    DEFAULT_COUNTING_INTERVAL_IN_MINUTES,
    DEFAULT_COUNTS_FILE_STEM,
    DEFAULT_COUNTS_FILE_TYPE,
    DEFAULT_EVENTLIST_FILE_STEM,
    DEFAULT_EVENTLIST_FILE_TYPE,
    DEFAULT_SECTIONS_FILE_TYPE,
    DEFAULT_TRACK_FILE_TYPE,
)
from OTAnalytics.application.datastore import EventListParser, FlowParser, TrackParser
from OTAnalytics.application.logger import logger
from OTAnalytics.application.state import TracksMetadata
from OTAnalytics.application.use_cases.create_events import CreateEvents
from OTAnalytics.application.use_cases.flow_repository import AddFlow
from OTAnalytics.application.use_cases.section_repository import AddSection
from OTAnalytics.application.use_cases.track_repository import (
    AddAllTracks,
    ClearAllTracks,
    GetAllTrackIds,
)
from OTAnalytics.domain.event import EventRepository
from OTAnalytics.domain.flow import Flow
from OTAnalytics.domain.progress import ProgressbarBuilder
from OTAnalytics.domain.section import Section


class CliParseError(Exception):
    pass


class SectionsFileDoesNotExist(Exception):
    pass


class InvalidSectionFileType(Exception):
    pass


@dataclass(frozen=True)
class CliArguments:
    start_cli: bool
    debug: bool
    track_files: list[str]
    sections_file: str
    eventlist_filename: str


class CliArgumentParser:
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
            "--debug",
            action="store_true",
            help="Set log level to DEBUG.",
            required=False,
        )

    def parse(self) -> CliArguments:
        """Parse and checks for cli arg

        Returns:
            CliArguments: _description_
        """
        args = self._parser.parse_args()
        return CliArguments(
            args.cli, args.debug, args.ottrks, args.otflow, args.save_name
        )


class OTAnalyticsCli:
    """The OTAnalytics command line interface.

    Args:
        application (OTAnalyticsApplication): the entry point to OTAnalytics application
        cli_args (CliArguments): the command line argument passed
    """

    def __init__(
        self,
        cli_args: CliArguments,
        track_parser: TrackParser,
        flow_parser: FlowParser,
        event_list_parser: EventListParser,
        event_repository: EventRepository,
        add_section: AddSection,
        add_flow: AddFlow,
        create_events: CreateEvents,
        export_counts: ExportCounts,
        add_all_tracks: AddAllTracks,
        get_all_track_ids: GetAllTrackIds,
        clear_all_tracks: ClearAllTracks,
        progressbar: ProgressbarBuilder,
    ) -> None:
        self._validate_cli_args(cli_args)
        self.cli_args = cli_args

        self._track_parser = track_parser
        self._flow_parser = flow_parser
        self._event_list_parser = event_list_parser
        self._event_repository = event_repository
        self._add_section = add_section
        self._add_flow = add_flow
        self._create_events = create_events
        self._export_counts = export_counts
        self._add_all_tracks = add_all_tracks
        self._get_all_track_ids = get_all_track_ids
        self._clear_all_tracks = clear_all_tracks
        self._progressbar = progressbar

    def start(self) -> None:
        """Start analysis."""
        # TODO parse config and add track and section files
        ottrk_files: set[Path] = self._get_ottrk_files(self.cli_args.track_files)
        sections_file: Path = self._get_sections_file(self.cli_args.sections_file)

        sections, flows = self._parse_flows(sections_file)

        self._run_analysis(ottrk_files, sections, flows)

    def _parse_flows(self, flow_file: Path) -> tuple[Iterable[Section], Iterable[Flow]]:
        return self._flow_parser.parse(flow_file)

    def _add_sections(self, sections: Iterable[Section]) -> None:
        """Add sections to section repository."""
        for section in sections:
            self._add_section.add(section)

    def _add_flows(self, flows: Iterable[Flow]) -> None:
        """Add flows to flow repository."""
        for flow in flows:
            self._add_flow.add(flow)

    def _parse_tracks(self, track_files: list[Path]) -> None:
        for track_file in self._progressbar(track_files, "Parsed track files", "files"):
            tracks = self._track_parser.parse(track_file)
            self._add_all_tracks(tracks)

    def _run_analysis(
        self, ottrk_files: set[Path], sections: Iterable[Section], flows: Iterable[Flow]
    ) -> None:
        """Run analysis."""
        self._clear_all_tracks()
        self._event_repository.clear()
        self._add_sections(sections)
        self._add_flows(flows)
        ottrk_files_sorted: list[Path] = sorted(
            ottrk_files, key=lambda file: str(file).lower()
        )
        self._parse_tracks(ottrk_files_sorted)

        logger().info("Create event list ...")
        self._create_events()
        logger().info("Event list created.")

        event_list_output_file = self._determine_eventlist_save_path(
            ottrk_files_sorted[0]
        )
        self._event_list_parser.serialize(
            self._event_repository.get_all(), sections, event_list_output_file
        )
        logger().info(f"Event list saved at '{event_list_output_file}'")

        self._do_export_counts(event_list_output_file)

    def _determine_eventlist_save_path(self, track_file: Path) -> Path:
        """Determine save path of eventlist.

        The save path will be the parent directory of the track file.
        The eventlist file name will be either name passed via CLI or the
        `DEFAULT_EVENTLIST_FILENAME`.

        Args:
            track_file (Path): the track file used to determine the save path.

        Returns:
            Path: the save path of the event list.
        """
        eventlist_file_name = self.cli_args.eventlist_filename
        if eventlist_file_name == "":
            return track_file.with_name(
                f"{DEFAULT_EVENTLIST_FILE_STEM}.{DEFAULT_EVENTLIST_FILE_TYPE}"
            )

        return track_file.with_name(
            f"{self.cli_args.eventlist_filename}.{DEFAULT_EVENTLIST_FILE_TYPE}"
        )

    @staticmethod
    def _validate_cli_args(args: CliArguments) -> None:
        """Validates the command line arguments passed.

        Args:
            args (Namespace): the arguments to be validated

        Raises:
            CliParseError: if no track file has been passed
            CliParseError: if no otflow file has been passed
        """

        if not args.track_files:
            raise CliParseError("No ottrk files passed. Abort analysis.")

        if not args.sections_file:
            raise CliParseError("No otflow file passed. Abort analysis.")

    @staticmethod
    def _get_ottrk_files(files: list[str]) -> set[Path]:
        """Parse ottrk files.

        Files that do not exist will be skipped.

        Args:
            files (list[str]): ottrk files to be parsed

        Returns:
            list[Path]: the ottrk files.
        """
        ottrk_files: set[Path] = set()
        for file in files:
            ottrk_file = Path(file)
            if ottrk_file.is_dir():
                files_in_directory = ottrk_file.rglob(f"*.{DEFAULT_TRACK_FILE_TYPE}")
                ottrk_files.update(files_in_directory)
                continue

            if (
                not ottrk_file.exists()
                or ottrk_file.suffix != f".{DEFAULT_TRACK_FILE_TYPE}"
            ):
                logger().warning(
                    f"Ottrk file'{ottrk_file}' does not exist. Skipping file."
                )
                continue

            ottrk_files.add(ottrk_file)
        return ottrk_files

    @staticmethod
    def _get_sections_file(file: str) -> Path:
        """Parse sections file.

        Args:
            file (str): the sections file to be parsed

        Raises:
            SectionFileDoesNotExist: if sections file does not exist

        Returns:
            Path: the sections file.
        """
        sections_file = Path(file)
        if not sections_file.exists():
            raise SectionsFileDoesNotExist(
                f"Sections file '{sections_file}' does not exist. "
                "Unable to run analysis."
            )
        if sections_file.suffix != f".{DEFAULT_SECTIONS_FILE_TYPE}":
            raise InvalidSectionFileType(
                f"Sections file {sections_file} has wrong file type. "
                "Unable to run analysis."
            )

        return sections_file

    def _do_export_counts(self, event_list_output_file: Path) -> None:
        logger().info("Create counts ...")
        tracks_metadata = TracksMetadata(self._add_all_tracks._track_repository)
        tracks_metadata.notify_tracks(list(self._get_all_track_ids()))
        start = tracks_metadata.first_detection_occurrence
        end = tracks_metadata.last_detection_occurrence
        modes = tracks_metadata.classifications
        if start is None:
            raise ValueError("start is None but has to be defined for exporting counts")
        if end is None:
            raise ValueError("end is None but has to be defined for exporting counts")
        if modes is None:
            raise ValueError("modes is None but has to be defined for exporting counts")
        interval: int = DEFAULT_COUNTING_INTERVAL_IN_MINUTES
        if event_list_output_file.stem == DEFAULT_EVENTLIST_FILE_STEM:
            output_file_stem = DEFAULT_COUNTS_FILE_STEM
        else:
            output_file_stem = (
                f"{event_list_output_file.stem}_{DEFAULT_COUNTS_FILE_STEM}"
            )
        output_file = event_list_output_file.with_stem(output_file_stem).with_suffix(
            f".{DEFAULT_COUNTS_FILE_TYPE}"
        )
        counting_specification = CountingSpecificationDto(
            start=start,
            end=end,
            modes=list(modes),
            interval_in_minutes=interval,
            output_file=str(output_file),
            output_format="CSV",
        )
        self._export_counts.export(specification=counting_specification)
        logger().info(f"Counts saved at {output_file}")
