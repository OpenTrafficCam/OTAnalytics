from datetime import timedelta
from pathlib import Path
from unittest.mock import Mock

import av
import numpy
import pytest
from PIL import Image, ImageChops

from OTAnalytics.domain.video import VideoReader
from OTAnalytics.plugin_prototypes.track_visualization.pil_image import PilImage
from OTAnalytics.plugin_prototypes.track_visualization.track_viz import PilImageFactory
from OTAnalytics.plugin_video_processing.video_reader import (
    PyAvVideoReader,
    av_to_image,
    rotate,
)

DEFAULT_IMAGE_FACTORY = PilImageFactory()


class TestPyAVVideoReader:
    def read_expected_frames(self, video_path: Path) -> list[Image.Image]:
        expected_frames = []
        with av.open(str(video_path.absolute())) as container:
            for frame in container.decode(video=0):
                expected_frames.append(
                    av_to_image(frame, DEFAULT_IMAGE_FACTORY).as_image()
                )
        return expected_frames

    @pytest.fixture
    def video_reader(self) -> VideoReader:
        return PyAvVideoReader(Mock(), DEFAULT_IMAGE_FACTORY)

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

        target = PyAvVideoReader(given_videos_metadata, DEFAULT_IMAGE_FACTORY)
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

        target = PyAvVideoReader(given_videos_metadata, DEFAULT_IMAGE_FACTORY)
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

        target = PyAvVideoReader(given_videos_metadata, DEFAULT_IMAGE_FACTORY)
        actual = target._get_total_frames(given_video_stream, given_video_path)

        assert actual == 60

        given_videos_metadata.get_by_video_name.assert_called_once_with(
            given_video_path.name
        )


def write_rotated_video(path: Path, angle: int, width: int, height: int) -> Path:
    with av.open(str(path), "w") as container:
        stream = container.add_stream("mpeg4", rate=20)
        stream.width = width
        stream.height = height
        stream.pix_fmt = "yuv420p"
        stream.set_display_rotation(angle)
        black = numpy.zeros((height, width, 3), numpy.uint8)
        for _ in range(5):
            frame = av.VideoFrame.from_ndarray(black, format="rgb24")
            for packet in stream.encode(frame):
                container.mux(packet)
        for packet in stream.encode():
            container.mux(packet)
    return path


class TestRotation:
    @pytest.mark.parametrize("angle", (90, -90))
    def test_get_frame_applies_display_rotation(
        self, tmp_path: Path, angle: int
    ) -> None:
        video = write_rotated_video(tmp_path / "rotated.mp4", angle, 64, 32)
        video_reader = PyAvVideoReader(Mock(), DEFAULT_IMAGE_FACTORY)

        image = video_reader.get_frame(video, 1).as_image()

        assert image.size == (32, 64)

    def test_get_frame_keeps_orientation_without_rotation(self, tmp_path: Path) -> None:
        video = write_rotated_video(tmp_path / "upright.mp4", 0, 64, 32)
        video_reader = PyAvVideoReader(Mock(), DEFAULT_IMAGE_FACTORY)

        image = video_reader.get_frame(video, 1).as_image()

        assert image.size == (64, 32)

    def test_rotate_rejects_angle_not_multiple_of_90(self) -> None:
        with pytest.raises(ValueError):
            rotate(numpy.zeros((2, 3)), 45)
