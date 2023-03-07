from pathlib import Path

import pytest
from numpy import array, int32, ndarray

from OTAnalytics.application.datastore import Video, VideoReader


class MockVideoReader(VideoReader):
    def get_frame(self, video: Path, index: int) -> ndarray:
        del video
        del index
        return array([[1, 0], [0, 1]], int32)


class TestVideo:
    video_reader = MockVideoReader()

    def test_raise_error_if_file_not_exists(self) -> None:
        with pytest.raises(ValueError):
            Video(video_reader=self.video_reader, path="foo/bar.mp4")

    def test_init_with_valid_args(self, cyclist_video: Path) -> None:
        video = Video(video_reader=self.video_reader, path=cyclist_video)
        assert video.path == cyclist_video
        assert video.video_reader == self.video_reader

    def test_get_frame_return_correct_image(self, cyclist_video: Path) -> None:
        video = Video(video_reader=self.video_reader, path=cyclist_video)
        assert video.get_frame(0).all() == array([[1, 0], [0, 1]], int32).all()
