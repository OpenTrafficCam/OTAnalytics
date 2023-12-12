from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence
from unittest.mock import Mock, call

from OTAnalytics.application.datastore import FlowParser, VideoParser
from OTAnalytics.application.parser.config_parser import (
    AnalysisConfig,
    ExportConfig,
    OtConfig,
)
from OTAnalytics.application.project import Project
from OTAnalytics.domain import flow, section, video
from OTAnalytics.domain.flow import Flow
from OTAnalytics.domain.section import Section
from OTAnalytics.domain.video import Video
from OTAnalytics.plugin_parser.json_parser import parse_json
from OTAnalytics.plugin_parser.otconfig_parser import PROJECT, OtConfigParser


class TestOtConfigParser:
    def test_serialize_config(self, test_data_tmp_dir: Path) -> None:
        video_parser = Mock(spec=VideoParser)
        flow_parser = Mock(spec=FlowParser)
        config_parser = OtConfigParser(
            video_parser=video_parser,
            flow_parser=flow_parser,
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

    def test_parse_config(self, test_data_tmp_dir: Path, otconfig_file: Path) -> None:
        video_parser = Mock(spec=VideoParser)
        flow_parser = Mock(spec=FlowParser)
        config_parser = OtConfigParser(
            video_parser=video_parser,
            flow_parser=flow_parser,
        )
        project = Project(
            name="My Test Project",
            start_date=(datetime(2020, 1, 1, 11, 11, 17, tzinfo=timezone.utc)),
        )
        videos: Sequence[Video] = ()
        sections: Sequence[Section] = ()
        flows: Sequence[Flow] = ()
        otflow = Path(
            "tests/data/Testvideo_Cars-Cyclist_FR20_2020-01-01_00-00-00.otflow"
        )
        tracks = {
            Path("tests/data/Testvideo_Cars-Cyclist_FR20_2020-01-01_00-00-00.ottrk")
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
            event_format="csv",
            count_intervals={2, 3, 4},
        )
        expected_analysis_config = AnalysisConfig(
            do_events=True,
            do_counting=True,
            otflow_file=otflow,
            track_files=tracks,
            export_config=expected_export_config,
            num_processes=2,
            logfile=Path("path/to/my/log_dir"),
            debug=True,
        )

        expected_config = OtConfig(
            project=project,
            analysis=expected_analysis_config,
            videos=videos,
            sections=sections,
            flows=flows,
        )
        assert config == expected_config
