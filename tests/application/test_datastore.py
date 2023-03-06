from pathlib import Path

import numpy as np
import pytest

from OTAnalytics.application.datastore import Video, VideoReader


class MockVideoReader(VideoReader):
    def get_frame(self, video: Path, index: int) -> np.ndarray:
        del video
        del index
        return np.array([[1, 0], [0, 1]], np.int32)


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
        assert video.get_frame(0).all() == np.array([[1, 0], [0, 1]], np.int32).all()
