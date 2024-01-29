from datetime import datetime
from pathlib import Path
from shutil import copy2, rmtree
from typing import Any
from unittest.mock import Mock, call, patch

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
    DEFAULT_COUNT_INTERVAL_TIME_UNIT,
    DEFAULT_COUNTS_FILE_STEM,
    DEFAULT_COUNTS_FILE_TYPE,
    DEFAULT_EVENTLIST_FILE_TYPE,
    DEFAULT_NUM_PROCESSES,
    DEFAULT_TRACK_FILE_TYPE,
)
from OTAnalytics.application.datastore import FlowParser, TrackParser, VideoParser
from OTAnalytics.application.eventlist import SceneActionDetector
from OTAnalytics.application.logger import DEFAULT_LOG_FILE
from OTAnalytics.application.parser.cli_parser import CliArguments, CliParseError
from OTAnalytics.application.parser.config_parser import ConfigParser
from OTAnalytics.application.run_configuration import RunConfiguration
from OTAnalytics.application.state import TracksMetadata, VideosMetadata
from OTAnalytics.application.use_cases.create_events import (
    CreateEvents,
    SimpleCreateIntersectionEvents,
    SimpleCreateSceneEvents,
)
from OTAnalytics.application.use_cases.create_intersection_events import (
    BatchedTracksRunIntersect,
)
from OTAnalytics.application.use_cases.cut_tracks_with_sections import (
    CutTracksIntersectingSection,
)
from OTAnalytics.application.use_cases.event_repository import AddEvents, ClearAllEvents
from OTAnalytics.application.use_cases.export_events import EventListExporter
from OTAnalytics.application.use_cases.flow_repository import AddFlow, FlowRepository
from OTAnalytics.application.use_cases.section_repository import (
    AddSection,
    GetAllSections,
    GetSectionsById,
    RemoveSection,
)
from OTAnalytics.application.use_cases.track_repository import (
    AddAllTracks,
    ClearAllTracks,
    GetAllTrackIds,
    GetAllTracks,
    GetTracksWithoutSingleDetections,
    RemoveTracks,
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
from OTAnalytics.plugin_parser.otconfig_parser import OtConfigParser
from OTAnalytics.plugin_parser.otvision_parser import (
    DEFAULT_TRACK_LENGTH_LIMIT,
    CachedVideoParser,
    OtFlowParser,
    OttrkParser,
    PythonDetectionParser,
    SimpleVideoParser,
)
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
from OTAnalytics.plugin_video_processing.video_reader import OpenCvVideoReader
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
    return CachedVideoParser(SimpleVideoParser(OpenCvVideoReader()))


@pytest.fixture
def config_parser(video_parser: VideoParser, flow_parser: FlowParser) -> ConfigParser:
    return OtConfigParser(video_parser, flow_parser)


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
        start_cli,
        debug,
        logfile_overwrite,
        config_file,
        track_files,
        sections_file,
        save_dir,
        save_name,
        save_suffix,
        _event_formats,
        _count_intervals,
        num_processes,
        logfile,
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
    PROVIDE_EVENTLIST_EXPORTER: str = "provide_eventlist_exporter"
    CUT_TRACKS: str = "cut_tracks"
    ADD_ALL_TRACKS: str = "add_all_tracks"
    GET_ALL_TRACK_IDS: str = "get_all_track_ids"
    CLEAR_ALL_TRACKS: str = "clear_all_tracks"
    TRACKS_METADATA: str = "tracks_metadata"
    VIDEOS_METADATA: str = "videos_metadata"
    PROGRESSBAR: str = "progressbar"

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
            self.PROVIDE_EVENTLIST_EXPORTER: Mock(),
            self.CUT_TRACKS: Mock(spec=CutTracksIntersectingSection),
            self.ADD_ALL_TRACKS: Mock(spec=AddAllTracks),
            self.GET_ALL_TRACK_IDS: Mock(spec=GetAllTrackIds),
            self.CLEAR_ALL_TRACKS: Mock(spec=ClearAllTracks),
            self.TRACKS_METADATA: Mock(spec=TracksMetadata),
            self.VIDEOS_METADATA: Mock(spec=VideosMetadata),
            self.PROGRESSBAR: Mock(spec=NoProgressbarBuilder),
        }

    @pytest.fixture
    def cli_dependencies(self) -> dict[str, Any]:
        track_repository = TrackRepository(PythonTrackDataset())
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
        cut_tracks = (
            SimpleCutTracksIntersectingSection(
                GetSectionsById(section_repository),
                get_all_tracks,
                add_all_tracks,
                RemoveTracks(track_repository),
                RemoveSection(section_repository),
            ),
        )
        create_scene_events = SimpleCreateSceneEvents(
            get_tracks_without_single_detections,
            SceneActionDetector(),
            add_events,
        )
        create_events = CreateEvents(
            clear_all_events, create_intersection_events, create_scene_events
        )
        export_counts = ExportTrafficCounting(
            event_repository,
            flow_repository,
            GetSectionsById(section_repository),
            create_events,
            FilterBySectionEnterEvent(SimpleRoadUserAssigner()),
            SimpleTaggerFactory(track_repository),
            FillZerosExporterFactory(
                AddSectionInformationExporterFactory(SimpleExporterFactory())
            ),
        )
        return {
            self.TRACK_PARSER: OttrkParser(
                PythonDetectionParser(
                    ByMaxConfidence(), track_repository, DEFAULT_TRACK_LENGTH_LIMIT
                ),
            ),
            self.EVENT_REPOSITORY: event_repository,
            self.ADD_SECTION: AddSection(section_repository),
            self.GET_ALL_SECTIONS: GetAllSections(section_repository),
            self.ADD_FLOW: AddFlow(flow_repository),
            self.CREATE_EVENTS: create_events,
            self.EXPORT_COUNTS: export_counts,
            self.PROVIDE_EVENTLIST_EXPORTER: provide_available_eventlist_exporter,
            self.CUT_TRACKS: cut_tracks,
            self.ADD_ALL_TRACKS: add_all_tracks,
            self.GET_ALL_TRACK_IDS: get_all_track_ids,
            self.CLEAR_ALL_TRACKS: clear_all_tracks,
            self.TRACKS_METADATA: TracksMetadata(track_repository),
            self.VIDEOS_METADATA: VideosMetadata(),
            self.PROGRESSBAR: NoProgressbarBuilder(),
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
        assert cli._cut_tracks == mock_cli_dependencies[self.CUT_TRACKS]
        assert cli._add_all_tracks == mock_cli_dependencies[self.ADD_ALL_TRACKS]
        assert cli._clear_all_tracks == mock_cli_dependencies[self.CLEAR_ALL_TRACKS]
        assert cli._tracks_metadata == mock_cli_dependencies[self.TRACKS_METADATA]
        assert cli._videos_metadata == mock_cli_dependencies[self.VIDEOS_METADATA]
        assert cli._progressbar == mock_cli_dependencies[self.PROGRESSBAR]

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

    def test_apply_cut_tracks(self, mock_cli_dependencies: dict[str, Mock]) -> None:
        section = Mock()
        section.id = SectionId("Section 1")
        section.name = section.id.id
        section.get_type.return_value = SectionType.LINE

        normal_cutting_section = Mock()
        normal_cutting_section.id = SectionId("#cut")
        normal_cutting_section.name = normal_cutting_section.id.id
        normal_cutting_section.get_type.return_value = SectionType.CUTTING

        cli_cutting_section = Mock()
        cli_cutting_section.id = SectionId("#clicut")
        cli_cutting_section.name = cli_cutting_section.id.id
        cli_cutting_section.get_type.return_value = SectionType.LINE

        cli = OTAnalyticsCli(Mock(), **mock_cli_dependencies)
        cli._apply_cuts([normal_cutting_section, section, cli_cutting_section])

        cut_tracks = mock_cli_dependencies[self.CUT_TRACKS]
        assert cut_tracks.call_args_list == [
            call(cli_cutting_section),
            call(normal_cutting_section),
        ]

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
            test_data_tmp_dir / f"{filename}.{DEFAULT_COUNTS_FILE_STEM}_{interval}"
            f"{DEFAULT_COUNT_INTERVAL_TIME_UNIT}."
            f"{DEFAULT_COUNTS_FILE_TYPE}"
        )
        mock_cli_dependencies[self.GET_ALL_TRACK_IDS].return_value = [TrackId("1")]
        mock_cli_dependencies[self.VIDEOS_METADATA].first_video_start = start_date
        mock_cli_dependencies[self.VIDEOS_METADATA].last_video_end = end_date
        mock_cli_dependencies[
            self.TRACKS_METADATA
        ].detection_classifications = classifications

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
