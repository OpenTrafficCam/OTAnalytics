from datetime import timedelta
from fractions import Fraction
from math import floor
from pathlib import Path

import av
import numpy
from av import VideoFrame
from av.container import InputContainer
from av.video.stream import VideoStream
from numpy import ndarray
from PIL import Image

from OTAnalytics.application.state import VideosMetadata
from OTAnalytics.domain.track import PilImage, TrackImage
from OTAnalytics.domain.video import InvalidVideoError, VideoReader

OFFSET = 1
GRAYSCALE = "L"
DISPLAYMATRIX = "DISPLAYMATRIX"


def av_to_image(frame: VideoFrame, side_data: dict) -> PilImage:
    array = frame.to_ndarray(format="rgb24")
    rotated_image = rotate(array, side_data)
    return PilImage(Image.fromarray(rotated_image).convert(GRAYSCALE))


def rotate(array: ndarray, side_data: dict) -> ndarray:
    """
    Rotate a numpy array using the DISPLAYMATRIX rotation angle defined in side_data.

    Args:
        array: to rotate
        side_data: metadata dictionary to read the angle from

    Returns: rotated array

    """
    if DISPLAYMATRIX in side_data:
        angle = side_data[DISPLAYMATRIX]
        if angle % 90 != 0:
            raise ValueError(
                f"Rotation angle must be multiple of 90 degrees, but is {angle}"
            )
        rotation = angle / 90
        rotated_image = numpy.rot90(array, rotation)
        return rotated_image
    return array


class PyAvVideoReader(VideoReader):

    def __init__(self, videos_metadata: VideosMetadata) -> None:
        self._videos_metadata = videos_metadata

    def get_fps(self, video_path: Path) -> float:
        with self.__get_clip(video_path) as container:
            rate = self.__get_fps(container, video_path)
            return rate.numerator / rate.denominator
        raise ValueError(f"Could not read frames per second from {str(video_path)}")

    def __get_fps(self, container: InputContainer, video_path: Path) -> Fraction:
        average_rate = container.streams.video[0].average_rate
        if average_rate is None:
            raise ValueError(f"Could not read frames per second from {str(video_path)}")
        return average_rate

    def get_frame(self, video_path: Path, frame_number: int) -> TrackImage:
        """Get image of video at position `frame_number`.

        It uses PyAV to seek the closest keyframe. Afterwards, it iterates forward
        through the video to find the correct frame. Given this implementation,
        the complexity is O(n).

        Args:
            video_path (Path): path to the video_path.
            frame_number (int): the frame of the video to get.
        Raises:
            FrameDoesNotExistError: if frame does not exist.
        Returns:
            ndarray: the image as an multi-dimensional array.
        """
        return self._read_frame(frame_number, video_path)

    def _read_frame(
        self,
        frame_to_read: int,
        video_path: Path,
    ) -> PilImage:
        with self.__get_clip(video_path) as container:
            if len(container.streams.video) <= 0:
                raise InvalidVideoError(f"{str(video_path)} is not a video")
            video = container.streams.video[0]
            max_frames = self._get_total_frames(video, video_path)
            frame_to_read = min(frame_to_read, max_frames - OFFSET)
            framerate = self.__get_fps(container, video_path)
            time_base = (
                video.time_base if video.time_base else Fraction(av.time_base, 1)
            )
            self._seek_to_nearest_frame(container, frame_to_read, framerate)
            frame = self._decode_frame(container, frame_to_read, framerate, time_base)
            side_data = container.streams.video[0].side_data
        return av_to_image(frame, side_data)

    def _get_total_frames(self, video_stream: VideoStream, video_path: Path) -> int:
        if frames := video_stream.frames:
            return frames
        if metadata := self._videos_metadata.get_by_video_name(video_path.name):
            return metadata.number_of_frames
        raise ValueError(f"Could not read total frames from {str(video_path)}")

    def _decode_frame(
        self,
        container: InputContainer,
        frame_to_read: int,
        framerate: Fraction,
        time_base: Fraction,
    ) -> VideoFrame:
        """
        Args:
            container (InputContainer): Container from which video frames will be
                decoded.
            frame_to_read (int): The specific frame number to read from the video.
            framerate (Fraction): The framerate of the video.
            time_base (Fraction): The time base used for converting frame presentation
                timestamp to seconds.

        Returns:
            The requested video frame as a VideoFrame object.
        """
        decode = container.decode(video=0)
        frame = next(decode)
        sec_frame = round(framerate * frame.pts * time_base)
        for _ in range(sec_frame, frame_to_read):
            frame = next(decode)
        return frame

    def _seek_to_nearest_frame(
        self, container: InputContainer, frame_to_read: int, framerate: Fraction
    ) -> None:
        """
        Seek to the closest (key)frame of the video, according to InputContainer#seek.
        The offset to seek to is based on the `time_base` of the av module, because we
        seek on the container not on the video stream inside the container. Using the
        `time_base` of the video stream results in a wrong offset.

        Args:
            container (InputContainer): Container from which frames are being read.
            frame_to_read (int): The specific frame number to be read.
            framerate (Fraction): The video's frame rate.
        """
        time_in_video = int(frame_to_read / framerate)
        offset = time_in_video * av.time_base
        container.seek(offset, backward=True)

    @staticmethod
    def __get_clip(video_path: Path) -> InputContainer:
        try:
            return av.open(str(video_path.absolute()))
        except IOError as e:
            raise InvalidVideoError(f"{str(video_path)} is not a valid video") from e

    def get_frame_number_for(self, video_path: Path, delta: timedelta) -> int:
        return floor(self.get_fps(video_path) * delta.total_seconds())
