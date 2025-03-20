from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest
from numpy import array, int32
from PIL import Image

from OTAnalytics.application.datastore import (
    Datastore,
    EventListParser,
    TrackParser,
    TrackToVideoRepository,
    TrackVideoParser,
    VideoParser,
)
from OTAnalytics.application.parser.config_parser import ConfigParser
from OTAnalytics.application.parser.flow_parser import FlowParser
from OTAnalytics.domain.event import EventRepository
from OTAnalytics.domain.flow import FlowRepository
from OTAnalytics.domain.progress import ProgressbarBuilder
from OTAnalytics.domain.remark import RemarkRepository
from OTAnalytics.domain.section import SectionId, SectionRepository
from OTAnalytics.domain.track import TrackImage
from OTAnalytics.domain.track_repository import TrackFileRepository, TrackRepository
from OTAnalytics.domain.video import SimpleVideo, VideoReader, VideoRepository

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
    def get_fps(self, video: Path) -> float:
        return 20

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


class TestSimpleVideo:
    video_reader = MockVideoReader()

    def test_raise_error_if_file_not_exists(self) -> None:
        with pytest.raises(ValueError):
            SimpleVideo(self.video_reader, Path("foo/bar.mp4"), None)

    def test_init_with_valid_args(self, cyclist_video: Path) -> None:
        video = SimpleVideo(self.video_reader, cyclist_video, None)
        assert video.path == cyclist_video
        assert video.video_reader == self.video_reader

    def test_get_frame_return_correct_image(self, cyclist_video: Path) -> None:
        video = SimpleVideo(self.video_reader, cyclist_video, None)
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


@pytest.fixture
def remark_repository() -> Mock:
    return Mock(spec=RemarkRepository)


class TestDatastore:

    def test_save_event_list_file(
        self,
        track_repository: Mock,
        track_file_repository: Mock,
        track_parser: Mock,
        section_repository: Mock,
        flow_repository: Mock,
        video_parser: Mock,
        track_video_parser: Mock,
        event_repository: Mock,
        event_list_parser: Mock,
        video_repository: Mock,
        track_to_video_repository: Mock,
        progressbar: Mock,
        remark_repository: Mock,
    ) -> None:
        track_parser.parse.return_value = []
        track_video_parser.parse.return_value = []
        store = Datastore(
            track_repository=track_repository,
            track_file_repository=track_file_repository,
            track_parser=track_parser,
            section_repository=section_repository,
            flow_repository=flow_repository,
            event_repository=event_repository,
            event_list_parser=event_list_parser,
            video_repository=video_repository,
            video_parser=video_parser,
            track_video_parser=track_video_parser,
            track_to_video_repository=track_to_video_repository,
            progressbar=progressbar,
            remark_repository=remark_repository,
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
        flow_repository: Mock,
        video_parser: Mock,
        track_video_parser: Mock,
        event_repository: Mock,
        event_list_parser: Mock,
        video_repository: Mock,
        track_to_video_repository: Mock,
        progressbar: Mock,
        remark_repository: Mock,
    ) -> None:
        store = Datastore(
            track_repository=track_repository,
            track_file_repository=track_file_repository,
            track_parser=track_parser,
            section_repository=section_repository,
            flow_repository=flow_repository,
            event_repository=event_repository,
            event_list_parser=event_list_parser,
            video_repository=video_repository,
            video_parser=video_parser,
            track_video_parser=track_video_parser,
            track_to_video_repository=track_to_video_repository,
            progressbar=progressbar,
            remark_repository=remark_repository,
        )
        section_id = SectionId("my section")
        plugin_data = {"some": "new_value"}

        store.set_section_plugin_data(
            section_id=section_id,
            plugin_data=plugin_data,
        )

        section_repository.set_section_plugin_data.assert_called_once_with(
            section_id=section_id, plugin_data=plugin_data
        )

    def test_update_section_plugin_data_with_existing_data(
        self,
        track_repository: Mock,
        track_file_repository: Mock,
        track_parser: Mock,
        section_repository: Mock,
        flow_repository: Mock,
        video_parser: Mock,
        track_video_parser: Mock,
        event_repository: Mock,
        event_list_parser: Mock,
        video_repository: Mock,
        track_to_video_repository: Mock,
        progressbar: Mock,
        remark_repository: Mock,
    ) -> None:
        store = Datastore(
            track_repository=track_repository,
            track_file_repository=track_file_repository,
            track_parser=track_parser,
            section_repository=section_repository,
            flow_repository=flow_repository,
            event_repository=event_repository,
            event_list_parser=event_list_parser,
            video_repository=video_repository,
            video_parser=video_parser,
            track_video_parser=track_video_parser,
            track_to_video_repository=track_to_video_repository,
            progressbar=progressbar,
            remark_repository=remark_repository,
        )
        section_id = SectionId("my section")
        new_plugin_data = {"other": "new_value"}

        store.set_section_plugin_data(
            section_id=section_id,
            plugin_data=new_plugin_data,
        )

        section_repository.set_section_plugin_data.assert_called_once_with(
            section_id=section_id, plugin_data=new_plugin_data
        )


# TODO Add indirection between trackToVideoRepository and new VideoRepository
