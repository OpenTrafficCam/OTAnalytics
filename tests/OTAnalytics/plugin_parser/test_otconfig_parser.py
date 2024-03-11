from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence
from unittest.mock import Mock, PropertyMock, call

from OTAnalytics.application.config_specification import OtConfigDefaultValueProvider
from OTAnalytics.application.datastore import VideoParser
from OTAnalytics.application.parser.config_parser import (
    AnalysisConfig,
    ExportConfig,
    OtConfig,
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
    PROJECT,
    SAVE_NAME,
    SAVE_SUFFIX,
    TRACKS,
    FixMissingAnalysis,
    MultiFixer,
    OtConfigFormatFixer,
    OtConfigParser,
)
from tests.conftest import do_nothing


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
        sections: list[Section] = []
        flows: list[Flow] = []
        output = test_data_tmp_dir / "config.otconfig"
        serialized_videos = {video.VIDEOS: {"serialized": "videos"}}
        serialized_sections = {section.SECTIONS: {"serialized": "sections"}}
        video_parser.convert.return_value = serialized_videos
        flow_parser.convert.return_value = serialized_sections

        config_parser.serialize(
            project=project,
            video_files=videos,
            sections=sections,
            flows=flows,
            file=output,
        )

        serialized_content = parse_json(output)
        expected_content: dict[str, Any] = {PROJECT: project.to_dict()}
        expected_content |= serialized_videos
        expected_content |= serialized_sections

        assert serialized_content == expected_content
        assert video_parser.convert.call_args_list == [
            call(videos, relative_to=test_data_tmp_dir)
        ]
        assert flow_parser.convert.call_args_list == [call(sections, flows)]

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
