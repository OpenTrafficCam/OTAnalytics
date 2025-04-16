from datetime import timedelta
from pathlib import Path
from unittest.mock import Mock

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
                expected_frames.append(av_to_image(frame, {}).as_image())
        return expected_frames

    @pytest.fixture
    def video_reader(self) -> VideoReader:
        return PyAvVideoReader(Mock())

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

    def test_get_total_frames_video_stream_has_no_frame_info(self) -> None:
        given_video_path = Path("some/path/to/video.mp4")
        given_video_stream = Mock()
        given_video_stream.frames = 0

        expected = 120
        given_metadata = Mock()
        given_metadata.number_of_frames = expected
        given_videos_metadata = Mock()
        given_videos_metadata.get_by_video_name.return_value = given_metadata

        target = PyAvVideoReader(given_videos_metadata)
        actual = target._get_total_frames(given_video_stream, given_video_path)

        assert actual == expected
        given_videos_metadata.get_by_video_name.assert_called_once_with(
            given_video_path.name
        )

    def test_get_total_frames_video_stream_has_frame_info(self) -> None:
        expected = 120
        given_video_path = Path("some/path/to/video.mp4")
        given_video_stream = Mock()
        given_video_stream.frames = expected
        given_videos_metadata = Mock()

        target = PyAvVideoReader(given_videos_metadata)
        actual = target._get_total_frames(given_video_stream, given_video_path)
        assert actual == expected

    def test_get_total_frames_video_no_frame_info_available(
        self, cyclist_video: Path
    ) -> None:
        given_video_path = cyclist_video
        given_video_stream = Mock()
        given_video_stream.frames = 0
        given_videos_metadata = Mock()
        given_videos_metadata.get_by_video_name.return_value = None

        target = PyAvVideoReader(given_videos_metadata)
        actual = target._get_total_frames(given_video_stream, given_video_path)

        assert actual == 60

        given_videos_metadata.get_by_video_name.assert_called_once_with(
            given_video_path.name
        )
