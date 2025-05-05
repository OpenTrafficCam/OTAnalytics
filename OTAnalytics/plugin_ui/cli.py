from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable

from more_itertools import peekable

from OTAnalytics.application.analysis.traffic_counting import ExportCounts, ExportMode
from OTAnalytics.application.analysis.traffic_counting_specification import (
    CountingSpecificationDto,
)
from OTAnalytics.application.config import (
    CONTEXT_FILE_TYPE_COUNTS,
    CONTEXT_FILE_TYPE_ROAD_USER_ASSIGNMENTS,
    CONTEXT_FILE_TYPE_TRACK_STATISTICS,
    DEFAULT_COUNT_INTERVAL_TIME_UNIT,
    DEFAULT_COUNTS_FILE_TYPE,
    DEFAULT_SECTIONS_FILE_TYPE,
    DEFAULT_TRACK_FILE_TYPE,
)
from OTAnalytics.application.datastore import TrackParser
from OTAnalytics.application.logger import logger
from OTAnalytics.application.parser.cli_parser import CliParseError
from OTAnalytics.application.run_configuration import RunConfiguration
from OTAnalytics.application.state import TracksMetadata, VideosMetadata
from OTAnalytics.application.use_cases.apply_cli_cuts import ApplyCliCuts
from OTAnalytics.application.use_cases.create_events import CreateEvents
from OTAnalytics.application.use_cases.export_events import (
    EventExportSpecification,
    EventListExporterProvider,
)
from OTAnalytics.application.use_cases.flow_repository import AddFlow
from OTAnalytics.application.use_cases.road_user_assignment_export import (
    ExportRoadUserAssignments,
    ExportSpecification,
)
from OTAnalytics.application.use_cases.section_repository import (
    AddSection,
    GetAllSections,
)
from OTAnalytics.application.use_cases.track_export import (
    ExportTracks,
    TrackExportSpecification,
    TrackFileFormat,
)
from OTAnalytics.application.use_cases.track_repository import (
    AddAllTracks,
    ClearAllTracks,
    GetAllTrackIds,
)
from OTAnalytics.application.use_cases.track_statistics_export import (
    ExportTrackStatistics,
    TrackStatisticsExportSpecification,
)
from OTAnalytics.domain.event import EventRepository
from OTAnalytics.domain.flow import Flow
from OTAnalytics.domain.progress import ProgressbarBuilder
from OTAnalytics.domain.section import Section
from OTAnalytics.domain.track_dataset.track_dataset import TrackDataset
from OTAnalytics.domain.track_repository import TrackRepositoryEvent
from OTAnalytics.plugin_parser.road_user_assignment_export import CSV_FORMAT
from OTAnalytics.plugin_parser.streaming_parser import StreamTrackParser


class SectionsFileDoesNotExist(Exception):
    pass


class InvalidSectionFileType(Exception):
    pass


class OTAnalyticsCli(ABC):
    """The OTAnalytics command line interface."""

    def __init__(
        self,
        run_config: RunConfiguration,
        event_repository: EventRepository,
        add_section: AddSection,
        get_all_sections: GetAllSections,
        add_flow: AddFlow,
        create_events: CreateEvents,
        export_counts: ExportCounts,
        provide_eventlist_exporter: EventListExporterProvider,
        apply_cli_cuts: ApplyCliCuts,
        add_all_tracks: AddAllTracks,
        get_all_track_ids: GetAllTrackIds,
        clear_all_tracks: ClearAllTracks,
        tracks_metadata: TracksMetadata,
        videos_metadata: VideosMetadata,
        export_tracks: ExportTracks,
        export_road_user_assignments: ExportRoadUserAssignments,
        export_track_statistics: ExportTrackStatistics,
    ) -> None:
        self._validate_cli_args(run_config)
        self._run_config = run_config

        self._event_repository = event_repository
        self._add_section = add_section
        self._get_all_sections = get_all_sections
        self._add_flow = add_flow
        self._create_events = create_events
        self._export_counts = export_counts
        self._provide_eventlist_exporter = provide_eventlist_exporter

        self._apply_cli_cuts = apply_cli_cuts
        self._add_all_tracks = add_all_tracks
        self._get_all_track_ids = get_all_track_ids
        self._clear_all_tracks = clear_all_tracks
        self._tracks_metadata = tracks_metadata
        self._videos_metadata = videos_metadata

        self._export_tracks = export_tracks
        self._export_road_user_assignments = export_road_user_assignments
        self._export_track_statistics = export_track_statistics

    def start(self) -> None:
        """Start analysis."""
        try:
            sections = self._run_config.sections
            flows = self._run_config.flows

            self._prepare_analysis(sections, flows)
            self._run_analysis(self._run_config.track_files)
            self._export_analysis(sections, ExportMode.create(True, True))

        except Exception as cause:
            logger().exception(cause, exc_info=True)

    def _add_sections(self, sections: Iterable[Section]) -> None:
        """Add sections to section repository."""
        for section in sections:
            self._add_section(section)

    def _add_flows(self, flows: Iterable[Flow]) -> None:
        """Add flows to flow repository."""
        for flow in flows:
            self._add_flow(flow)

    def _prepare_analysis(
        self, sections: Iterable[Section], flows: Iterable[Flow]
    ) -> None:
        """Clear track and event repository, setup given sections and flows."""
        self._clear_all_tracks()
        self._event_repository.clear()
        self._add_sections(sections)
        self._add_flows(flows)

    @abstractmethod
    def _run_analysis(self, ottrk_files: set[Path]) -> None:
        raise NotImplementedError

    def _export_analysis(
        self, sections: Iterable[Section], export_mode: ExportMode
    ) -> None:
        """Export events, counts and tracks."""
        save_path = self._run_config.save_dir / self._run_config.save_name
        if self._run_config.do_events:
            self._export_events(sections, save_path, export_mode)

        if self._run_config.do_counting:
            self._do_export_counts(save_path, export_mode)

        if self._run_config.do_export_tracks:
            self._do_export_tracks(save_path, export_mode)

        if self._run_config.do_export_track_statistics:
            self._do_export_track_statistics(save_path, export_mode)

    @staticmethod
    def _validate_cli_args(run_config: RunConfiguration) -> None:
        """Validates the command line arguments passed.

        Args:
            run_config (RunConfiguration): the run configuration to be validated.

        Raises:
            CliParseError: if no track file has been passed.
            CliParseError: if no otflow file has been passed.
        """

        if not run_config.track_files:
            raise CliParseError("No ottrk files passed. Abort analysis.")

        if not run_config.config_file and not run_config.otflow:
            raise CliParseError("No otflow or otconfig file passed. Abort analysis.")

    @staticmethod
    def _get_ottrk_files(files: Iterable[Path]) -> set[Path]:
        """Parse ottrk files.

        Files that do not exist will be skipped.

        Args:
            files (list[str]): ottrk files to be parsed

        Returns:
            list[Path]: the ottrk files.
        """
        ottrk_files: set[Path] = set()
        for file in files:
            ottrk_file = file.expanduser()
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

    def _export_events(
        self,
        sections: Iterable[Section],
        save_path: Path,
        export_mode: ExportMode,
    ) -> None:
        events = self._event_repository.get_all()

        for event_format in self._run_config.event_formats:
            event_list_exporter = self._provide_eventlist_exporter(event_format)
            actual_save_path = save_path.with_suffix(
                f".events{event_list_exporter.get_extension()}"
            )

            event_export_specification = EventExportSpecification(
                file=actual_save_path,
                export_mode=export_mode,
            )

            event_list_exporter.export(events, sections, event_export_specification)
            logger().info(f"Event list saved at '{actual_save_path}'")

        assignment_path = save_path.with_suffix(
            f".{CONTEXT_FILE_TYPE_ROAD_USER_ASSIGNMENTS}.csv"
        )
        specification = ExportSpecification(
            save_path=assignment_path, format=CSV_FORMAT.name, mode=export_mode
        )
        self._export_road_user_assignments.export(specification)
        logger().info(f"Road user assignment saved at '{assignment_path}'")

    def _do_export_counts(self, save_path: Path, export_mode: ExportMode) -> None:
        logger().info("Create counts ...")
        self._tracks_metadata.notify_tracks(
            TrackRepositoryEvent.create_added(self._get_all_track_ids())
        )
        start = self._videos_metadata.first_video_start
        end = self._videos_metadata.last_video_end
        modes = self._tracks_metadata.filtered_detection_classifications

        if start is None:
            raise ValueError("start is None but has to be defined for exporting counts")
        if end is None:
            raise ValueError("end is None but has to be defined for exporting counts")
        if modes is None:
            raise ValueError("modes is None but has to be defined for exporting counts")
        for count_interval in self._run_config.count_intervals:
            output_file = save_path.with_suffix(
                f".{CONTEXT_FILE_TYPE_COUNTS}_{count_interval}"
                f"{DEFAULT_COUNT_INTERVAL_TIME_UNIT}."
                f"{DEFAULT_COUNTS_FILE_TYPE}"
            )
            counting_specification = CountingSpecificationDto(
                start=start,
                end=end,
                modes=list(modes),
                interval_in_minutes=count_interval,
                output_file=str(output_file),
                output_format="CSV",
                export_mode=export_mode,
            )
            self._export_counts.export(specification=counting_specification)

    def _do_export_tracks(self, save_path: Path, export_mode: ExportMode) -> None:
        logger().info("Start tracks export")
        specification = TrackExportSpecification(
            save_path=save_path,
            export_format=[TrackFileFormat.CSV, TrackFileFormat.OTTRK],
            export_mode=export_mode,
        )
        self._export_tracks.export(specification)
        logger().info("Finished tracks export")

    def _do_export_track_statistics(
        self, save_path: Path, export_mode: ExportMode
    ) -> None:
        logger().info("Create track statistics ...")
        track_statistics_path = save_path.with_suffix(
            f".{CONTEXT_FILE_TYPE_TRACK_STATISTICS}.csv"
        )
        specification = TrackStatisticsExportSpecification(
            save_path=track_statistics_path,
            format="CSV",
            export_mode=export_mode,
        )
        self._export_track_statistics.export(specification)


class OTAnalyticsBulkCli(OTAnalyticsCli):

    def __init__(
        self,
        run_config: RunConfiguration,
        event_repository: EventRepository,
        add_section: AddSection,
        get_all_sections: GetAllSections,
        add_flow: AddFlow,
        create_events: CreateEvents,
        export_counts: ExportCounts,
        provide_eventlist_exporter: EventListExporterProvider,
        apply_cli_cuts: ApplyCliCuts,
        add_all_tracks: AddAllTracks,
        get_all_track_ids: GetAllTrackIds,
        clear_all_tracks: ClearAllTracks,
        tracks_metadata: TracksMetadata,
        videos_metadata: VideosMetadata,
        export_tracks: ExportTracks,
        export_road_user_assignments: ExportRoadUserAssignments,
        export_track_statistics: ExportTrackStatistics,
        track_parser: TrackParser,
        progressbar: ProgressbarBuilder,
    ) -> None:
        super().__init__(
            run_config,
            event_repository,
            add_section,
            get_all_sections,
            add_flow,
            create_events,
            export_counts,
            provide_eventlist_exporter,
            apply_cli_cuts,
            add_all_tracks,
            get_all_track_ids,
            clear_all_tracks,
            tracks_metadata,
            videos_metadata,
            export_tracks,
            export_road_user_assignments,
            export_track_statistics,
        )
        self._track_parser = track_parser
        self._progressbar = progressbar

    def _run_analysis(
        self,
        ottrk_files: set[Path],
    ) -> None:
        """Run analysis."""
        ottrk_files_sorted: list[Path] = sorted(
            ottrk_files, key=lambda file: str(file).lower()
        )
        self._parse_tracks(ottrk_files_sorted)
        self._apply_cli_cuts.apply(
            self._get_all_sections(), preserve_cutting_sections=True
        )
        logger().info("Create event list ...")
        self._create_events()
        logger().info("Event list created.")

    def _parse_tracks(self, track_files: list[Path]) -> None:
        for track_file in self._progressbar(track_files, "Parsed track files", "files"):
            parse_result = self._track_parser.parse(track_file)
            self._add_all_tracks(parse_result.tracks)
            self._tracks_metadata.update_detection_classes(
                parse_result.detection_metadata.detection_classes
            )
            self._videos_metadata.update(parse_result.video_metadata)


class OTAnalyticsStreamCli(OTAnalyticsCli):

    def __init__(
        self,
        run_config: RunConfiguration,
        event_repository: EventRepository,
        add_section: AddSection,
        get_all_sections: GetAllSections,
        add_flow: AddFlow,
        create_events: CreateEvents,
        export_counts: ExportCounts,
        export_track_statistics: ExportTrackStatistics,
        provide_eventlist_exporter: EventListExporterProvider,
        apply_cli_cuts: ApplyCliCuts,
        add_all_tracks: AddAllTracks,
        get_all_track_ids: GetAllTrackIds,
        clear_all_tracks: ClearAllTracks,
        tracks_metadata: TracksMetadata,
        videos_metadata: VideosMetadata,
        export_tracks: ExportTracks,
        export_road_user_assignments: ExportRoadUserAssignments,
        track_parser: StreamTrackParser,
    ) -> None:
        super().__init__(
            run_config,
            event_repository,
            add_section,
            get_all_sections,
            add_flow,
            create_events,
            export_counts,
            provide_eventlist_exporter,
            apply_cli_cuts,
            add_all_tracks,
            get_all_track_ids,
            clear_all_tracks,
            tracks_metadata,
            videos_metadata,
            export_tracks,
            export_road_user_assignments,
            export_track_statistics,
        )
        self._track_parser = track_parser

    def _parse_track_stream(self, track_files: set[Path]) -> Iterable[TrackDataset]:
        self._track_parser.register_tracks_metadata(self._tracks_metadata)
        self._track_parser.register_videos_metadata(self._videos_metadata)

        return self._track_parser.parse(track_files)

    def _run_analysis(self, ottrk_files: set[Path]) -> None:
        """Run analysis."""
        sections = self._run_config.sections
        is_first = True

        track_stream = peekable(self._parse_track_stream(ottrk_files))

        for track_ds in track_stream:
            is_last = track_stream.peek(default=None) is None

            self._add_all_tracks(track_ds)

            self._apply_cli_cuts.apply(
                self._get_all_sections(), preserve_cutting_sections=True
            )

            logger().info("Create event list ...")
            self._create_events()
            logger().info("Event list created.")

            export_mode = ExportMode.create(is_first, flush=is_last)

            super()._export_analysis(sections, export_mode)

            self._clear_all_tracks()
            self._event_repository.clear()

            is_first = False

    def _export_analysis(
        self, sections: Iterable[Section], export_mode: ExportMode
    ) -> None:
        pass
