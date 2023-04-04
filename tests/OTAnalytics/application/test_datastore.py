from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest
from numpy import array, int32

from OTAnalytics.application.datastore import Datastore, Video, VideoReader
from OTAnalytics.domain.track import TrackId, TrackImage


class MockVideoReader(VideoReader):
    def get_frame(self, video: Path, index: int) -> TrackImage:
        del video
        del index

        class MockImage(TrackImage):
            def as_array(self) -> Any:
                return array([[1, 0], [0, 1]], int32)

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
        assert (
            video.get_frame(0).as_array().all() == array([[1, 0], [0, 1]], int32).all()
        )


class TestDatastore:
    def test_load_track_file(self) -> None:
        video_reader = Mock()
        some_track = Mock()
        some_track_id = TrackId(1)
        some_track.id = some_track_id
        some_video = Video(video_reader=video_reader, path=Path(""))
        track_parser = Mock()
        track_parser.parse.return_value = [some_track]
        section_parser = Mock()
        event_list_parser = Mock()
        video_parser = Mock()
        video_parser.parse.return_value = [some_track_id], [some_video]
        store = Datastore(
            track_parser=track_parser,
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

    def test_save_section_file(self) -> None:
        track_parser = Mock()
        track_parser.parse.return_value = []
        section_parser = Mock()
        event_list_parser = Mock()
        video_parser = Mock()
        video_parser.parse.return_value = []
        store = Datastore(
            track_parser=track_parser,
            section_parser=section_parser,
            event_list_parser=event_list_parser,
            video_parser=video_parser,
        )
        some_file = Mock()
        store.save_section_file(some_file)

        section_parser.serialize.assert_called()

    def test_save_event_list_file(self) -> None:
        track_parser = Mock()
        track_parser.parse.return_value = []
        section_parser = Mock()
        event_list_parser = Mock()
        video_parser = Mock()
        video_parser.parse.return_value = []
        store = Datastore(
            track_parser=track_parser,
            section_parser=section_parser,
            event_list_parser=event_list_parser,
            video_parser=video_parser,
        )
        some_file = Mock()
        store.save_event_list_file(some_file)

        event_list_parser.serialize.assert_called()
