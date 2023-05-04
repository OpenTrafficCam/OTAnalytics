from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest
from numpy import array, int32
from PIL import Image

from OTAnalytics.application.datastore import (
    Datastore,
    EventListParser,
    SectionParser,
    TrackParser,
    Video,
    VideoParser,
    VideoReader,
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
def event_list_parser() -> Mock:
    return Mock(spec=EventListParser)


class TestDatastore:
    def test_load_track_file(
        self,
        track_parser: Mock,
        section_repository: Mock,
        section_parser: Mock,
        video_parser: Mock,
        event_list_parser: Mock,
    ) -> None:
        some_track = Mock()
        some_track_id = TrackId(1)
        some_track.id = some_track_id
        some_video = Video(video_reader=Mock(), path=Path(""))
        track_parser.parse.return_value = [some_track]
        video_parser.parse.return_value = [some_track_id], [some_video]
        store = Datastore(
            track_repository=TrackRepository(),
            track_parser=track_parser,
            section_repository=section_repository,
            section_parser=section_parser,
            event_list_parser=event_list_parser,
            video_parser=video_parser,
        )
        some_file = Path("some.file.ottrk")

        store.load_track_file(some_file)

        track_parser.parse.assert_called_with(some_file)
        video_parser.parse.assert_called_with(some_file, [some_track_id])
        assert some_track in store._track_repository.get_all()
        assert some_video == store._video_repository.get_video_for(some_track.id)

    def test_load_track_files(
        self,
        track_parser: Mock,
        section_repository: Mock,
        section_parser: Mock,
        video_parser: Mock,
        event_list_parser: Mock,
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
        video_parser.parse.side_effect = [
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
        )
        some_file = Path("some.file.ottrk")
        other_file = Path("other.file.ottrk")

        store.load_track_files([some_file, other_file])

        assert some_video == store._video_repository.get_video_for(some_track_id)
        assert other_video == store._video_repository.get_video_for(other_track_id)

        track_parser.parse.assert_any_call(some_file)
        track_parser.parse.assert_any_call(other_file)
        track_repository.add_all.assert_any_call([some_track])
        track_repository.add_all.assert_any_call([other_track])
        video_parser.parse.assert_any_call(some_file, [some_track_id])
        video_parser.parse.assert_any_call(other_file, [other_track_id])

    def test_save_section_file(
        self,
        track_parser: Mock,
        section_repository: Mock,
        section_parser: Mock,
        video_parser: Mock,
        event_list_parser: Mock,
    ) -> None:
        track_parser.parse.return_value = []
        video_parser.parse.return_value = []
        store = Datastore(
            track_repository=TrackRepository(),
            track_parser=track_parser,
            section_repository=section_repository,
            section_parser=section_parser,
            event_list_parser=event_list_parser,
            video_parser=video_parser,
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
        event_list_parser: Mock,
    ) -> None:
        track_parser.parse.return_value = []
        video_parser.parse.return_value = []
        store = Datastore(
            track_repository=TrackRepository(),
            track_parser=track_parser,
            section_repository=section_repository,
            section_parser=section_parser,
            event_list_parser=event_list_parser,
            video_parser=video_parser,
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
        event_list_parser: Mock,
    ) -> None:
        store = Datastore(
            track_repository=TrackRepository(),
            track_parser=track_parser,
            section_repository=section_repository,
            section_parser=section_parser,
            event_list_parser=event_list_parser,
            video_parser=video_parser,
        )
        section_id = SectionId("my section")
        plugin_data = {"some": "new_value"}

        store.set_section_plugin_data(
            section_id=section_id,
            plugin_data=plugin_data,
        )

        section_repository.set_section_plugin_data.called_once_with(section_id)

    def test_update_section_plugin_data_with_existing_data(
        self,
        track_parser: Mock,
        section_repository: Mock,
        section_parser: Mock,
        video_parser: Mock,
        event_list_parser: Mock,
    ) -> None:
        store = Datastore(
            track_repository=TrackRepository(),
            track_parser=track_parser,
            section_repository=section_repository,
            section_parser=section_parser,
            event_list_parser=event_list_parser,
            video_parser=video_parser,
        )
        section_id = SectionId("my section")
        new_plugin_data = {"other": "new_value"}

        store.set_section_plugin_data(
            section_id=section_id,
            plugin_data=new_plugin_data,
        )

        section_repository.set_section_plugin_data.called_once_with(section_id)
