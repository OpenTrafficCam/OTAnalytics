from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from tqdm import tqdm

from OTAnalytics.application.analysis.intersect import (
    RunIntersect,
    RunSceneEventDetection,
)
from OTAnalytics.application.datastore import EventListParser, FlowParser, TrackParser
from OTAnalytics.domain.flow import Flow
from OTAnalytics.domain.section import Section
from OTAnalytics.domain.track import Track

EVENTLIST_FILE_TYPE = "otevents"
TRACK_FILE_TYPE = "ottrk"

SECTIONS_FILE_TYPE = "otflow"


class CliParseError(Exception):
    pass


class SectionsFileDoesNotExist(Exception):
    pass


class InvalidSectionFileType(Exception):
    pass


@dataclass(frozen=True)
class CliArguments:
    start_cli: bool
    track_files: list[str]
    sections_file: str


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

    def parse(self) -> CliArguments:
        """Parse and checks for cli arg

        Returns:
            CliArguments: _description_
        """
        args = self._parser.parse_args()
        return CliArguments(args.cli, args.ottrks, args.otflow)


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
        intersect: RunIntersect,
        scene_event_detection: RunSceneEventDetection,
    ) -> None:
        self._validate_cli_args(cli_args)
        self.cli_args = cli_args

        self._track_parser = track_parser
        self._flow_parser = flow_parser
        self._event_list_parser = event_list_parser
        self._intersect = intersect
        self._scene_event_detection = scene_event_detection

    def start(self) -> None:
        """Start analysis."""
        # TODO parse config and add track and section files
        ottrk_files: set[Path] = self._get_ottrk_files(self.cli_args.track_files)
        sections_file: Path = self._get_sections_file(self.cli_args.sections_file)

        sections, flows = self._parse_flows(sections_file)

        self._run_analysis(ottrk_files, sections)

    def _parse_flows(self, flow_file: Path) -> tuple[Iterable[Section], Iterable[Flow]]:
        return self._flow_parser.parse(flow_file)

    def _parse_tracks(self, track_file: Path) -> Iterable[Track]:
        return self._track_parser.parse(track_file)

    def _run_analysis(
        self, ottrk_files: set[Path], sections: Iterable[Section]
    ) -> None:
        """Run analysis.

        Args:
            ottrk_files (list[Path]): the ottrk files to be analyzed
        """
        for ottrk_file in tqdm(ottrk_files, desc="Analyzed files", unit=" files"):
            save_path = self._determine_eventlist_save_path(ottrk_file)
            tracks = self._parse_tracks(ottrk_file)
            events = self._intersect.run(tracks, sections)
            events.extend(self._scene_event_detection.run(tracks))
            self._event_list_parser.serialize(events, sections, save_path)
            print(f"Analysis finished. Event list saved at '{save_path}'")

    @staticmethod
    def _determine_eventlist_save_path(track_file: Path) -> Path:
        """Determine save path of eventlist.

        The save path will be determined by the location of the track file.

        Args:
            track_file (Path): the track file used to determine the save path

        Returns:
            Path: the save path of the event list
        """
        return track_file.with_suffix(f".{EVENTLIST_FILE_TYPE}")

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
                files_in_directory = ottrk_file.rglob(f"*.{TRACK_FILE_TYPE}")
                ottrk_files.update(files_in_directory)
                continue

            if not ottrk_file.exists() or ottrk_file.suffix != f".{TRACK_FILE_TYPE}":
                print(f"Ottrk file'{ottrk_file}' does not exist. Skipping file.")
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
        if sections_file.suffix != f".{SECTIONS_FILE_TYPE}":
            raise InvalidSectionFileType(
                f"Sections file {sections_file} has wrong file type. "
                "Unable to run analysis."
            )

        return sections_file
