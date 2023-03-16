from pathlib import Path

import pytest
from numpy import ndarray

from OTAnalytics.plugin_video_processing.video_reader import (
    FrameDoesNotExistError,
    MoviepyVideoReader,
)


class TestMoviepyVideoReader:
    video_reader = MoviepyVideoReader()

    def test_get_image_possible(self, cyclist_video: Path) -> None:
        image = self.video_reader.get_frame(cyclist_video, 1)
        assert isinstance(image, ndarray)

    def test_get_frame_out_of_bounds(self, cyclist_video: Path) -> None:
        with pytest.raises(FrameDoesNotExistError):
            self.video_reader.get_frame(cyclist_video, 100)
