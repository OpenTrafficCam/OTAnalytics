from pathlib import Path
from typing import Any, Sequence
from unittest.mock import MagicMock, Mock, call

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
from OTAnalytics.domain.track import TrackId, TrackImage, TrackRepository
from OTAnalytics.domain.types import EventType
from OTAnalytics.domain.video import SimpleVideo, Video, VideoReader, VideoRepository


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


class TestSimpleVideo:
    video_reader = MockVideoReader()

    def test_raise_error_if_file_not_exists(self) -> None:
        with pytest.raises(ValueError):
            SimpleVideo(video_reader=self.video_reader, path=Path("foo/bar.mp4"))

    def test_init_with_valid_args(self, cyclist_video: Path) -> None:
        video = SimpleVideo(video_reader=self.video_reader, path=cyclist_video)
        assert video.path == cyclist_video
        assert video.video_reader == self.video_reader

    def test_get_frame_return_correct_image(self, cyclist_video: Path) -> None:
        video = SimpleVideo(video_reader=self.video_reader, path=cyclist_video)
        assert video.get_frame(0).as_image() == Image.fromarray(
            array([[1, 0], [0, 1]], int32)
        )


@pytest.fixture
def track_repository() -> Mock:
    return Mock(spec=TrackRepository)


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

    def test_load_track_file(
        self,
        track_repository: Mock,
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
        some_track = Mock()
        some_track_id = TrackId("1")
        some_track.id = some_track_id
        some_video = SimpleVideo(video_reader=Mock(), path=Path(""))
        track_parser.parse.return_value = [some_track]
        track_video_parser.parse.return_value = [some_track_id], [some_video]

        order = MagicMock()
        order.track_parser = track_parser
        order.track_video_parser = track_video_parser
        order.video_repository = video_repository
        order.track_repository = track_repository
        order.track_to_video_repository = track_to_video_repository

        store = Datastore(
            track_repository=track_repository,
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
        some_file = Path("some.file.ottrk")

        store.load_track_file(some_file)

        assert order.mock_calls == [
            call.track_parser.parse(some_file),
            call.track_video_parser.parse(some_file, [some_track_id]),
            call.video_repository.add_all([some_video]),
            call.track_to_video_repository.add_all([some_track_id], [some_video]),
            call.track_repository.add_all([some_track]),
        ]

    def test_load_track_files(
        self,
        track_repository: Mock,
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
        some_track = Mock()
        some_track_id = TrackId("1")
        some_track.id = some_track_id
        some_video = SimpleVideo(video_reader=Mock(), path=Path(""))
        other_track = Mock()
        other_track_id = TrackId("2")
        other_track.id = other_track_id
        other_video = SimpleVideo(video_reader=Mock(), path=Path(""))
        track_parser.parse.side_effect = [[some_track], [other_track]]
        track_video_parser.parse.side_effect = [
            [[some_track_id], [some_video]],
            [[other_track_id], [other_video]],
        ]
        store = Datastore(
            track_repository=track_repository,
            track_parser=track_parser,
            section_repository=section_repository,
            flow_parser=flow_parser,
            flow_repository=flow_repository,
            event_repository=event_repository,
            event_list_parser=event_list_parser,
            video_parser=video_parser,
            video_repository=video_repository,
            track_video_parser=track_video_parser,
            track_to_video_repository=track_to_video_repository,
            progressbar=progressbar,
            config_parser=config_parser,
        )
        some_file = Path("some.file.ottrk")
        other_file = Path("other.file.ottrk")
        progressbar.return_value = [some_file, other_file]

        store.load_track_files([some_file, other_file])

        track_parser.parse.assert_any_call(some_file)
        track_parser.parse.assert_any_call(other_file)
        track_repository.add_all.assert_any_call([some_track])
        track_repository.add_all.assert_any_call([other_track])
        track_video_parser.parse.assert_any_call(some_file, [some_track_id])
        track_video_parser.parse.assert_any_call(other_file, [other_track_id])
        assert track_to_video_repository.add_all.call_args_list == [
            call([some_track_id], [some_video]),
            call([other_track_id], [other_video]),
        ]

    def test_save_section_file(
        self,
        track_repository: Mock,
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
