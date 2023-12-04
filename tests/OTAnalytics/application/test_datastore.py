from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Sequence
from unittest.mock import Mock

import pytest
from numpy import array, int32
from PIL import Image

from OTAnalytics.application.datastore import (
    ConfigParser,
    Datastore,
    EventListParser,
    FlowParser,
    OtConfig,
    TrackParser,
    TrackToVideoRepository,
    TrackVideoParser,
    VideoMetadata,
    VideoParser,
)
from OTAnalytics.application.project import Project
from OTAnalytics.domain.event import EventRepository
from OTAnalytics.domain.flow import Flow, FlowRepository
from OTAnalytics.domain.geometry import Coordinate, RelativeOffsetCoordinate
from OTAnalytics.domain.progress import ProgressbarBuilder
from OTAnalytics.domain.section import (
    LineSection,
    Section,
    SectionId,
    SectionRepository,
)
from OTAnalytics.domain.track import TrackFileRepository, TrackImage, TrackRepository
from OTAnalytics.domain.types import EventType
from OTAnalytics.domain.video import SimpleVideo, Video, VideoReader, VideoRepository

FIRST_START_DATE = datetime(
    year=2019,
    month=12,
    day=31,
    hour=23,
    minute=0,
    tzinfo=timezone.utc,
)
SECOND_START_DATE = FIRST_START_DATE + timedelta(seconds=3)


class MockVideoReader(VideoReader):
    def get_frame(self, video: Path, index: int) -> TrackImage:
        del video
        del index

        class MockImage(TrackImage):
            def as_image(self) -> Any:
                return Image.fromarray(array([[1, 0], [0, 1]], int32))

            def width(self) -> int:
                return 2

            def height(self) -> int:
                return 2

        return MockImage()

    def get_frame_number_for(self, video_path: Path, date: timedelta) -> int:
        return 0


class TestVideoMetadata:
    def test_fully_specified_metadata(self) -> None:
        metadata = VideoMetadata(
            path="video_path_1.mp4",
            recorded_start_date=FIRST_START_DATE,
            expected_duration=timedelta(seconds=3),
            recorded_fps=20.0,
            actual_fps=20.0,
            number_of_frames=60,
        )
        assert metadata.start == FIRST_START_DATE
        assert metadata.end == FIRST_START_DATE + timedelta(seconds=3)

    def test_partially_specified_metadata(self) -> None:
        metadata = VideoMetadata(
            path="video_path_1.mp4",
            recorded_start_date=FIRST_START_DATE,
            expected_duration=None,
            recorded_fps=20.0,
            actual_fps=None,
            number_of_frames=60,
        )
        assert metadata.start == FIRST_START_DATE
        expected_video_end = FIRST_START_DATE + timedelta(seconds=3)
        assert metadata.end == expected_video_end


class TestSimpleVideo:
    video_reader = MockVideoReader()

    def test_raise_error_if_file_not_exists(self) -> None:
        with pytest.raises(ValueError):
            SimpleVideo(
                video_reader=self.video_reader,
                path=Path("foo/bar.mp4"),
                start_date=FIRST_START_DATE,
            )

    def test_init_with_valid_args(self, cyclist_video: Path) -> None:
        video = SimpleVideo(
            video_reader=self.video_reader,
            path=cyclist_video,
            start_date=FIRST_START_DATE,
        )
        assert video.path == cyclist_video
        assert video.video_reader == self.video_reader

    def test_get_frame_return_correct_image(self, cyclist_video: Path) -> None:
        video = SimpleVideo(
            video_reader=self.video_reader,
            path=cyclist_video,
            start_date=FIRST_START_DATE,
        )
        assert video.get_frame(0).as_image() == Image.fromarray(
            array([[1, 0], [0, 1]], int32)
        )


@pytest.fixture
def track_repository() -> Mock:
    return Mock(spec=TrackRepository)


@pytest.fixture
def track_file_repository() -> Mock:
    return Mock(spec=TrackFileRepository)


@pytest.fixture
def track_parser() -> Mock:
    return Mock(spec=TrackParser)


@pytest.fixture
def section_repository() -> Mock:
    return Mock(spec=SectionRepository)


@pytest.fixture
def flow_parser() -> Mock:
    return Mock(spec=FlowParser)


@pytest.fixture
def flow_repository() -> Mock:
    return Mock(spec=FlowRepository)


@pytest.fixture
def video_parser() -> Mock:
    return Mock(spec=VideoParser)


@pytest.fixture
def track_video_parser() -> Mock:
    return Mock(spec=TrackVideoParser)


@pytest.fixture
def event_repository() -> Mock:
    return Mock(spec=EventRepository)


@pytest.fixture
def event_list_parser() -> Mock:
    return Mock(spec=EventListParser)


@pytest.fixture
def video_repository() -> Mock:
    return Mock(spec=VideoRepository)


@pytest.fixture
def track_to_video_repository() -> Mock:
    return Mock(spec=TrackToVideoRepository)


@pytest.fixture
def config_parser() -> Mock:
    return Mock(spec=ConfigParser)


@pytest.fixture
def progressbar() -> Mock:
    return Mock(spec=ProgressbarBuilder)


class TestDatastore:
    def test_load_config_file(
        self,
        track_repository: Mock,
        track_file_repository: Mock,
        track_parser: Mock,
        section_repository: Mock,
        flow_parser: Mock,
        flow_repository: Mock,
        video_parser: Mock,
        track_video_parser: Mock,
        event_repository: Mock,
        event_list_parser: Mock,
        video_repository: Mock,
        track_to_video_repository: Mock,
        progressbar: Mock,
        config_parser: Mock,
    ) -> None:
        store = Datastore(
            track_repository=track_repository,
            track_file_repository=track_file_repository,
            track_parser=track_parser,
            section_repository=section_repository,
            flow_parser=flow_parser,
            flow_repository=flow_repository,
            event_repository=event_repository,
            event_list_parser=event_list_parser,
            video_repository=video_repository,
            video_parser=video_parser,
            track_video_parser=track_video_parser,
            track_to_video_repository=track_to_video_repository,
            progressbar=progressbar,
            config_parser=config_parser,
        )
        project: Project = Mock(spec=Project)
        videos: Sequence[Video] = []
        sections: Sequence[Section] = []
        flows: Sequence[Flow] = []
        config_parser.parse.return_value = OtConfig(
            project=project,
            videos=videos,
            sections=sections,
            flows=flows,
        )
        some_file = Path("some.file.otconfig")

        store.load_otconfig(some_file)

        assert store.project == project
        track_repository.clear.assert_called_once()
        section_repository.clear.assert_called_once()
        flow_repository.clear.assert_called_once()
        video_repository.clear.assert_called_once()
        event_repository.clear.assert_called_once()
        track_to_video_repository.clear.assert_called_once()
        config_parser.parse.assert_called_with(some_file)
        video_repository.add_all.called_with(videos)
        section_repository.add_all.called_with(sections)
        flow_repository.add_all.called_with(flows)

    def test_save_section_file(
        self,
        track_repository: Mock,
        track_file_repository: Mock,
        track_parser: Mock,
        section_repository: Mock,
        flow_parser: Mock,
        flow_repository: Mock,
        video_parser: Mock,
        track_video_parser: Mock,
        event_repository: Mock,
        event_list_parser: Mock,
        video_repository: Mock,
        track_to_video_repository: Mock,
        progressbar: Mock,
        config_parser: Mock,
    ) -> None:
        track_parser.parse.return_value = []
        track_video_parser.parse.return_value = []
        store = Datastore(
            track_repository=track_repository,
            track_file_repository=track_file_repository,
            track_parser=track_parser,
            section_repository=section_repository,
            flow_parser=flow_parser,
            flow_repository=flow_repository,
            event_repository=event_repository,
            event_list_parser=event_list_parser,
            video_repository=video_repository,
            video_parser=video_parser,
            track_video_parser=track_video_parser,
            track_to_video_repository=track_to_video_repository,
            progressbar=progressbar,
            config_parser=config_parser,
        )
        some_file = Mock()

        store.add_section(
            LineSection(
                id=SectionId("section"),
                name="section",
                relative_offset_coordinates={
                    EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0)
                },
                plugin_data={},
                coordinates=[Coordinate(0, 0), Coordinate(1, 1)],
            )
        )
        store.save_flow_file(some_file)

        flow_parser.serialize.assert_called()

    def test_save_event_list_file(
        self,
        track_repository: Mock,
        track_file_repository: Mock,
        track_parser: Mock,
        section_repository: Mock,
        flow_parser: Mock,
        flow_repository: Mock,
        video_parser: Mock,
        track_video_parser: Mock,
        event_repository: Mock,
        event_list_parser: Mock,
        video_repository: Mock,
        track_to_video_repository: Mock,
        progressbar: Mock,
        config_parser: Mock,
    ) -> None:
        track_parser.parse.return_value = []
        track_video_parser.parse.return_value = []
        store = Datastore(
            track_repository=track_repository,
            track_file_repository=track_file_repository,
            track_parser=track_parser,
            section_repository=section_repository,
            flow_parser=flow_parser,
            flow_repository=flow_repository,
            event_repository=event_repository,
            event_list_parser=event_list_parser,
            video_repository=video_repository,
            video_parser=video_parser,
            track_video_parser=track_video_parser,
            track_to_video_repository=track_to_video_repository,
            progressbar=progressbar,
            config_parser=config_parser,
        )
        some_file = Mock()

        store.save_event_list_file(some_file)

        event_list_parser.serialize.assert_called()

    def test_update_section_plugin_data_not_existing(
        self,
        track_repository: Mock,
        track_file_repository: Mock,
        track_parser: Mock,
        section_repository: Mock,
        flow_parser: Mock,
        flow_repository: Mock,
        video_parser: Mock,
        track_video_parser: Mock,
        event_repository: Mock,
        event_list_parser: Mock,
        video_repository: Mock,
        track_to_video_repository: Mock,
        progressbar: Mock,
        config_parser: Mock,
    ) -> None:
        store = Datastore(
            track_repository=track_repository,
            track_file_repository=track_file_repository,
            track_parser=track_parser,
            section_repository=section_repository,
            flow_parser=flow_parser,
            flow_repository=flow_repository,
            event_repository=event_repository,
            event_list_parser=event_list_parser,
            video_repository=video_repository,
            video_parser=video_parser,
            track_video_parser=track_video_parser,
            track_to_video_repository=track_to_video_repository,
            progressbar=progressbar,
            config_parser=config_parser,
        )
        section_id = SectionId("my section")
        plugin_data = {"some": "new_value"}

        store.set_section_plugin_data(
            section_id=section_id,
            plugin_data=plugin_data,
        )

        section_repository.set_section_plugin_data.called_once_with(
            section_id, plugin_data
        )

    def test_update_section_plugin_data_with_existing_data(
        self,
        track_repository: Mock,
        track_file_repository: Mock,
        track_parser: Mock,
        section_repository: Mock,
        flow_parser: Mock,
        flow_repository: Mock,
        video_parser: Mock,
        track_video_parser: Mock,
        event_repository: Mock,
        event_list_parser: Mock,
        video_repository: Mock,
        track_to_video_repository: Mock,
        progressbar: Mock,
        config_parser: Mock,
    ) -> None:
        store = Datastore(
            track_repository=track_repository,
            track_file_repository=track_file_repository,
            track_parser=track_parser,
            section_repository=section_repository,
            flow_parser=flow_parser,
            flow_repository=flow_repository,
            event_repository=event_repository,
            event_list_parser=event_list_parser,
            video_repository=video_repository,
            video_parser=video_parser,
            track_video_parser=track_video_parser,
            track_to_video_repository=track_to_video_repository,
            progressbar=progressbar,
            config_parser=config_parser,
        )
        section_id = SectionId("my section")
        new_plugin_data = {"other": "new_value"}

        store.set_section_plugin_data(
            section_id=section_id,
            plugin_data=new_plugin_data,
        )

        section_repository.set_section_plugin_data.called_once_with(
            section_id, new_plugin_data
        )


# TODO Add indirection between trackToVideoRepository and new VideoRepository
