from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, call

import pytest

from OTAnalytics import version
from OTAnalytics.application.datastore import VideoMetadata, VideoParser
from OTAnalytics.domain import flow, geometry, section
from OTAnalytics.domain.event import EVENT_LIST, Event, EventType
from OTAnalytics.domain.flow import Flow, FlowId
from OTAnalytics.domain.geometry import (
    DirectionVector2D,
    ImageCoordinate,
    RelativeOffsetCoordinate,
)
from OTAnalytics.domain.section import (
    SECTIONS,
    Area,
    Coordinate,
    LineSection,
    Section,
    SectionId,
)
from OTAnalytics.domain.track import (
    Detection,
    Track,
    TrackClassificationCalculator,
    TrackId,
    TrackImage,
)
from OTAnalytics.domain.track_repository import TrackRepository
from OTAnalytics.domain.video import Video
from OTAnalytics.plugin_datastore.python_track_store import (
    ByMaxConfidence,
    PythonTrack,
    PythonTrackDataset,
)
from OTAnalytics.plugin_parser import dataformat_versions, ottrk_dataformat
from OTAnalytics.plugin_parser.json_parser import write_json, write_json_bz2
from OTAnalytics.plugin_parser.otvision_parser import (
    DEFAULT_TRACK_LENGTH_LIMIT,
    EVENT_FORMAT_VERSION,
    METADATA,
    SECTION_FORMAT_VERSION,
    VERSION,
    VERSION_1_0,
    VERSION_1_1,
    CachedVideo,
    CachedVideoParser,
    DetectionFixer,
    InvalidSectionData,
    MetadataFixer,
    Otdet_Version_1_0_to_1_1,
    Otdet_Version_1_0_To_1_2,
    OtEventListParser,
    OtFlowParser,
    OttrkFormatFixer,
    OttrkParser,
    PythonDetectionParser,
    TrackLengthLimit,
    Version,
)
from tests.conftest import TrackBuilder, assert_track_datasets_equal


@pytest.fixture
def track_builder_setup_with_sample_data(track_builder: TrackBuilder) -> TrackBuilder:
    return append_sample_data(track_builder, frame_offset=0, microsecond_offset=0)


def append_sample_data(
    track_builder: TrackBuilder,
    frame_offset: int = 0,
    microsecond_offset: int = 0,
) -> TrackBuilder:
    track_builder.add_frame(frame_offset + 1)
    track_builder.add_microsecond(microsecond_offset + 1)
    track_builder.append_detection()

    track_builder.add_frame(frame_offset + 2)
    track_builder.add_microsecond(microsecond_offset + 2)
    track_builder.append_detection()

    track_builder.add_frame(frame_offset + 3)
    track_builder.add_microsecond(microsecond_offset + 3)
    track_builder.append_detection()

    track_builder.add_frame(frame_offset + 4)
    track_builder.add_microsecond(microsecond_offset + 4)
    track_builder.append_detection()

    track_builder.add_frame(frame_offset + 5)
    track_builder.add_microsecond(microsecond_offset + 5)
    track_builder.append_detection()

    return track_builder


@pytest.fixture
def mocked_track_repository() -> Mock:
    repository = Mock(spec=TrackRepository)
    repository.get_for.return_value = None
    return repository


@pytest.fixture
def mocked_track_file_repository() -> Mock:
    repository = Mock(spec=TrackRepository)
    repository.get_all.return_value = set()
    return repository


class TestVersion_1_0_To_1_1:
    def test_fix_x_y_coordinates(
        self, track_builder_setup_with_sample_data: TrackBuilder
    ) -> None:
        track_builder_setup_with_sample_data.set_otdet_version(str(VERSION_1_0))
        input_detection = track_builder_setup_with_sample_data.create_detection()
        serialized_detection = track_builder_setup_with_sample_data.serialize_detection(
            input_detection, False, False
        )
        expected_detection = serialized_detection.copy()
        expected_detection[ottrk_dataformat.X] = -5
        expected_detection[ottrk_dataformat.Y] = -5
        fixer = Otdet_Version_1_0_to_1_1()

        fixed = fixer.fix(serialized_detection, VERSION_1_0)

        assert fixed == expected_detection


class TestVersion_1_1_To_1_2:
    def test_fix_occurrence(
        self, track_builder_setup_with_sample_data: TrackBuilder
    ) -> None:
        track_builder_setup_with_sample_data.set_otdet_version(str(VERSION_1_1))
        detection = track_builder_setup_with_sample_data.create_detection()
        serialized_detection = track_builder_setup_with_sample_data.serialize_detection(
            detection, False, False
        )
        expected_detection = serialized_detection.copy()
        serialized_detection[
            ottrk_dataformat.OCCURRENCE
        ] = detection.occurrence.strftime(ottrk_dataformat.DATE_FORMAT)

        fixer = Otdet_Version_1_0_To_1_2()

        fixed = fixer.fix(serialized_detection, VERSION_1_1)

        assert fixed == expected_detection


class TestOttrkFormatFixer:
    def test_run_all_fixer(
        self, track_builder_setup_with_sample_data: TrackBuilder
    ) -> None:
        otdet_version = Version.from_str(
            track_builder_setup_with_sample_data.otdet_version
        )
        ottrk_version = Version.from_str(
            track_builder_setup_with_sample_data.ottrk_version
        )
        content = track_builder_setup_with_sample_data.build_ottrk()
        metadata = content[ottrk_dataformat.METADATA]
        detections = track_builder_setup_with_sample_data.build_serialized_detections()
        some_fixer = Mock(spec=DetectionFixer)
        other_fixer = Mock(spec=DetectionFixer)
        some_fixer.fix.side_effect = lambda detection, _: detection
        other_fixer.fix.side_effect = lambda detection, _: detection
        some_metadata_fixer = Mock(spec=MetadataFixer)
        other_metadata_fixer = Mock(spec=MetadataFixer)
        some_metadata_fixer.fix.side_effect = lambda metadata, _: metadata
        other_metadata_fixer.fix.side_effect = lambda metadata, _: metadata
        detection_fixes: list[DetectionFixer] = [some_fixer, other_fixer]
        metadata_fixes: list[MetadataFixer] = [
            some_metadata_fixer,
            other_metadata_fixer,
        ]
        fixer = OttrkFormatFixer(detection_fixes, metadata_fixes)

        fixed_content = fixer.fix(content)

        assert fixed_content == content
        assert some_fixer.fix.call_args_list == [
            call(detection, otdet_version) for detection in detections
        ]
        assert other_fixer.fix.call_args_list == [
            call(detection, otdet_version) for detection in detections
        ]
        some_metadata_fixer.fix.assert_called_with(metadata, ottrk_version)
        other_metadata_fixer.fix.assert_called_with(metadata, ottrk_version)

    def test_no_fixes_in_newest_version(
        self, track_builder_setup_with_sample_data: TrackBuilder
    ) -> None:
        track_builder_setup_with_sample_data.set_otdet_version("1.2")
        content = track_builder_setup_with_sample_data.build_ottrk()
        fixer = OttrkFormatFixer([])

        fixed_content = fixer.fix(content)

        assert fixed_content == content


class TestOttrkParser:
    @pytest.fixture
    def ottrk_parser(
        self, mocked_track_repository: Mock, mocked_track_file_repository: Mock
    ) -> OttrkParser:
        calculator = ByMaxConfidence()
        detection_parser = PythonDetectionParser(
            calculator,
            mocked_track_repository,
            track_length_limit=DEFAULT_TRACK_LENGTH_LIMIT,
        )
        return OttrkParser(detection_parser)

    def test_parse_whole_ottrk(
        self, ottrk_parser: OttrkParser, ottrk_path: Path
    ) -> None:
        # TODO What is the expected result?
        ottrk_parser.parse(ottrk_path)

    @pytest.mark.parametrize(
        "version,track_id", [("1.0", "legacy#legacy#1"), ("1.1", "1#1#1")]
    )
    def test_parse_ottrk_sample(
        self,
        test_data_tmp_dir: Path,
        track_builder_setup_with_sample_data: TrackBuilder,
        ottrk_parser: OttrkParser,
        version: str,
        track_id: str,
    ) -> None:
        track_builder_setup_with_sample_data.set_ottrk_version(version)
        ottrk_data = track_builder_setup_with_sample_data.build_ottrk()
        ottrk_file = test_data_tmp_dir / "sample_file.ottrk"
        write_json_bz2(ottrk_data, ottrk_file)
        parse_result = ottrk_parser.parse(ottrk_file)

        example_track_builder = TrackBuilder()
        example_track_builder.add_track_id(track_id)
        append_sample_data(example_track_builder)
        expected_track = example_track_builder.build_track()
        expected_detection_classes = frozenset(
            ["person", "bus", "boat", "truck", "car", "motorcycle", "bicycle", "train"]
        )
        assert_track_datasets_equal(
            parse_result.tracks, PythonTrackDataset.from_list([expected_track])
        )
        assert (
            parse_result.detection_metadata.detection_classes
            == expected_detection_classes
        )
        assert parse_result.video_metadata == VideoMetadata(
            path="myhostname_file.mp4",
            recorded_start_date=datetime(
                year=2020,
                month=1,
                day=1,
                hour=0,
                minute=0,
                tzinfo=timezone.utc,
            ),
            expected_duration=None,
            recorded_fps=20.0,
            actual_fps=None,
            number_of_frames=60,
        )
        ottrk_file.unlink()


class TestPythonDetectionParser:
    @pytest.fixture
    def parser(self, mocked_track_repository: Mock) -> PythonDetectionParser:
        return PythonDetectionParser(
            ByMaxConfidence(),
            mocked_track_repository,
        )

    def test_parse_detections_output_has_same_order_as_input(
        self,
        track_builder_setup_with_sample_data: TrackBuilder,
        parser: PythonDetectionParser,
    ) -> None:
        detections: list[
            dict
        ] = track_builder_setup_with_sample_data.build_serialized_detections()
        metadata_video = track_builder_setup_with_sample_data.get_metadata()[
            ottrk_dataformat.VIDEO
        ]

        result_sorted_input = parser._parse_detections(
            detections,
            metadata_video,
            TrackId,
        )
        unsorted_detections = [detections[-1], detections[0]] + detections[1:-1]
        result_unsorted_input = parser._parse_detections(
            unsorted_detections,
            metadata_video,
            TrackId,
        )

        expected_sorted = {
            TrackId("1"): track_builder_setup_with_sample_data.build_detections()
        }

        assert expected_sorted == result_sorted_input
        assert expected_sorted != result_unsorted_input

    def test_parse_tracks(
        self,
        track_builder_setup_with_sample_data: TrackBuilder,
        parser: PythonDetectionParser,
    ) -> None:
        detections: list[
            dict
        ] = track_builder_setup_with_sample_data.build_serialized_detections()
        metadata_video = track_builder_setup_with_sample_data.get_metadata()[
            ottrk_dataformat.VIDEO
        ]

        result_sorted_input = parser.parse_tracks(detections, metadata_video)
        unsorted_detections = [detections[-1], detections[0]] + detections[1:-1]
        result_unsorted_input = parser.parse_tracks(unsorted_detections, metadata_video)

        expected_sorted = PythonTrackDataset.from_list(
            [track_builder_setup_with_sample_data.build_track()]
        )
        assert_track_datasets_equal(result_sorted_input, expected_sorted)
        assert_track_datasets_equal(result_unsorted_input, expected_sorted)

    def test_parse_tracks_merge_with_existing(
        self,
        track_builder_setup_with_sample_data: TrackBuilder,
        mocked_track_repository: Mock,
        parser: PythonDetectionParser,
    ) -> None:
        detections: list[
            dict
        ] = track_builder_setup_with_sample_data.build_serialized_detections()
        deserialized_detections = (
            track_builder_setup_with_sample_data.build_detections()
        )
        metadata_video = track_builder_setup_with_sample_data.get_metadata()[
            ottrk_dataformat.VIDEO
        ]
        existing_track_builder = TrackBuilder()
        append_sample_data(
            existing_track_builder,
            frame_offset=0,
            microsecond_offset=len(detections),
        )
        existing_track = existing_track_builder.build_track()
        merged_classification = "car"
        classificator = Mock(spec=TrackClassificationCalculator)
        classificator.calculate.return_value = merged_classification
        mocked_track_repository.get_for.return_value = existing_track
        all_detections = deserialized_detections + existing_track.detections
        merged_track = PythonTrack(
            existing_track.id, merged_classification, all_detections
        )

        result_sorted_input = parser.parse_tracks(detections, metadata_video)

        expected_sorted = PythonTrackDataset.from_list([merged_track])

        assert_track_datasets_equal(result_sorted_input, expected_sorted)

    @pytest.mark.parametrize(
        "track_length_limit",
        [
            TrackLengthLimit(20, 12000),
            TrackLengthLimit(0, 4),
        ],
    )
    def test_parse_tracks_consider_minimum_length(
        self,
        mocked_track_repository: Mock,
        track_builder_setup_with_sample_data: TrackBuilder,
        track_length_limit: TrackLengthLimit,
    ) -> None:
        parser = PythonDetectionParser(
            ByMaxConfidence(),
            mocked_track_repository,
            track_length_limit,
        )
        detections: list[
            dict
        ] = track_builder_setup_with_sample_data.build_serialized_detections()

        metadata_video = track_builder_setup_with_sample_data.get_metadata()[
            ottrk_dataformat.VIDEO
        ]
        result_sorted_input = parser.parse_tracks(detections, metadata_video).as_list()

        assert len(result_sorted_input) == 0

    def assert_detection_equal(self, d1: Detection, d2: Detection) -> None:
        assert d1.classification == d2.classification
        assert d1.confidence == d2.confidence
        assert d1.x == d2.x
        assert d1.y == d2.y
        assert d1.w == d2.w
        assert d1.h == d2.h
        assert d1.frame == d2.frame
        assert d1.occurrence == d2.occurrence
        assert d1.video_name == d2.video_name
        assert d1.interpolated_detection == d2.interpolated_detection
        assert d1.track_id == d2.track_id


class TestOtFlowParser:
    def test_parse_sections_and_flows(self, test_data_tmp_dir: Path) -> None:
        first_coordinate = Coordinate(0, 0)
        second_coordinate = Coordinate(1, 1)
        third_coordinate = Coordinate(1, 0)
        line_section_id = SectionId("some")
        line_section: Section = LineSection(
            id=line_section_id,
            name="some",
            relative_offset_coordinates={
                EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0)
            },
            plugin_data={"key_1": "some_data", "key_2": "some_data"},
            coordinates=[first_coordinate, second_coordinate],
        )
        area_section_id = SectionId("other")
        area_section: Section = Area(
            id=area_section_id,
            name="other",
            relative_offset_coordinates={
                EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0)
            },
            plugin_data={"key_1": "some_data", "key_2": "some_data"},
            coordinates=[
                first_coordinate,
                second_coordinate,
                third_coordinate,
                first_coordinate,
            ],
        )
        some_flow_id = FlowId("1")
        some_flow_name = "some to other"
        some_flow_distance = 1
        some_flow = Flow(
            some_flow_id,
            name=some_flow_name,
            start=line_section_id,
            end=area_section_id,
            distance=some_flow_distance,
        )
        other_flow_id = FlowId("2")
        other_flow_name = "other to some"
        other_flow_distance = None
        other_flow = Flow(
            other_flow_id,
            name=other_flow_name,
            start=area_section_id,
            end=line_section_id,
            distance=other_flow_distance,
        )
        json_file = test_data_tmp_dir / "section.otflow"
        json_file.touch()
        sections = [line_section, area_section]
        flows = [some_flow, other_flow]
        parser = OtFlowParser()
        parser.serialize(sections, flows, json_file)

        parsed_sections, parsed_flows = parser.parse(json_file)

        assert parsed_sections == sections
        assert len(parsed_flows) == 2

        some_parsed_flow = parsed_flows[0]
        assert some_parsed_flow.id == some_flow_id
        assert some_parsed_flow.name == some_flow_name
        assert some_parsed_flow.start == line_section_id
        assert some_parsed_flow.end == area_section_id
        assert some_parsed_flow.distance == some_flow_distance

        other_parsed_flow = parsed_flows[1]
        assert other_parsed_flow.id == other_flow_id
        assert other_parsed_flow.name == other_flow_name
        assert other_parsed_flow.start == area_section_id
        assert other_parsed_flow.end == line_section_id
        assert other_parsed_flow.distance == other_flow_distance

    def test_validate(self) -> None:
        parser = OtFlowParser()
        pytest.raises(
            InvalidSectionData, parser.parse_section, {section.TYPE: section.LINE}
        )

    def test_convert_section(self) -> None:
        some_section_id = SectionId("some")
        some_section: Section = LineSection(
            id=some_section_id,
            name="some",
            relative_offset_coordinates={
                EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0)
            },
            plugin_data={},
            coordinates=[Coordinate(0, 0), Coordinate(1, 1)],
        )
        other_section_id = SectionId("other")
        other_section: Section = LineSection(
            id=other_section_id,
            name="other",
            relative_offset_coordinates={
                EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0)
            },
            plugin_data={},
            coordinates=[Coordinate(1, 0), Coordinate(0, 1)],
        )
        some_flow = Flow(
            FlowId("1"),
            name="some to other",
            start=some_section_id,
            end=other_section_id,
            distance=1,
        )
        sections = [some_section, other_section]
        flows = [some_flow]
        parser = OtFlowParser()

        content = parser.convert(sections, flows)

        assert content == {
            section.SECTIONS: [some_section.to_dict(), other_section.to_dict()],
            flow.FLOWS: [some_flow.to_dict()],
        }

    def test_parse_plugin_data_no_entry(self, test_data_tmp_dir: Path) -> None:
        start = Coordinate(0, 0)
        end = Coordinate(1, 1)
        expected: Section = LineSection(
            id=SectionId("some"),
            name="some",
            relative_offset_coordinates={
                EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0)
            },
            plugin_data={},
            coordinates=[start, end],
        )

        section_data = {
            section.SECTIONS: [
                {
                    section.ID: "some",
                    section.NAME: "some",
                    section.TYPE: "line",
                    section.RELATIVE_OFFSET_COORDINATES: {
                        EventType.SECTION_ENTER.serialize(): {
                            geometry.X: 0,
                            geometry.Y: 0,
                        }
                    },
                    section.COORDINATES: [
                        {
                            geometry.X: 0,
                            geometry.Y: 0,
                        },
                        {
                            geometry.X: 1,
                            geometry.Y: 1,
                        },
                    ],
                }
            ],
            flow.FLOWS: [],
        }
        save_path = test_data_tmp_dir / "sections.otflow"
        write_json(section_data, save_path)

        parser = OtFlowParser()
        sections, _ = parser.parse(save_path)

        assert sections == [expected]

    def test_parse_plugin_data_with_plugin_data(self, test_data_tmp_dir: Path) -> None:
        start = Coordinate(0, 0)
        end = Coordinate(1, 1)
        expected: Section = LineSection(
            id=SectionId("some"),
            name="some",
            relative_offset_coordinates={
                EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0)
            },
            plugin_data={"key_1": "some_data", "1": "some_data"},
            coordinates=[start, end],
        )

        section_data = {
            section.SECTIONS: [
                {
                    section.ID: "some",
                    section.NAME: "some",
                    section.TYPE: "line",
                    section.RELATIVE_OFFSET_COORDINATES: {
                        EventType.SECTION_ENTER.serialize(): {
                            geometry.X: 0,
                            geometry.Y: 0,
                        }
                    },
                    section.COORDINATES: [
                        {geometry.X: 0, geometry.Y: 0},
                        {geometry.X: 1, geometry.Y: 1},
                    ],
                    section.PLUGIN_DATA: {"key_1": "some_data", "1": "some_data"},
                }
            ],
            flow.FLOWS: [],
        }
        save_path = test_data_tmp_dir / "sections.otflow"
        write_json(section_data, save_path)

        parser = OtFlowParser()
        sections, _ = parser.parse(save_path)

        assert sections == [expected]


class TestOtEventListParser:
    def test_convert_event(self, test_data_tmp_dir: Path) -> None:
        road_user_id = "1"
        road_user_type = "car"
        hostname = "myhostname"
        section_id = SectionId("N")
        direction_vector = DirectionVector2D(1, 0)
        video_name = "my_video_name.mp4"
        first_event = Event(
            road_user_id=road_user_id,
            road_user_type=road_user_type,
            hostname=hostname,
            occurrence=datetime(2022, 1, 1, 0, 0, 0, 0),
            frame_number=1,
            section_id=section_id,
            event_coordinate=ImageCoordinate(0, 0),
            event_type=EventType.SECTION_ENTER,
            direction_vector=direction_vector,
            video_name=video_name,
        )
        second_event = Event(
            road_user_id=road_user_id,
            road_user_type=road_user_type,
            hostname=hostname,
            occurrence=datetime(2022, 1, 1, 0, 0, 0, 10),
            frame_number=2,
            section_id=section_id,
            event_coordinate=ImageCoordinate(10, 0),
            event_type=EventType.SECTION_LEAVE,
            direction_vector=direction_vector,
            video_name=video_name,
        )
        line_section = LineSection(
            id=SectionId("N"),
            name="N",
            relative_offset_coordinates={
                EventType.SECTION_ENTER: RelativeOffsetCoordinate(0.5, 0.5),
                EventType.SECTION_LEAVE: RelativeOffsetCoordinate(0.5, 0.5),
            },
            plugin_data={"foo": "bar"},
            coordinates=[Coordinate(0, 0), Coordinate(1, 0)],
        )
        area_section = Area(
            id=SectionId("S"),
            name="S",
            relative_offset_coordinates={
                EventType.SECTION_ENTER: RelativeOffsetCoordinate(0.5, 0.5),
                EventType.SECTION_LEAVE: RelativeOffsetCoordinate(0.5, 0.5),
            },
            plugin_data={"foo": "bar"},
            coordinates=[
                Coordinate(0, 0),
                Coordinate(0, 10),
                Coordinate(10, 10),
                Coordinate(10, 0),
                Coordinate(0, 0),
            ],
        )
        events = [first_event, second_event]
        sections = [line_section, area_section]

        event_list_parser = OtEventListParser()
        content = event_list_parser._convert(events, sections)

        assert content == {
            METADATA: {
                VERSION: version.__version__,
                SECTION_FORMAT_VERSION: dataformat_versions.otsection_version(),
                EVENT_FORMAT_VERSION: dataformat_versions.otevent_version(),
            },
            SECTIONS: [line_section.to_dict(), area_section.to_dict()],
            EVENT_LIST: [first_event.to_dict(), second_event.to_dict()],
        }

    def test_serialize_events(
        self, tracks: list[Track], sections: list[Section], test_data_tmp_dir: Path
    ) -> None:
        event_list_parser = OtEventListParser()
        event_list_file = test_data_tmp_dir / "eventlist.json"
        event_list_parser.serialize([], sections, event_list_file)
        assert event_list_file.exists()


class TestCachedVideo:
    def test_cache_frames(self, test_data_tmp_dir: Path) -> None:
        video_file = test_data_tmp_dir / "video.mp4"
        video_file.touch()
        image = Mock(spec=TrackImage)
        video = Mock(spec=Video)
        video.get_frame.return_value = image

        cached_video = CachedVideo(video)

        first_returned_frame = cached_video.get_frame(0)
        second_returned_frame = cached_video.get_frame(0)

        video.get_frame.assert_called_once_with(0)

        assert first_returned_frame == image
        assert second_returned_frame is first_returned_frame

    def test_get_path(self) -> None:
        original_path = Path(".")
        other = Mock(spec=Video)
        other.get_path.return_value = original_path
        cached_video = CachedVideo(other)

        path = cached_video.get_path()

        other.get_path.assert_called_once()
        assert path is original_path

    def test_to_dict(self) -> None:
        base_path = Path(".")
        original_dict: dict = {}
        other = Mock(spec=Video)
        other.to_dict.return_value = original_dict
        cached_video = CachedVideo(other)

        cached_dict = cached_video.to_dict(base_path)

        other.to_dict.assert_called_once()
        assert cached_dict is original_dict


class TestCachedVideoParser:
    def test_parse_to_cached_video(self, test_data_tmp_dir: Path) -> None:
        video_file = test_data_tmp_dir / "video.mp4"
        video_file.touch()
        video = Mock(spec=Video)
        video_parser = Mock(spec=VideoParser)
        video_parser.parse.return_value = video

        cached_parser = CachedVideoParser(video_parser)

        parsed_video = cached_parser.parse(video_file)

        assert isinstance(parsed_video, CachedVideo)
        assert parsed_video.other == video

    def test_parse_list_to_cached_videos(self, test_data_tmp_dir: Path) -> None:
        content: list[dict] = [{}]
        base_folder = test_data_tmp_dir
        video1 = Mock(spec=Video)
        video2 = Mock(spec=Video)
        video_parser = Mock(spec=VideoParser)
        video_parser.parse_list.return_value = [video1, video2]

        cached_parser = CachedVideoParser(video_parser)

        parsed_videos = cached_parser.parse_list(content, base_folder)

        assert all(
            isinstance(parsed_video, CachedVideo) for parsed_video in parsed_videos
        )
        assert len(parsed_videos) == 2
        if isinstance(parsed_videos[0], CachedVideo):
            assert parsed_videos[0].other == video1
        if isinstance(parsed_videos[1], CachedVideo):
            assert parsed_videos[1].other == video2

    def test_convert_delegates_to_other(self, test_data_tmp_dir: Path) -> None:
        video1 = Mock(spec=Video)
        video2 = Mock(spec=Video)
        expected_result: dict = {}
        video_parser = Mock(spec=VideoParser)
        video_parser.convert.return_value = expected_result

        cached_parser = CachedVideoParser(video_parser)

        result = cached_parser.convert([video1, video2], test_data_tmp_dir)

        assert expected_result is result
