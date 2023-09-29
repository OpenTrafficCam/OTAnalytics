import sys
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
from OTAnalytics.application.config import (
    DEFAULT_EVENTLIST_FILE_STEM,
    DEFAULT_EVENTLIST_FILE_TYPE,
    DEFAULT_TRACK_FILE_TYPE,
)
from OTAnalytics.application.datastore import EventListParser, FlowParser, TrackParser
from OTAnalytics.application.eventlist import SceneActionDetector
from OTAnalytics.application.state import TrackViewState
from OTAnalytics.application.use_cases.create_events import (
    CreateEvents,
    SimpleCreateIntersectionEvents,
    SimpleCreateSceneEvents,
)
from OTAnalytics.application.use_cases.cut_tracks_with_sections import (
    CutTracksIntersectingSection,
)
from OTAnalytics.application.use_cases.event_repository import AddEvents, ClearAllEvents
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
    GetTracksFromIds,
    GetTracksWithoutSingleDetections,
    RemoveTracks,
)
from OTAnalytics.domain.event import EventRepository, SceneEventBuilder
from OTAnalytics.domain.progress import NoProgressbarBuilder
from OTAnalytics.domain.section import SectionId, SectionRepository, SectionType
from OTAnalytics.domain.track import ByMaxConfidence, TrackRepository
from OTAnalytics.plugin_intersect.shapely.intersect import ShapelyIntersector
from OTAnalytics.plugin_intersect.shapely.mapping import ShapelyMapper
from OTAnalytics.plugin_intersect.simple.cut_tracks_with_sections import (
    SimpleCutTrackSegmentBuilder,
    SimpleCutTracksIntersectingSection,
    SimpleCutTracksWithSection,
)
from OTAnalytics.plugin_intersect.simple_intersect import (
    SimpleRunIntersect,
    SimpleTracksIntersectingSections,
)
from OTAnalytics.plugin_intersect_parallelization.multiprocessing import (
    MultiprocessingIntersectParallelization,
)
from OTAnalytics.plugin_parser.export import (
    AddSectionInformationExporterFactory,
    FillZerosExporterFactory,
    SimpleExporterFactory,
)
from OTAnalytics.plugin_parser.otvision_parser import (
    DEFAULT_TRACK_LENGTH_LIMIT,
    OtEventListParser,
    OtFlowParser,
    OttrkParser,
    PythonDetectionParser,
)
from OTAnalytics.plugin_ui.cli import (
    CliArgumentParser,
    CliArguments,
    CliParseError,
    InvalidSectionFileType,
    OTAnalyticsCli,
    SectionsFileDoesNotExist,
)
from tests.conftest import YieldFixture


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


class TestCliArgumentParser:
    def test_parse_with_valid_cli_args(self) -> None:
        track_file_1 = f"track_file_1.{DEFAULT_TRACK_FILE_TYPE}"
        track_file_2 = f"track_file_2.{DEFAULT_TRACK_FILE_TYPE}"
        sections_file = "section_file.otflow"
        eventlist_name = "my_events"

        cli_args: list[str] = [
            "path",
            "--cli",
            "--ottrks",
            track_file_1,
            track_file_2,
            "--otflow",
            sections_file,
            "--save-name",
            eventlist_name,
        ]
        with patch.object(sys, "argv", cli_args):
            parser = CliArgumentParser()
            args = parser.parse()
            assert args == CliArguments(
                True, False, [track_file_1, track_file_2], sections_file, eventlist_name
            )


class TestOTAnalyticsCli:
    TRACK_PARSER: str = "track_parser"
    FLOW_PARSER: str = "flow_parser"
    EVENT_LIST_PARSER: str = "event_list_parser"
    EVENT_REPOSITORY: str = "event_repository"
    ADD_SECTION: str = "add_section"
    GET_ALL_SECTIONS: str = "get_all_sections"
    ADD_FLOW: str = "add_flow"
    CREATE_EVENTS: str = "create_events"
    EXPORT_COUNTS: str = "export_counts"
    CUT_TRACKS: str = "cut_tracks"
    ADD_ALL_TRACKS: str = "add_all_tracks"
    GET_ALL_TRACK_IDS: str = "get_all_track_ids"
    CLEAR_ALL_TRACKS: str = "clear_all_tracks"
    PROGRESSBAR: str = "progressbar"

    @pytest.fixture
    def mock_cli_dependencies(self) -> dict[str, Any]:
        return {
            self.TRACK_PARSER: Mock(spec=TrackParser),
            self.FLOW_PARSER: Mock(spec=FlowParser),
            self.EVENT_LIST_PARSER: Mock(spec=EventListParser),
            self.EVENT_REPOSITORY: Mock(spec=EventRepository),
            self.ADD_SECTION: Mock(spec=AddSection),
            self.GET_ALL_SECTIONS: Mock(spec=GetAllSections),
            self.ADD_FLOW: Mock(spec=AddFlow),
            self.CREATE_EVENTS: Mock(spec=CreateEvents),
            self.EXPORT_COUNTS: Mock(spec=ExportCounts),
            self.CUT_TRACKS: Mock(spec=CutTracksIntersectingSection),
            self.ADD_ALL_TRACKS: Mock(spec=AddAllTracks),
            self.GET_ALL_TRACK_IDS: Mock(spec=GetAllTrackIds),
            self.CLEAR_ALL_TRACKS: Mock(spec=ClearAllTracks),
            self.PROGRESSBAR: Mock(spec=NoProgressbarBuilder),
        }

    @pytest.fixture
    def cli_dependencies(self) -> dict[str, Any]:
        track_repository = TrackRepository()
        section_repository = SectionRepository()
        event_repository = EventRepository()
        flow_repository = FlowRepository()
        add_events = AddEvents(event_repository)

        get_all_tracks = GetTracksWithoutSingleDetections(track_repository)
        get_all_track_ids = GetAllTrackIds(track_repository)
        add_all_tracks = AddAllTracks(track_repository)
        clear_all_tracks = ClearAllTracks(track_repository)

        clear_all_events = ClearAllEvents(event_repository)
        create_intersection_events = SimpleCreateIntersectionEvents(
            SimpleRunIntersect(
                ShapelyIntersector(),
                MultiprocessingIntersectParallelization(),
                get_all_tracks,
            ),
            section_repository,
            add_events,
        )
        tracks_intersecting_sections = SimpleTracksIntersectingSections(
            get_all_tracks, ShapelyIntersector()
        )
        cut_tracks_with_section = SimpleCutTracksWithSection(
            GetTracksFromIds(track_repository),
            ShapelyMapper(),
            SimpleCutTrackSegmentBuilder(ByMaxConfidence()),
            TrackViewState(),
        )
        cut_tracks = (
            SimpleCutTracksIntersectingSection(
                GetSectionsById(section_repository),
                get_all_tracks,
                tracks_intersecting_sections,
                cut_tracks_with_section,
                add_all_tracks,
                RemoveTracks(track_repository),
                RemoveSection(section_repository),
            ),
        )
        create_scene_events = SimpleCreateSceneEvents(
            get_all_tracks,
            SceneActionDetector(SceneEventBuilder()),
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
            self.FLOW_PARSER: OtFlowParser(),
            self.EVENT_LIST_PARSER: OtEventListParser(),
            self.EVENT_REPOSITORY: event_repository,
            self.ADD_SECTION: AddSection(section_repository),
            self.GET_ALL_SECTIONS: GetAllSections(section_repository),
            self.ADD_FLOW: AddFlow(flow_repository),
            self.CREATE_EVENTS: create_events,
            self.EXPORT_COUNTS: export_counts,
            self.CUT_TRACKS: cut_tracks,
            self.ADD_ALL_TRACKS: add_all_tracks,
            self.GET_ALL_TRACK_IDS: get_all_track_ids,
            self.CLEAR_ALL_TRACKS: clear_all_tracks,
            self.PROGRESSBAR: NoProgressbarBuilder(),
        }

    def test_init(self, mock_cli_dependencies: dict[str, Any]) -> None:
        cli_args = CliArguments(
            True,
            False,
            [f"track_file.{DEFAULT_TRACK_FILE_TYPE}"],
            "sections_file.otflow",
            "my_events",
        )
        cli = OTAnalyticsCli(cli_args, **mock_cli_dependencies)
        assert cli.cli_args == cli_args
        assert cli._track_parser == mock_cli_dependencies[self.TRACK_PARSER]
        assert cli._flow_parser == mock_cli_dependencies[self.FLOW_PARSER]
        assert cli._event_list_parser == mock_cli_dependencies[self.EVENT_LIST_PARSER]
        assert cli._add_section == mock_cli_dependencies[self.ADD_SECTION]
        assert cli._get_all_sections == mock_cli_dependencies[self.GET_ALL_SECTIONS]
        assert cli._add_flow == mock_cli_dependencies[self.ADD_FLOW]
        assert cli._create_events == mock_cli_dependencies[self.CREATE_EVENTS]
        assert cli._export_counts == mock_cli_dependencies[self.EXPORT_COUNTS]
        assert cli._cut_tracks == mock_cli_dependencies[self.CUT_TRACKS]
        assert cli._add_all_tracks == mock_cli_dependencies[self.ADD_ALL_TRACKS]
        assert cli._clear_all_tracks == mock_cli_dependencies[self.CLEAR_ALL_TRACKS]
        assert cli._progressbar == mock_cli_dependencies[self.PROGRESSBAR]

    def test_init_empty_tracks_cli_arg(
        self, mock_cli_dependencies: dict[str, Any]
    ) -> None:
        cli_args = CliArguments(
            True,
            False,
            track_files=[],
            sections_file="section_file.otflow",
            eventlist_filename="",
        )
        with pytest.raises(CliParseError, match=r"No ottrk files passed.*"):
            OTAnalyticsCli(cli_args, **mock_cli_dependencies)

    def test_init_no_section_cli_arg(
        self, mock_cli_dependencies: dict[str, Any]
    ) -> None:
        cli_args = CliArguments(
            True,
            False,
            track_files=[f"ottrk_file.{DEFAULT_TRACK_FILE_TYPE}"],
            sections_file="",
            eventlist_filename="",
        )
        with pytest.raises(CliParseError, match=r"No otflow file passed.*"):
            OTAnalyticsCli(cli_args, **mock_cli_dependencies)

    def test_validate_cli_args_no_tracks(self) -> None:
        cli_args = CliArguments(True, False, [], "section.otflow", "")
        with pytest.raises(CliParseError, match=r"No ottrk files passed.*"):
            OTAnalyticsCli._validate_cli_args(cli_args)

    def test_validate_cli_args_no_section(self) -> None:
        cli_args = CliArguments(
            True, False, [f"track.{DEFAULT_TRACK_FILE_TYPE}"], "", ""
        )
        with pytest.raises(CliParseError, match=r"No otflow file passed.*"):
            OTAnalyticsCli._validate_cli_args(cli_args)

    def test_parse_ottrk_files_with_subdirs(self, temp_tracks_directory: Path) -> None:
        tracks = OTAnalyticsCli._get_ottrk_files([str(temp_tracks_directory)])
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
        track_1 = f"path/to/foo.{DEFAULT_TRACK_FILE_TYPE}"
        track_2 = f"path/to/bar.{DEFAULT_TRACK_FILE_TYPE}"

        parsed_tracks = OTAnalyticsCli._get_ottrk_files([track_1, track_2])
        assert not parsed_tracks

    def test_parse_ottrk_files_single_file(self, temp_ottrk: Path) -> None:
        parsed_tracks = OTAnalyticsCli._get_ottrk_files([str(temp_ottrk)])
        assert temp_ottrk in parsed_tracks

    def test_parse_ottrk_files_multiple_files(
        self, temp_ottrk: Path, temp_tracks_directory: Path
    ) -> None:
        parsed_tracks = OTAnalyticsCli._get_ottrk_files(
            [str(temp_ottrk), str(temp_tracks_directory)]
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

    @pytest.mark.parametrize(
        "eventlist_filename,expected_filename",
        [("my_events", "my_events"), ("", DEFAULT_EVENTLIST_FILE_STEM)],
    )
    def test_determine_eventlist_save_path(
        self,
        eventlist_filename: str,
        expected_filename: str,
        mock_cli_dependencies: dict[str, Any],
    ) -> None:
        cli_args = Mock(spec=CliArguments)
        cli_args.eventlist_filename = eventlist_filename
        cli_args.track_files = Mock()
        cli_args.sections_file = Mock()
        cli = OTAnalyticsCli(cli_args, **mock_cli_dependencies)
        track_file = Path(f"path/to/track.{DEFAULT_TRACK_FILE_TYPE}")
        result = cli._determine_eventlist_save_path(track_file)
        assert result == Path(
            f"path/to/{expected_filename}.{DEFAULT_EVENTLIST_FILE_TYPE}"
        )

    def test_start_with_no_video_in_folder(
        self, temp_ottrk: Path, temp_section: Path, cli_dependencies: dict[str, Any]
    ) -> None:
        eventlist_filename = "my_events"
        cli_args = CliArguments(
            True, False, [str(temp_ottrk)], str(temp_section), eventlist_filename
        )
        cli = OTAnalyticsCli(cli_args, **cli_dependencies)
        cli.start()

        expected_event_list_file = temp_ottrk.with_name(
            f"{eventlist_filename}.{DEFAULT_EVENTLIST_FILE_TYPE}"
        )
        assert expected_event_list_file.exists()

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
