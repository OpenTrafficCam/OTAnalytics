from pathlib import Path
from typing import Any
from unittest.mock import Mock, call

import pytest
from numpy import array, int32
from PIL import Image

from OTAnalytics.application.datastore import (
    Datastore,
    EventListParser,
    SectionParser,
    TrackParser,
    TrackToVideoRepository,
    TrackVideoParser,
    Video,
    VideoParser,
    VideoReader,
    VideoRepository,
)
from OTAnalytics.domain.geometry import Coordinate, RelativeOffsetCoordinate
from OTAnalytics.domain.section import LineSection, SectionId, SectionRepository
from OTAnalytics.domain.track import TrackId, TrackImage, TrackRepository
from OTAnalytics.domain.types import EventType


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


class TestVideo:
    video_reader = MockVideoReader()

    def test_raise_error_if_file_not_exists(self) -> None:
        with pytest.raises(ValueError):
            Video(video_reader=self.video_reader, path=Path("foo/bar.mp4"))

    def test_init_with_valid_args(self, cyclist_video: Path) -> None:
        video = Video(video_reader=self.video_reader, path=cyclist_video)
        assert video.path == cyclist_video
        assert video.video_reader == self.video_reader

    def test_get_frame_return_correct_image(self, cyclist_video: Path) -> None:
        video = Video(video_reader=self.video_reader, path=cyclist_video)
        assert video.get_frame(0).as_image() == Image.fromarray(
            array([[1, 0], [0, 1]], int32)
        )


@pytest.fixture
def track_parser() -> Mock:
    return Mock(spec=TrackParser)


@pytest.fixture
def section_repository() -> Mock:
    return Mock(spec=SectionRepository)


@pytest.fixture
def section_parser() -> Mock:
    return Mock(spec=SectionParser)


@pytest.fixture
def video_parser() -> Mock:
    return Mock(spec=VideoParser)


@pytest.fixture
def track_video_parser() -> Mock:
    return Mock(spec=TrackVideoParser)


@pytest.fixture
def event_list_parser() -> Mock:
    return Mock(spec=EventListParser)


@pytest.fixture
def video_repository() -> Mock:
    return Mock(spec=VideoRepository)


@pytest.fixture
def track_to_video_repository() -> Mock:
    return Mock(spec=TrackToVideoRepository)


class TestDatastore:
    def test_load_track_file(
        self,
        track_parser: Mock,
        section_repository: Mock,
        section_parser: Mock,
        video_parser: Mock,
        track_video_parser: Mock,
        event_list_parser: Mock,
        video_repository: Mock,
        track_to_video_repository: Mock,
    ) -> None:
        some_track = Mock()
        some_track_id = TrackId(1)
        some_track.id = some_track_id
        some_video = Video(video_reader=Mock(), path=Path(""))
        track_parser.parse.return_value = [some_track]
        track_video_parser.parse.return_value = [some_track_id], [some_video]
        store = Datastore(
            track_repository=TrackRepository(),
            track_parser=track_parser,
            section_repository=section_repository,
            section_parser=section_parser,
            event_list_parser=event_list_parser,
            video_repository=video_repository,
            video_parser=video_parser,
            track_video_parser=track_video_parser,
            track_to_video_repository=track_to_video_repository,
        )
        some_file = Path("some.file.ottrk")

        store.load_track_file(some_file)

        track_parser.parse.assert_called_with(some_file)
        track_video_parser.parse.assert_called_with(some_file, [some_track_id])
        assert some_track in store._track_repository.get_all()
        track_to_video_repository.add.called_with(some_track_id, some_video)

    def test_load_track_files(
        self,
        track_parser: Mock,
        section_repository: Mock,
        section_parser: Mock,
        video_parser: Mock,
        track_video_parser: Mock,
        event_list_parser: Mock,
        video_repository: Mock,
        track_to_video_repository: Mock,
    ) -> None:
        track_repository = Mock(spec=TrackRepository)
        some_track = Mock()
        some_track_id = TrackId(1)
        some_track.id = some_track_id
        some_video = Video(video_reader=Mock(), path=Path(""))
        other_track = Mock()
        other_track_id = TrackId(2)
        other_track.id = other_track_id
        other_video = Video(video_reader=Mock(), path=Path(""))
        track_parser.parse.side_effect = [[some_track], [other_track]]
        track_video_parser.parse.side_effect = [
            [[some_track_id], [some_video]],
            [[other_track_id], [other_video]],
        ]
        store = Datastore(
            track_repository=track_repository,
            track_parser=track_parser,
            section_repository=section_repository,
            section_parser=section_parser,
            event_list_parser=event_list_parser,
            video_parser=video_parser,
            video_repository=video_repository,
            track_video_parser=track_video_parser,
            track_to_video_repository=track_to_video_repository,
        )
        some_file = Path("some.file.ottrk")
        other_file = Path("other.file.ottrk")

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
        track_parser: Mock,
        section_repository: Mock,
        section_parser: Mock,
        video_parser: Mock,
        track_video_parser: Mock,
        event_list_parser: Mock,
        video_repository: Mock,
        track_to_video_repository: Mock,
    ) -> None:
        track_parser.parse.return_value = []
        track_video_parser.parse.return_value = []
        store = Datastore(
            track_repository=TrackRepository(),
            track_parser=track_parser,
            section_repository=section_repository,
            section_parser=section_parser,
            event_list_parser=event_list_parser,
            video_repository=video_repository,
            video_parser=video_parser,
            track_video_parser=track_video_parser,
            track_to_video_repository=track_to_video_repository,
        )
        some_file = Mock()
        store.add_section(
            LineSection(
                id=SectionId("section"),
                relative_offset_coordinates={
                    EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0)
                },
                plugin_data={},
                coordinates=[Coordinate(0, 0), Coordinate(1, 1)],
            )
        )
        store.save_section_file(some_file)

        section_parser.serialize.assert_called()

    def test_save_event_list_file(
        self,
        track_parser: Mock,
        section_repository: Mock,
        section_parser: Mock,
        video_parser: Mock,
        track_video_parser: Mock,
        event_list_parser: Mock,
        video_repository: Mock,
        track_to_video_repository: Mock,
    ) -> None:
        track_parser.parse.return_value = []
        track_video_parser.parse.return_value = []
        store = Datastore(
            track_repository=TrackRepository(),
            track_parser=track_parser,
            section_repository=section_repository,
            section_parser=section_parser,
            event_list_parser=event_list_parser,
            video_repository=video_repository,
            video_parser=video_parser,
            track_video_parser=track_video_parser,
            track_to_video_repository=track_to_video_repository,
        )
        some_file = Mock()
        store.save_event_list_file(some_file)

        event_list_parser.serialize.assert_called()

    def test_update_section_plugin_data_not_existing(
        self,
        track_parser: Mock,
        section_repository: Mock,
        section_parser: Mock,
        video_parser: Mock,
        track_video_parser: Mock,
        event_list_parser: Mock,
        video_repository: Mock,
        track_to_video_repository: Mock,
    ) -> None:
        store = Datastore(
            track_repository=TrackRepository(),
            track_parser=track_parser,
            section_repository=section_repository,
            section_parser=section_parser,
            event_list_parser=event_list_parser,
            video_repository=video_repository,
            video_parser=video_parser,
            track_video_parser=track_video_parser,
            track_to_video_repository=track_to_video_repository,
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
        track_parser: Mock,
        section_repository: Mock,
        section_parser: Mock,
        video_parser: Mock,
        track_video_parser: Mock,
        event_list_parser: Mock,
        video_repository: Mock,
        track_to_video_repository: Mock,
    ) -> None:
        store = Datastore(
            track_repository=TrackRepository(),
            track_parser=track_parser,
            section_repository=section_repository,
            section_parser=section_parser,
            event_list_parser=event_list_parser,
            video_repository=video_repository,
            video_parser=video_parser,
            track_video_parser=track_video_parser,
            track_to_video_repository=track_to_video_repository,
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
