from argparse import ArgumentParser
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Iterable

from OTAnalytics.application.analysis.traffic_counting import ExportCounts
from OTAnalytics.application.analysis.traffic_counting_specification import (
    CountingSpecificationDto,
)
from OTAnalytics.application.config import (
    CLI_CUTTING_SECTION_MARKER,
    DEFAULT_COUNTING_INTERVAL_IN_MINUTES,
    DEFAULT_COUNTS_FILE_STEM,
    DEFAULT_COUNTS_FILE_TYPE,
    DEFAULT_NUM_PROCESSES,
    DEFAULT_SECTIONS_FILE_TYPE,
    DEFAULT_TRACK_FILE_TYPE,
)
from OTAnalytics.application.datastore import FlowParser, TrackParser
from OTAnalytics.application.logger import DEFAULT_LOG_FILE, logger
from OTAnalytics.application.state import TracksMetadata, VideosMetadata
from OTAnalytics.application.use_cases.create_events import CreateEvents
from OTAnalytics.application.use_cases.cut_tracks_with_sections import (
    CutTracksIntersectingSection,
)
from OTAnalytics.application.use_cases.export_events import EventListExporter
from OTAnalytics.application.use_cases.flow_repository import AddFlow
from OTAnalytics.application.use_cases.section_repository import (
    AddSection,
    GetAllSections,
)
from OTAnalytics.application.use_cases.track_repository import (
    AddAllTracks,
    ClearAllTracks,
    GetAllTrackIds,
)
from OTAnalytics.domain.event import EventRepository
from OTAnalytics.domain.flow import Flow
from OTAnalytics.domain.progress import ProgressbarBuilder
from OTAnalytics.domain.section import Section, SectionType
from OTAnalytics.domain.track_repository import TrackRepositoryEvent
from OTAnalytics.plugin_prototypes.eventlist_exporter.eventlist_exporter import (
    AVAILABLE_EVENTLIST_EXPORTERS,
    OTC_CSV_FORMAT_NAME,
    OTC_EXCEL_FORMAT_NAME,
    OTC_OTEVENTS_FORMAT_NAME,
)


class EventFormat(Enum):
    CSV: str = "csv"
    EXCEL: str = "xlsx"
    OTEVENTS: str = "otevents"


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
    save_name: str
    save_suffix: str
    event_list_exporter: EventListExporter
    count_interval: int
    num_processes: int
    log_file: str
    logfile_overwrite: bool


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


class OTAnalyticsCli:
    """The OTAnalytics command line interface.

    Args:
        cli_args (CliArguments): the command line argument passed
    """

    def __init__(
        self,
        cli_args: CliArguments,
        track_parser: TrackParser,
        flow_parser: FlowParser,
        event_repository: EventRepository,
        add_section: AddSection,
        get_all_sections: GetAllSections,
        add_flow: AddFlow,
        create_events: CreateEvents,
        export_counts: ExportCounts,
        cut_tracks: CutTracksIntersectingSection,
        add_all_tracks: AddAllTracks,
        get_all_track_ids: GetAllTrackIds,
        clear_all_tracks: ClearAllTracks,
        tracks_metadata: TracksMetadata,
        videos_metadata: VideosMetadata,
        progressbar: ProgressbarBuilder,
    ) -> None:
        self._validate_cli_args(cli_args)
        self.cli_args = cli_args

        self._track_parser = track_parser
        self._flow_parser = flow_parser
        self._event_repository = event_repository
        self._add_section = add_section
        self._get_all_sections = get_all_sections
        self._add_flow = add_flow
        self._create_events = create_events
        self._export_counts = export_counts
        self._cut_tracks = cut_tracks
        self._add_all_tracks = add_all_tracks
        self._get_all_track_ids = get_all_track_ids
        self._clear_all_tracks = clear_all_tracks
        self._tracks_metadata = tracks_metadata
        self._videos_metadata = videos_metadata
        self._progressbar = progressbar

    def start(self) -> None:
        """Start analysis."""
        # TODO parse config and add track and section files
        try:
            ottrk_files: set[Path] = self._get_ottrk_files(self.cli_args.track_files)
            sections_file: Path = self._get_sections_file(self.cli_args.sections_file)

            sections, flows = self._parse_flows(sections_file)

            self._run_analysis(ottrk_files, sections, flows)
        except Exception as cause:
            logger().exception(cause, exc_info=True)

    def _parse_flows(self, flow_file: Path) -> tuple[Iterable[Section], Iterable[Flow]]:
        return self._flow_parser.parse(flow_file)

    def _add_sections(self, sections: Iterable[Section]) -> None:
        """Add sections to section repository."""
        for section in sections:
            self._add_section(section)

    def _add_flows(self, flows: Iterable[Flow]) -> None:
        """Add flows to flow repository."""
        for flow in flows:
            self._add_flow(flow)

    def _parse_tracks(self, track_files: list[Path]) -> None:
        for track_file in self._progressbar(track_files, "Parsed track files", "files"):
            parse_result = self._track_parser.parse(track_file)
            self._add_all_tracks(parse_result.tracks)
            self._tracks_metadata.update_detection_classes(
                parse_result.detection_metadata.detection_classes
            )
            self._videos_metadata.update(parse_result.video_metadata)

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
        self._apply_cuts(self._get_all_sections())

        logger().info("Create event list ...")
        self._create_events()
        logger().info("Event list created.")

        save_path = self._create_save_path()
        self._export_events(sections, save_path)
        self._do_export_counts(save_path)

    def _apply_cuts(self, sections: Iterable[Section]) -> None:
        cutting_sections = sorted(
            [
                section
                for section in sections
                if section.get_type() == SectionType.CUTTING
                or section.name.startswith(CLI_CUTTING_SECTION_MARKER)
            ],
            key=lambda section: section.id.id,
        )
        logger().info("Cut tracks with cutting sections...")
        for cutting_section in cutting_sections:
            logger().info(
                f"Cut tracks with cutting section '{cutting_section.name}'..."
            )
            self._cut_tracks(cutting_section)
        logger().info("Finished cutting all tracks")

    def _create_save_path(self) -> Path:
        """Create save path for files [Events, Counts].

        The save path will be the parent directory of the section file.

        Returns:
            Path: the save path.
        """
        otflow = Path(self.cli_args.sections_file)
        cli_args = self.cli_args

        save_stem = cli_args.save_name if cli_args.save_name else otflow.stem
        save_suffix = f"_{cli_args.save_suffix}" if cli_args.save_suffix else ""

        if not self.cli_args.save_name:
            # No save name specified. Take otflow name as stem for save path.
            return otflow.with_name(save_stem + save_suffix)

        # Save name is either absolute or relative path.
        save_path = Path(self.cli_args.save_name).expanduser()
        return save_path.with_name(save_path.stem + save_suffix)

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
            ottrk_file = Path(file).expanduser()
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
        sections_file = Path(file).expanduser()
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

    def _export_events(self, sections: Iterable[Section], save_path: Path) -> None:
        events = self._event_repository.get_all()
        event_list_exporter = self.cli_args.event_list_exporter
        actual_save_path = save_path.with_suffix(
            f".events.{event_list_exporter.get_extension()}"
        )
        event_list_exporter.export(events, sections, actual_save_path)
        logger().info(f"Event list saved at '{actual_save_path}'")

    def _do_export_counts(self, save_path: Path) -> None:
        logger().info("Create counts ...")
        self._tracks_metadata.notify_tracks(
            TrackRepositoryEvent(list(self._get_all_track_ids()), [])
        )
        start = self._videos_metadata.first_video_start
        end = self._videos_metadata.last_video_end
        modes = self._tracks_metadata.detection_classifications
        if start is None:
            raise ValueError("start is None but has to be defined for exporting counts")
        if end is None:
            raise ValueError("end is None but has to be defined for exporting counts")
        if modes is None:
            raise ValueError("modes is None but has to be defined for exporting counts")
        output_file = save_path.with_suffix(
            f".{DEFAULT_COUNTS_FILE_STEM}.{DEFAULT_COUNTS_FILE_TYPE}"
        )
        counting_specification = CountingSpecificationDto(
            start=start,
            end=end,
            modes=list(modes),
            interval_in_minutes=self.cli_args.count_interval,
            output_file=str(output_file),
            output_format="CSV",
        )
        self._export_counts.export(specification=counting_specification)
        logger().info(f"Counts saved at {output_file}")
