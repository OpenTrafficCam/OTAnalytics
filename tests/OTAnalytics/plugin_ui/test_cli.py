from datetime import datetime
from pathlib import Path
from shutil import copy2, rmtree
from typing import Any
from unittest.mock import Mock, PropertyMock, patch

import pytest

from OTAnalytics.application.analysis.traffic_counting import (
    ExportCounts,
    ExportTrafficCounting,
    FilterBySectionEnterEvent,
    SimpleRoadUserAssigner,
    SimpleTaggerFactory,
)
from OTAnalytics.application.analysis.traffic_counting_specification import (
    CountingSpecificationDto,
)
from OTAnalytics.application.config import (
    CONTEXT_FILE_TYPE_COUNTS,
    DEFAULT_COUNT_INTERVAL_TIME_UNIT,
    DEFAULT_COUNTS_FILE_TYPE,
    DEFAULT_EVENTLIST_FILE_TYPE,
    DEFAULT_NUM_PROCESSES,
    DEFAULT_TRACK_FILE_TYPE,
)
from OTAnalytics.application.datastore import TrackParser, VideoParser
from OTAnalytics.application.eventlist import SceneActionDetector
from OTAnalytics.application.logger import DEFAULT_LOG_FILE
from OTAnalytics.application.parser.cli_parser import CliArguments, CliParseError
from OTAnalytics.application.parser.config_parser import ConfigParser
from OTAnalytics.application.parser.flow_parser import FlowParser
from OTAnalytics.application.run_configuration import RunConfiguration
from OTAnalytics.application.state import TracksMetadata, VideosMetadata
from OTAnalytics.application.use_cases.apply_cli_cuts import ApplyCliCuts
from OTAnalytics.application.use_cases.create_events import (
    CreateEvents,
    SimpleCreateIntersectionEvents,
    SimpleCreateSceneEvents,
)
from OTAnalytics.application.use_cases.create_intersection_events import (
    BatchedTracksRunIntersect,
)
from OTAnalytics.application.use_cases.event_repository import AddEvents, ClearAllEvents
from OTAnalytics.application.use_cases.export_events import EventListExporter
from OTAnalytics.application.use_cases.flow_repository import AddFlow, FlowRepository
from OTAnalytics.application.use_cases.road_user_assignment_export import (
    ExportRoadUserAssignments,
)
from OTAnalytics.application.use_cases.section_repository import (
    AddSection,
    GetAllSections,
    GetSectionsById,
    RemoveSection,
)
from OTAnalytics.application.use_cases.track_export import ExportTracks
from OTAnalytics.application.use_cases.track_repository import (
    AddAllTracks,
    ClearAllTracks,
    GetAllTrackIds,
    GetAllTracks,
    GetTracksWithoutSingleDetections,
    RemoveTracks,
    TrackRepositorySize,
)
from OTAnalytics.domain.event import EventRepository
from OTAnalytics.domain.progress import NoProgressbarBuilder
from OTAnalytics.domain.section import SectionId, SectionRepository, SectionType
from OTAnalytics.domain.track import TrackId
from OTAnalytics.domain.track_repository import TrackRepository
from OTAnalytics.plugin_datastore.python_track_store import (
    ByMaxConfidence,
    PythonTrackDataset,
)
from OTAnalytics.plugin_datastore.track_geometry_store.pygeos_store import (
    PygeosTrackGeometryDataset,
)
from OTAnalytics.plugin_intersect.simple.cut_tracks_with_sections import (
    SimpleCutTracksIntersectingSection,
)
from OTAnalytics.plugin_intersect_parallelization.multiprocessing import (
    MultiprocessingIntersectParallelization,
)
from OTAnalytics.plugin_parser.export import (
    AddSectionInformationExporterFactory,
    FillZerosExporterFactory,
    SimpleExporterFactory,
)
from OTAnalytics.plugin_parser.otconfig_parser import (
    OtConfigFormatFixer,
    OtConfigParser,
)
from OTAnalytics.plugin_parser.otvision_parser import (
    DEFAULT_TRACK_LENGTH_LIMIT,
    CachedVideoParser,
    OtFlowParser,
    OttrkParser,
    PythonDetectionParser,
    SimpleVideoParser,
)
from OTAnalytics.plugin_parser.road_user_assignment_export import (
    SimpleRoadUserAssignmentExporterFactory,
)
from OTAnalytics.plugin_parser.track_export import CsvTrackExport
from OTAnalytics.plugin_prototypes.eventlist_exporter.eventlist_exporter import (
    AVAILABLE_EVENTLIST_EXPORTERS,
    OTC_OTEVENTS_FORMAT_NAME,
    provide_available_eventlist_exporter,
)
from OTAnalytics.plugin_ui.cli import (
    InvalidSectionFileType,
    OTAnalyticsCli,
    SectionsFileDoesNotExist,
)
from OTAnalytics.plugin_video_processing.video_reader import PyAvVideoReader
from tests.conftest import YieldFixture

CONFIG_FILE = "path/to/config.otconfig"
SECTION_FILE = "path/to/section.otflow"
TRACK_FILE = f"ottrk_file.{DEFAULT_TRACK_FILE_TYPE}"


@pytest.fixture
def temp_tracks_directory(
    test_data_tmp_dir: Path, ottrk_path: Path
) -> YieldFixture[Path]:
    tracks = test_data_tmp_dir / "tracks"
    tracks.mkdir()
    copy2(src=ottrk_path, dst=tracks / f"track_1.{DEFAULT_TRACK_FILE_TYPE}")
    copy2(src=ottrk_path, dst=tracks / f"track_2.{DEFAULT_TRACK_FILE_TYPE}")

    sub_directory = tracks / "sub_directory"
    sub_directory.mkdir()
    copy2(src=ottrk_path, dst=sub_directory / f"track_3.{DEFAULT_TRACK_FILE_TYPE}")
    copy2(src=ottrk_path, dst=sub_directory / f"track_4.{DEFAULT_TRACK_FILE_TYPE}")
    yield tracks
    rmtree(tracks)


@pytest.fixture
def temp_ottrk(test_data_tmp_dir: Path, ottrk_path: Path) -> YieldFixture[Path]:
    file_name = ottrk_path.name
    temp_ottrk = test_data_tmp_dir / file_name
    copy2(src=ottrk_path, dst=temp_ottrk)
    yield temp_ottrk
    temp_ottrk.unlink()


@pytest.fixture
def temp_section(test_data_tmp_dir: Path, otsection_file: Path) -> YieldFixture[Path]:
    file_name = otsection_file.name
    temp_otsection = test_data_tmp_dir / file_name
    copy2(src=otsection_file, dst=temp_otsection)
    yield temp_otsection
    temp_otsection.unlink()


@pytest.fixture
def temp_otconfig(
    test_data_tmp_dir: Path, otconfig_file: Path, ottrk_path: Path, cyclist_video: Path
) -> YieldFixture[Path]:
    temp_dir = test_data_tmp_dir / "temp_otconfig"
    temp_dir.mkdir(parents=True)
    temp_otconfig = temp_dir / otconfig_file.name
    temp_ottrk = temp_dir / ottrk_path.name
    temp_video = temp_dir / cyclist_video.name
    copy2(src=otconfig_file, dst=temp_otconfig)
    copy2(src=ottrk_path, dst=temp_ottrk)
    copy2(src=cyclist_video, dst=temp_video)
    yield temp_otconfig


@pytest.fixture
def event_list_exporter() -> EventListExporter:
    return AVAILABLE_EVENTLIST_EXPORTERS[OTC_OTEVENTS_FORMAT_NAME]


@pytest.fixture
def flow_parser() -> FlowParser:
    return OtFlowParser()


@pytest.fixture
def mock_flow_parser() -> Mock:
    parser = Mock()
    parser.parse.return_value = ([], [])
    return parser


@pytest.fixture
def video_parser() -> VideoParser:
    return CachedVideoParser(SimpleVideoParser(PyAvVideoReader()))


@pytest.fixture
def config_parser(
    do_nothing_fixer: OtConfigFormatFixer,
    video_parser: VideoParser,
    flow_parser: FlowParser,
) -> ConfigParser:
    return OtConfigParser(
        format_fixer=do_nothing_fixer,
        video_parser=video_parser,
        flow_parser=flow_parser,
    )


def create_run_config(
    flow_parser: FlowParser,
    start_cli: bool = True,
    debug: bool = False,
    config_file: str = CONFIG_FILE,
    track_files: list[str] | None = None,
    sections_file: str = SECTION_FILE,
    save_dir: str = "",
    save_name: str = "",
    save_suffix: str = "",
    event_formats: list[str] | None = None,
    count_intervals: list[int] | None = None,
    track_export: bool = False,
    num_processes: int = DEFAULT_NUM_PROCESSES,
    logfile: str = str(DEFAULT_LOG_FILE),
    logfile_overwrite: bool = False,
) -> RunConfiguration:
    if event_formats:
        _event_formats = event_formats
    else:
        _event_formats = [DEFAULT_EVENTLIST_FILE_TYPE]

    if count_intervals:
        _count_intervals = count_intervals
    else:
        _count_intervals = [1]

    if track_files is None:
        track_files = [TRACK_FILE]
    cli_args = CliArguments(
        start_cli=start_cli,
        debug=debug,
        logfile_overwrite=logfile_overwrite,
        track_export=track_export,
        config_file=config_file,
        track_files=track_files,
        otflow_file=sections_file,
        save_dir=save_dir,
        save_name=save_name,
        save_suffix=save_suffix,
        event_formats=_event_formats,
        count_intervals=_count_intervals,
        num_processes=num_processes,
        log_file=logfile,
    )
    run_config = RunConfiguration(flow_parser, cli_args)
    return run_config


class TestOTAnalyticsCli:
    TRACK_PARSER: str = "track_parser"
    EVENT_REPOSITORY: str = "event_repository"
    ADD_SECTION: str = "add_section"
    GET_ALL_SECTIONS: str = "get_all_sections"
    ADD_FLOW: str = "add_flow"
    CREATE_EVENTS: str = "create_events"
    EXPORT_COUNTS: str = "export_counts"
    EXPORT_TRACKS: str = "export_tracks"
    PROVIDE_EVENTLIST_EXPORTER: str = "provide_eventlist_exporter"
    APPLY_CLI_CUTS: str = "apply_cli_cuts"
    ADD_ALL_TRACKS: str = "add_all_tracks"
    GET_ALL_TRACK_IDS: str = "get_all_track_ids"
    CLEAR_ALL_TRACKS: str = "clear_all_tracks"
    TRACKS_METADATA: str = "tracks_metadata"
    VIDEOS_METADATA: str = "videos_metadata"
    PROGRESSBAR: str = "progressbar"
    EXPORT_ROAD_USER_ASSIGNMENT: str = "export_road_user_assignments"

    @pytest.fixture
    def mock_cli_dependencies(self) -> dict[str, Any]:
        return {
            self.TRACK_PARSER: Mock(spec=TrackParser),
            self.EVENT_REPOSITORY: Mock(spec=EventRepository),
            self.ADD_SECTION: Mock(spec=AddSection),
            self.GET_ALL_SECTIONS: Mock(spec=GetAllSections),
            self.ADD_FLOW: Mock(spec=AddFlow),
            self.CREATE_EVENTS: Mock(spec=CreateEvents),
            self.EXPORT_COUNTS: Mock(spec=ExportCounts),
            self.EXPORT_TRACKS: Mock(spec=ExportTracks),
            self.PROVIDE_EVENTLIST_EXPORTER: Mock(),
            self.APPLY_CLI_CUTS: Mock(spec=ApplyCliCuts),
            self.ADD_ALL_TRACKS: Mock(spec=AddAllTracks),
            self.GET_ALL_TRACK_IDS: Mock(spec=GetAllTrackIds),
            self.CLEAR_ALL_TRACKS: Mock(spec=ClearAllTracks),
            self.TRACKS_METADATA: Mock(spec=TracksMetadata),
            self.VIDEOS_METADATA: Mock(spec=VideosMetadata),
            self.PROGRESSBAR: Mock(spec=NoProgressbarBuilder),
            self.EXPORT_ROAD_USER_ASSIGNMENT: Mock(spec=ExportRoadUserAssignments),
        }

    @pytest.fixture
    def cli_dependencies(self) -> dict[str, Any]:
        track_repository = TrackRepository(
            PythonTrackDataset(PygeosTrackGeometryDataset.from_track_dataset)
        )
        section_repository = SectionRepository()
        event_repository = EventRepository()
        flow_repository = FlowRepository()
        add_events = AddEvents(event_repository)

        get_tracks_without_single_detections = GetTracksWithoutSingleDetections(
            track_repository
        )
        get_all_tracks = GetAllTracks(track_repository)
        get_all_track_ids = GetAllTrackIds(track_repository)
        add_all_tracks = AddAllTracks(track_repository)
        clear_all_tracks = ClearAllTracks(track_repository)

        clear_all_events = ClearAllEvents(event_repository)
        create_intersection_events = SimpleCreateIntersectionEvents(
            BatchedTracksRunIntersect(
                MultiprocessingIntersectParallelization(),
                get_all_tracks,
            ),
            section_repository.get_all,
            add_events,
        )
        cut_tracks = SimpleCutTracksIntersectingSection(
            GetSectionsById(section_repository),
            get_all_tracks,
            add_all_tracks,
            RemoveTracks(track_repository),
            RemoveSection(section_repository),
        )
        apply_cli_cuts = ApplyCliCuts(cut_tracks, TrackRepositorySize(track_repository))
        create_scene_events = SimpleCreateSceneEvents(
            get_tracks_without_single_detections,
            SceneActionDetector(),
            add_events,
        )
        create_events = CreateEvents(
            clear_all_events, create_intersection_events, create_scene_events
        )
        assigner = FilterBySectionEnterEvent(SimpleRoadUserAssigner())
        export_counts = ExportTrafficCounting(
            event_repository,
            flow_repository,
            GetSectionsById(section_repository),
            create_events,
            assigner,
            SimpleTaggerFactory(track_repository),
            FillZerosExporterFactory(
                AddSectionInformationExporterFactory(SimpleExporterFactory())
            ),
        )
        tracks_metadata = TracksMetadata(track_repository)
        videos_metadata = VideosMetadata()
        export_tracks = CsvTrackExport(
            track_repository, tracks_metadata, videos_metadata
        )
        export_road_user_assignments = ExportRoadUserAssignments(
            event_repository=event_repository,
            flow_repository=flow_repository,
            create_events=create_events,
            assigner=assigner,
            exporter_factory=SimpleRoadUserAssignmentExporterFactory(
                section_repository, get_all_tracks
            ),
        )
        return {
            self.TRACK_PARSER: OttrkParser(
                PythonDetectionParser(
                    ByMaxConfidence(),
                    track_repository,
                    PygeosTrackGeometryDataset.from_track_dataset,
                    DEFAULT_TRACK_LENGTH_LIMIT,
                ),
            ),
            self.EVENT_REPOSITORY: event_repository,
            self.ADD_SECTION: AddSection(section_repository),
            self.GET_ALL_SECTIONS: GetAllSections(section_repository),
            self.ADD_FLOW: AddFlow(flow_repository),
            self.CREATE_EVENTS: create_events,
            self.EXPORT_COUNTS: export_counts,
            self.EXPORT_TRACKS: export_tracks,
            self.PROVIDE_EVENTLIST_EXPORTER: provide_available_eventlist_exporter,
            self.APPLY_CLI_CUTS: apply_cli_cuts,
            self.ADD_ALL_TRACKS: add_all_tracks,
            self.GET_ALL_TRACK_IDS: get_all_track_ids,
            self.CLEAR_ALL_TRACKS: clear_all_tracks,
            self.TRACKS_METADATA: tracks_metadata,
            self.VIDEOS_METADATA: videos_metadata,
            self.PROGRESSBAR: NoProgressbarBuilder(),
            self.EXPORT_ROAD_USER_ASSIGNMENT: export_road_user_assignments,
        }

    def test_init(
        self, mock_cli_dependencies: dict[str, Any], mock_flow_parser: FlowParser
    ) -> None:
        run_config = create_run_config(mock_flow_parser)
        cli = OTAnalyticsCli(run_config, **mock_cli_dependencies)
        assert cli._run_config == run_config
        assert cli._track_parser == mock_cli_dependencies[self.TRACK_PARSER]
        assert cli._add_section == mock_cli_dependencies[self.ADD_SECTION]
        assert cli._get_all_sections == mock_cli_dependencies[self.GET_ALL_SECTIONS]
        assert cli._add_flow == mock_cli_dependencies[self.ADD_FLOW]
        assert cli._create_events == mock_cli_dependencies[self.CREATE_EVENTS]
        assert cli._export_counts == mock_cli_dependencies[self.EXPORT_COUNTS]
        assert cli._export_tracks == mock_cli_dependencies[self.EXPORT_TRACKS]
        assert cli._apply_cli_cuts == mock_cli_dependencies[self.APPLY_CLI_CUTS]
        assert cli._add_all_tracks == mock_cli_dependencies[self.ADD_ALL_TRACKS]
        assert cli._clear_all_tracks == mock_cli_dependencies[self.CLEAR_ALL_TRACKS]
        assert cli._tracks_metadata == mock_cli_dependencies[self.TRACKS_METADATA]
        assert cli._videos_metadata == mock_cli_dependencies[self.VIDEOS_METADATA]
        assert cli._progressbar == mock_cli_dependencies[self.PROGRESSBAR]
        assert (
            cli._export_road_user_assignments
            == mock_cli_dependencies[self.EXPORT_ROAD_USER_ASSIGNMENT]
        )

    def test_init_empty_tracks_cli_arg(
        self, mock_cli_dependencies: dict[str, Any], mock_flow_parser: FlowParser
    ) -> None:
        run_config = create_run_config(mock_flow_parser, track_files=[])
        with pytest.raises(CliParseError, match=r"No ottrk files passed.*"):
            OTAnalyticsCli(run_config, **mock_cli_dependencies)

    def test_init_no_otflow_and_otconfig_file_present(
        self, mock_cli_dependencies: dict[str, Any], mock_flow_parser: FlowParser
    ) -> None:
        run_config = create_run_config(
            mock_flow_parser, config_file="", sections_file=""
        )
        expected_error_msg = "No otflow or otconfig file passed.*"
        with pytest.raises(CliParseError, match=expected_error_msg):
            OTAnalyticsCli(run_config, **mock_cli_dependencies)

    def test_validate_cli_args_no_tracks(self, mock_flow_parser: FlowParser) -> None:
        run_config = create_run_config(mock_flow_parser, track_files=[])
        with pytest.raises(CliParseError, match=r"No ottrk files passed.*"):
            OTAnalyticsCli._validate_cli_args(run_config)

    def test_validate_cli_args_no_otflow_and_otconfig(
        self, mock_flow_parser: FlowParser
    ) -> None:
        run_config = create_run_config(
            mock_flow_parser, config_file="", sections_file=""
        )
        expected_error_msg = "No otflow or otconfig file passed.*"
        with pytest.raises(CliParseError, match=expected_error_msg):
            OTAnalyticsCli._validate_cli_args(run_config)

    def test_parse_ottrk_files_with_subdirs(self, temp_tracks_directory: Path) -> None:
        tracks = OTAnalyticsCli._get_ottrk_files([temp_tracks_directory])
        assert temp_tracks_directory / f"track_1.{DEFAULT_TRACK_FILE_TYPE}" in tracks
        assert temp_tracks_directory / f"track_2.{DEFAULT_TRACK_FILE_TYPE}" in tracks
        assert (
            temp_tracks_directory / f"sub_directory/track_3.{DEFAULT_TRACK_FILE_TYPE}"
            in tracks
        )
        assert (
            temp_tracks_directory / f"sub_directory/track_4.{DEFAULT_TRACK_FILE_TYPE}"
            in tracks
        )

    def test_parse_ottrk_files_no_existing_files(self) -> None:
        track_1 = Path(f"path/to/foo.{DEFAULT_TRACK_FILE_TYPE}")
        track_2 = Path(f"path/to/bar.{DEFAULT_TRACK_FILE_TYPE}")

        parsed_tracks = OTAnalyticsCli._get_ottrk_files([track_1, track_2])
        assert not parsed_tracks

    def test_parse_ottrk_files_single_file(self, temp_ottrk: Path) -> None:
        parsed_tracks = OTAnalyticsCli._get_ottrk_files([temp_ottrk])
        assert temp_ottrk in parsed_tracks

    def test_parse_ottrk_files_multiple_files(
        self, temp_ottrk: Path, temp_tracks_directory: Path
    ) -> None:
        parsed_tracks = OTAnalyticsCli._get_ottrk_files(
            [temp_ottrk, temp_tracks_directory]
        )
        assert temp_ottrk in parsed_tracks
        assert (
            temp_tracks_directory / f"track_1.{DEFAULT_TRACK_FILE_TYPE}"
            in parsed_tracks
        )
        assert (
            temp_tracks_directory / f"track_2.{DEFAULT_TRACK_FILE_TYPE}"
            in parsed_tracks
        )
        assert (
            temp_tracks_directory / f"sub_directory/track_3.{DEFAULT_TRACK_FILE_TYPE}"
            in parsed_tracks
        )
        assert (
            temp_tracks_directory / f"sub_directory/track_4.{DEFAULT_TRACK_FILE_TYPE}"
            in parsed_tracks
        )

    def test_parse_sections_file(self, otsection_file: Path) -> None:
        section_file = OTAnalyticsCli._get_sections_file(str(otsection_file))
        assert section_file == otsection_file

    def test_parse_sections_file_does_not_exist(self) -> None:
        with pytest.raises(SectionsFileDoesNotExist, match=r"Sections file.*"):
            OTAnalyticsCli._get_sections_file("foo/bar.otflow")

    def test_parse_sections_file_wrong_filetype(self, test_data_tmp_dir: Path) -> None:
        section_with_wrong_filetype = test_data_tmp_dir / "section.otmeow"
        section_with_wrong_filetype.touch()

        with pytest.raises(InvalidSectionFileType):
            OTAnalyticsCli._get_sections_file(str(section_with_wrong_filetype))

    def test_start_with_no_video_in_folder(
        self,
        test_data_tmp_dir: Path,
        temp_ottrk: Path,
        temp_section: Path,
        cli_dependencies: dict[str, Any],
        flow_parser: FlowParser,
    ) -> None:
        save_name = test_data_tmp_dir / "stem"
        save_suffix = "suffix"
        count_interval = 1
        run_config = create_run_config(
            flow_parser,
            track_files=[str(temp_ottrk)],
            sections_file=str(temp_section),
            config_file="",
            save_name=str(save_name),
            save_suffix=save_suffix,
            count_intervals=[count_interval],
        )
        cli = OTAnalyticsCli(run_config, **cli_dependencies)
        cli.start()
        expected_event_list_file = save_name.with_name(
            f"stem_{save_suffix}.events.{DEFAULT_EVENTLIST_FILE_TYPE}"
        )
        expected_counts_file = save_name.with_name(
            f"stem_{save_suffix}.counts_{count_interval}"
            f"{DEFAULT_COUNT_INTERVAL_TIME_UNIT}.{DEFAULT_COUNTS_FILE_TYPE}"
        )

        assert expected_event_list_file.exists()
        assert expected_counts_file.exists()

    def test_use_video_start_and_end_for_counting(
        self,
        test_data_tmp_dir: Path,
        mock_cli_dependencies: dict[str, Mock],
    ) -> None:
        section_1 = Mock()
        section_1.id = SectionId("Section 1")
        section_1.name = section_1.id.id
        section_1.get_type.return_value = SectionType.LINE

        section_2 = Mock()
        section_2.id = SectionId("Section 2")
        section_2.name = section_2.id.id
        section_2.get_type.return_value = SectionType.LINE

        start_date = datetime(2023, 11, 22, 0, 0)
        end_date = datetime(2023, 11, 22, 1, 0)
        classifications = frozenset(["car", "bike"])
        interval = 15
        filename = "filename"
        expected_output_file = (
            test_data_tmp_dir / f"{filename}.{CONTEXT_FILE_TYPE_COUNTS}_{interval}"
            f"{DEFAULT_COUNT_INTERVAL_TIME_UNIT}."
            f"{DEFAULT_COUNTS_FILE_TYPE}"
        )
        mock_cli_dependencies[self.GET_ALL_TRACK_IDS].return_value = [TrackId("1")]
        mock_cli_dependencies[self.VIDEOS_METADATA].first_video_start = start_date
        mock_cli_dependencies[self.VIDEOS_METADATA].last_video_end = end_date
        mock_cli_dependencies[
            self.TRACKS_METADATA
        ].filtered_detection_classifications = classifications

        run_config = Mock()
        run_config.count_intervals = {interval}
        cli = OTAnalyticsCli(run_config, **mock_cli_dependencies)
        cli._do_export_counts(test_data_tmp_dir / filename)

        export_counts = mock_cli_dependencies[self.EXPORT_COUNTS]

        expected_specification = CountingSpecificationDto(
            start=start_date,
            end=end_date,
            interval_in_minutes=interval,
            modes=list(classifications),
            output_format="CSV",
            output_file=str(expected_output_file),
        )
        export_counts.export.assert_called_with(specification=expected_specification)

    def test_cli_with_otconfig_has_expected_output_files(
        self,
        cli_dependencies: dict[str, Any],
        flow_parser: FlowParser,
        config_parser: ConfigParser,
        temp_otconfig: Path,
    ) -> None:
        cli_args = CliArguments(
            start_cli=True,
            debug=False,
            logfile_overwrite=False,
            track_export=False,
            config_file=str(temp_otconfig),
        )
        otconfig = config_parser.parse(temp_otconfig)
        run_config = RunConfiguration(flow_parser, cli_args, otconfig)
        cli = OTAnalyticsCli(run_config, **cli_dependencies)

        cli.start()
        for event_format in run_config.event_formats:
            expected_events_file = temp_otconfig.with_name(
                f"my_name_my_suffix.events.{event_format}"
            )
            assert expected_events_file.is_file()

        for count_interval in run_config.count_intervals:
            expected_counts_file = temp_otconfig.with_name(
                f"my_name_my_suffix.counts_{count_interval}"
                f"{DEFAULT_COUNT_INTERVAL_TIME_UNIT}.csv"
            )
            assert expected_counts_file.is_file()

    @patch("OTAnalytics.plugin_ui.cli.OTAnalyticsCli._run_analysis")
    @patch("OTAnalytics.plugin_ui.cli.logger")
    def test_exceptions_are_being_logged(
        self,
        get_logger: Mock,
        mock_run_analysis: Mock,
        mock_cli_dependencies: dict[str, Mock],
    ) -> None:
        exception = Exception("My Exception")
        mock_run_analysis.side_effect = exception
        logger = Mock()
        get_logger.return_value = logger

        cli = OTAnalyticsCli(Mock(), **mock_cli_dependencies)
        cli.start()
        logger.exception.assert_called_once_with(exception, exc_info=True)
        mock_run_analysis.assert_called_once()

    @patch("OTAnalytics.plugin_ui.cli.OTAnalyticsCli._do_export_counts")
    @patch("OTAnalytics.plugin_ui.cli.OTAnalyticsCli._export_events")
    @patch("OTAnalytics.plugin_ui.cli.OTAnalyticsCli._parse_tracks")
    @patch("OTAnalytics.plugin_ui.cli.OTAnalyticsCli._add_sections")
    @patch("OTAnalytics.plugin_ui.cli.OTAnalyticsCli._add_flows")
    def test_run_analysis(
        self,
        mock_add_flows: Mock,
        mock_add_sections: Mock,
        mock_parse_tracks: Mock,
        mock_export_events: Mock,
        mock_do_export_counts: Mock,
        mock_cli_dependencies: dict[str, Mock],
    ) -> None:
        run_config = Mock()
        type(run_config).do_events = PropertyMock(return_value=True)
        type(run_config).do_counting = PropertyMock(return_value=True)
        type(run_config).save_dir = PropertyMock(return_value=Path("path/to/my/dir"))
        type(run_config).save_name = PropertyMock(return_value="my_save_name")

        first_track_file = Path("path/to/a.ottrk")
        second_track_file = Path("path/to/b.ottrk")
        sections = [Mock()]
        flows = [Mock()]

        mock_cli_dependencies[self.GET_ALL_SECTIONS].return_value = sections

        cli = OTAnalyticsCli(run_config, **mock_cli_dependencies)
        cli._run_analysis({second_track_file, first_track_file}, sections, flows)

        mock_cli_dependencies[self.CLEAR_ALL_TRACKS].assert_called_once()
        mock_cli_dependencies[self.EVENT_REPOSITORY].clear.assert_called_once()
        mock_add_flows.assert_called_once_with(flows)
        mock_add_sections.assert_called_once_with(sections)
        mock_parse_tracks.assert_called_once_with([first_track_file, second_track_file])
        mock_cli_dependencies[self.GET_ALL_SECTIONS].assert_called_once()
        mock_cli_dependencies[self.APPLY_CLI_CUTS].apply.assert_called_once_with(
            sections, preserve_cutting_sections=False
        )
        mock_cli_dependencies[self.CREATE_EVENTS].assert_called_once()
        mock_export_events.assert_called_once_with(
            sections, run_config.save_dir / run_config.save_name
        )
        mock_do_export_counts.assert_called_once_with(
            run_config.save_dir / run_config.save_name
        )
