import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence
from unittest.mock import Mock, PropertyMock, call, patch

import pytest

from OTAnalytics.application.config import (
    DEFAULT_COUNTING_INTERVAL_IN_MINUTES,
    DEFAULT_DO_COUNTING,
    DEFAULT_DO_EVENTS,
    DEFAULT_EVENT_FORMATS,
    DEFAULT_LOG_FILE,
    DEFAULT_SAVE_NAME,
    DEFAULT_SAVE_SUFFIX,
)
from OTAnalytics.application.config_specification import OtConfigDefaultValueProvider
from OTAnalytics.application.datastore import VideoParser
from OTAnalytics.application.parser.config_parser import (
    AnalysisConfig,
    ExportConfig,
    OtConfig,
    StartDateMissing,
)
from OTAnalytics.application.parser.flow_parser import FlowParser
from OTAnalytics.application.project import Project
from OTAnalytics.domain import flow, section, video
from OTAnalytics.domain.flow import Flow
from OTAnalytics.domain.section import Section
from OTAnalytics.domain.video import Video
from OTAnalytics.plugin_parser.json_parser import parse_json
from OTAnalytics.plugin_parser.otconfig_parser import (
    ANALYSIS,
    COUNT_INTERVALS,
    DEBUG,
    DO_COUNTING,
    DO_EVENTS,
    EVENT_FORMATS,
    EXPORT,
    LOGFILE,
    NUM_PROCESSES,
    PATH,
    PROJECT,
    SAVE_NAME,
    SAVE_SUFFIX,
    TRACKS,
    FixMissingAnalysis,
    MultiFixer,
    OtConfigFormatFixer,
    OtConfigParser,
)
from tests.conftest import YieldFixture, do_nothing


@pytest.fixture
def mock_otconfig() -> OtConfig:
    project = Mock()
    track_files = Mock()
    analysis = Mock()
    analysis.tracks = track_files

    videos = Mock()
    sections = Mock()
    flows = Mock()
    remark = Mock()
    return OtConfig(project, analysis, videos, sections, flows, remark)


@pytest.fixture
def base_dir(test_data_tmp_dir: Path) -> YieldFixture[Path]:
    base_folder = test_data_tmp_dir / "my_base_folder"
    if base_folder.exists():
        shutil.rmtree(base_folder)
    base_folder.mkdir(exist_ok=False)
    yield base_folder
    shutil.rmtree(base_folder)


class TestOtConfigParser:
    def test_serialize_config(
        self, test_data_tmp_dir: Path, do_nothing_fixer: OtConfigFormatFixer
    ) -> None:
        video_parser = Mock(spec=VideoParser)
        flow_parser = Mock(spec=FlowParser)
        config_parser = OtConfigParser(
            video_parser=video_parser,
            flow_parser=flow_parser,
            format_fixer=do_nothing_fixer,
        )
        project = Project(name="My Test Project", start_date=datetime(2020, 1, 1))
        videos: list[Video] = []
        track_files: list[Path] = []
        sections: list[Section] = []
        flows: list[Flow] = []
        remark: str | None = "Comment"
        output = test_data_tmp_dir / "config.otconfig"
        serialized_videos = {video.VIDEOS: {"serialized": "videos"}}
        serialized_sections = {section.SECTIONS: {"serialized": "sections"}}
        serialized_remark = {"remark": "Comment"}
        serialized_analysis: dict = {
            ANALYSIS: {
                DO_EVENTS: DEFAULT_DO_EVENTS,
                DO_COUNTING: DEFAULT_DO_COUNTING,
                TRACKS: [],
                EXPORT: {
                    SAVE_NAME: DEFAULT_SAVE_NAME,
                    SAVE_SUFFIX: DEFAULT_SAVE_SUFFIX,
                    EVENT_FORMATS: list(DEFAULT_EVENT_FORMATS),
                    COUNT_INTERVALS: [DEFAULT_COUNTING_INTERVAL_IN_MINUTES],
                },
                NUM_PROCESSES: 1,
                LOGFILE: str(DEFAULT_LOG_FILE),
            }
        }

        video_parser.convert.return_value = serialized_videos
        flow_parser.convert.return_value = serialized_sections

        config_parser.serialize(
            project=project,
            video_files=videos,
            track_files=track_files,
            sections=sections,
            flows=flows,
            file=output,
            remark=remark,
        )

        serialized_content = parse_json(output)
        expected_content: dict[str, Any] = {PROJECT: project.to_dict()}
        expected_content |= serialized_videos
        expected_content |= serialized_analysis
        expected_content |= serialized_sections
        expected_content |= serialized_remark

        assert serialized_content == expected_content
        assert video_parser.convert.call_args_list == [
            call(videos, relative_to=test_data_tmp_dir)
        ]
        assert flow_parser.convert.call_args_list == [call(sections, flows)]

    @patch("OTAnalytics.plugin_parser.otconfig_parser.OtConfigParser.serialize")
    def test_serialize_from_config(
        self, mock_serialize: Mock, mock_otconfig: OtConfig
    ) -> None:
        save_path = Path("path/to/my/file.otconfig")
        serializer = OtConfigParser(Mock(), Mock(), Mock())

        serializer.serialize_from_config(mock_otconfig, save_path)

        mock_serialize.assert_called_once_with(
            mock_otconfig.project,
            mock_otconfig.videos,
            mock_otconfig.analysis.track_files,
            mock_otconfig.sections,
            mock_otconfig.flows,
            save_path,
            mock_otconfig.remark,
        )

    def test_parse_config(
        self, otconfig_file: Path, do_nothing_fixer: OtConfigFormatFixer
    ) -> None:
        video_parser = Mock(spec=VideoParser)
        flow_parser = Mock(spec=FlowParser)
        config_parser = OtConfigParser(
            video_parser=video_parser,
            flow_parser=flow_parser,
            format_fixer=do_nothing_fixer,
        )
        project = Project(
            name="My Test Project",
            start_date=(datetime(2020, 1, 1, 11, 11, 17, tzinfo=timezone.utc)),
        )
        videos: Sequence[Video] = ()
        sections: Sequence[Section] = ()
        flows: Sequence[Flow] = ()
        tracks = {
            otconfig_file.parent
            / "Testvideo_Cars-Cyclist_FR20_2020-01-01_00-00-00.ottrk"
        }
        remark = ""
        serialized_videos = {video.VIDEOS: {"serialized": "videos"}}
        serialized_flows = {
            section.SECTIONS: {"serialized": "sections"},
            flow.FLOWS: {"serialized": "flows"},
        }
        video_parser.convert.return_value = serialized_videos
        flow_parser.convert.return_value = serialized_flows
        video_parser.parse_list.return_value = videos
        flow_parser.parse_content.return_value = sections, flows

        config = config_parser.parse(file=otconfig_file)
        expected_export_config = ExportConfig(
            save_name="my_name",
            save_suffix="my_suffix",
            event_formats={"csv", "xlsx"},
            count_intervals={2, 3, 4},
        )
        expected_analysis_config = AnalysisConfig(
            do_events=True,
            do_counting=True,
            track_files=tracks,
            export_config=expected_export_config,
            num_processes=2,
            logfile=Path("path/to/my/log_dir"),
        )

        expected_config = OtConfig(
            project=project,
            analysis=expected_analysis_config,
            videos=videos,
            sections=sections,
            flows=flows,
            remark=remark,
        )
        assert config == expected_config

    def test_parse_config_without_analysis(
        self, test_data_dir: Path, otconfig_file: Path
    ) -> None:
        video_parser = Mock(spec=VideoParser)
        flow_parser = Mock(spec=FlowParser)
        format_fixer = Mock(spec=OtConfigFormatFixer)
        format_fixer.fix.side_effect = do_nothing
        config_parser = OtConfigParser(
            video_parser=video_parser,
            flow_parser=flow_parser,
            format_fixer=format_fixer,
        )
        videos: Sequence[Video] = ()
        sections: Sequence[Section] = ()
        flows: Sequence[Flow] = ()

        serialized_videos = {video.VIDEOS: {"serialized": "videos"}}
        serialized_flows = {
            section.SECTIONS: {"serialized": "sections"},
            flow.FLOWS: {"serialized": "flows"},
        }
        video_parser.convert.return_value = serialized_videos
        flow_parser.convert.return_value = serialized_flows
        video_parser.parse_list.return_value = videos
        flow_parser.parse_content.return_value = sections, flows

        config_parser.parse(file=otconfig_file)

        format_fixer.fix.assert_called_once()

    def test_validate(self) -> None:
        project = Project("My Name", None)
        with pytest.raises(StartDateMissing):
            OtConfigParser._validate_data(project)

    def test_parse_videos_alternative_files(self, base_dir: Path) -> None:
        expected_in_config_first_video = Path("relpath/to/video/first.mp4")
        expected_in_config_second_video = Path("relpath/to/video/second.mp4")

        actual_first_video = base_dir / expected_in_config_first_video.name
        actual_second_video = base_dir / expected_in_config_second_video.name
        actual_first_video.touch()
        actual_second_video.touch()

        video_entries = [
            {PATH: expected_in_config_first_video},
            {PATH: expected_in_config_second_video},
        ]
        video_parser = Mock()
        parser = OtConfigParser(Mock(), video_parser, Mock())
        parser._parse_videos(video_entries, base_dir)

        video_parser.parse_list.assert_called_once_with(
            [
                {PATH: expected_in_config_first_video.name},
                {PATH: expected_in_config_second_video.name},
            ],
            base_dir,
        )
        actual_first_video.unlink()
        actual_second_video.unlink()


class TestMultiFixer:
    def test_fix_all(self) -> None:
        original_content: dict = {}
        fixed_content_1: dict = {}
        fixed_content_2: dict = {}
        fixer_1 = Mock(spec=OtConfigFormatFixer)
        fixer_1.fix.return_value = fixed_content_1
        fixer_2 = Mock(spec=OtConfigFormatFixer)
        fixer_2.fix.return_value = fixed_content_2
        fixer = MultiFixer([fixer_1, fixer_2])

        fixed_content = fixer.fix(original_content)

        assert fixed_content == fixed_content_2
        fixer_1.fix.assert_called_once_with(original_content)
        fixer_2.fix.assert_called_once_with(fixed_content_1)


class TestFixMissingAnalysis:
    def test_fix(self) -> None:
        do_events = True
        do_counting = True
        track_files: set = set()
        num_processes = 4
        logfile = "logfile.log"
        debug = True
        event_formats = ["csv", "xlsx"]
        save_name = "my_name"
        save_suffix = "my_suffix"
        count_intervals = [2, 3, 4]
        export = {
            EVENT_FORMATS: event_formats,
            SAVE_NAME: save_name,
            SAVE_SUFFIX: save_suffix,
            COUNT_INTERVALS: count_intervals,
        }
        expected_content = {
            ANALYSIS: {
                DO_EVENTS: do_events,
                DO_COUNTING: do_counting,
                TRACKS: track_files,
                EXPORT: export,
                NUM_PROCESSES: num_processes,
                LOGFILE: logfile,
                DEBUG: debug,
            }
        }

        flow_parser = Mock(spec=FlowParser)
        flow_parser.parse.return_value = ([], [])

        value_provider = Mock(spec=OtConfigDefaultValueProvider)
        type(value_provider).do_events = PropertyMock(return_value=do_events)
        type(value_provider).do_counting = PropertyMock(return_value=do_counting)
        type(value_provider).track_files = PropertyMock(return_value=track_files)
        type(value_provider).event_formats = PropertyMock(return_value=event_formats)
        type(value_provider).save_name = PropertyMock(return_value=save_name)
        type(value_provider).save_suffix = PropertyMock(return_value=save_suffix)
        type(value_provider).count_intervals = PropertyMock(
            return_value=count_intervals
        )
        type(value_provider).num_processes = PropertyMock(return_value=num_processes)
        type(value_provider).log_file = PropertyMock(return_value=logfile)
        type(value_provider).debug = PropertyMock(return_value=debug)
        fixer = FixMissingAnalysis(run_config=value_provider)

        original_content: dict = {}

        fixed_content = fixer.fix(original_content)

        assert fixed_content == expected_content
