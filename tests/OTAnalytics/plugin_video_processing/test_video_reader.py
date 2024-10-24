from datetime import timedelta
from pathlib import Path

import av
import pytest
from PIL import Image, ImageChops

from OTAnalytics.domain.track import PilImage
from OTAnalytics.domain.video import VideoReader
from OTAnalytics.plugin_video_processing.video_reader import (
    PyAvVideoReader,
    av_to_image,
)


class TestPyAVVideoReader:
    def read_expected_frames(self, video_path: Path) -> list[Image.Image]:
        expected_frames = []
        with av.open(str(video_path.absolute())) as container:
            for frame in container.decode(video=0):
                expected_frames.append(av_to_image(frame).as_image())
        return expected_frames

    @pytest.fixture
    def video_reader(self) -> VideoReader:
        return PyAvVideoReader()

    def test_get_image_possible(
        self, cyclist_video: Path, video_reader: VideoReader
    ) -> None:
        image = video_reader.get_frame(cyclist_video, 1)
        assert isinstance(image, PilImage)

    @pytest.mark.parametrize("frame_num", (-1, 60, 61))
    def test_get_frame_out_of_bounds(
        self, cyclist_video: Path, video_reader: VideoReader, frame_num: int
    ) -> None:
        image = video_reader.get_frame(cyclist_video, frame_num)
        assert isinstance(image, PilImage)

    def test_get_frame_number_for(
        self, cyclist_video: Path, video_reader: VideoReader
    ) -> None:
        delta = timedelta(seconds=1)

        frame_number = video_reader.get_frame_number_for(cyclist_video, delta)

        assert frame_number == 20

    @pytest.mark.parametrize("frame_num", (0, 1, 5, 58, 59))
    def test_get_specific_frame(
        self, cyclist_video: Path, video_reader: VideoReader, frame_num: int
    ) -> None:
        expected_frames = self.read_expected_frames(cyclist_video)
        image = video_reader.get_frame(cyclist_video, frame_num)
        frame = image.as_image()
        streaming_frame = expected_frames[frame_num]
        assert frame.size == streaming_frame.size
        assert ImageChops.difference(frame, streaming_frame).getbbox() is None
