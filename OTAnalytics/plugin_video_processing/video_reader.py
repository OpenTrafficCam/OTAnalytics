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

FIRST_FRAME = 0
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
            frame_to_read = max(frame_to_read, FIRST_FRAME)
            framerate = self.__get_fps(container, video_path)
            time_base = (
                video.time_base if video.time_base else Fraction(av.time_base, 1)
            )
            frame = self._do_read_frame(
                container, frame_to_read, framerate, time_base, video_path
            )
            side_data = container.streams.video[0].side_data
        return av_to_image(frame, side_data)

    def _do_read_frame(
        self,
        container: InputContainer,
        frame_to_read: int,
        framerate: Fraction,
        time_base: Fraction,
        video_path: Path,
    ) -> VideoFrame:
        """
        Reads a specific video frame from a container.

        This function attempts to read a specific frame from a video container based on
        the given parameters. It first checks if the desired frame can be sought and,
        if possible, seeks to that frame and decodes it. If direct seeking is not
        possible, it iterates over the frames in the video until it finds the desired
        one.

        Args:
            container (InputContainer): The container object holding video streams.
            frame_to_read (int): The index of the frame to be read.
            framerate (Fraction): The framerate of the video.
            time_base (Fraction): The time base used for frame time calculation.
            video_path (Path): The file path to the video.

        Returns:
            VideoFrame: The decoded video frame corresponding to the specified
            `frame_to_read`.

        Raises:
            ValueError: If the specified frame index does not exist in the video file.
        """
        if self._can_look_ahead(video_path, frame_to_read, framerate, time_base):
            self._seek_to_nearest_frame(container, frame_to_read, framerate)
            return self._decode_frame(container, frame_to_read, framerate, time_base)
        for index, frame in enumerate(container.decode(video=0)):
            if index == frame_to_read:
                return frame
        raise ValueError(f"Frame {frame_to_read} does not exist in {video_path}")

    def _get_total_frames(self, video_stream: VideoStream, video_path: Path) -> int:
        """
        Calculates the total number of frames in a video by utilizing available metadata
        or manually counting if necessary.

        Args:
            video_stream (VideoStream): The source video stream object that may include
                frame count details.
            video_path (Path): The file path of the video to derive metadata or for
                manual frame counting.

        Returns:
            int: The total number of frames present in the video.
        """
        if frames := video_stream.frames:
            return frames
        if metadata := self._videos_metadata.get_by_video_name(video_path.name):
            return metadata.number_of_frames
        return self._count_manually(video_path)

    @staticmethod
    def _count_manually(video_file: Path) -> int:
        """
        Counts the total number of frames in a given video file manually.

        This method manually calculates the number of frames in a video file by
        decoding each frame using the `av` library. It iterates through all the frames
        in the video stream and maintains a counter. The function might be useful in
        cases where frame count metadata is unavailable or unreliable.

        Args:
            video_file (Path): The path to the video file for which the frame count is
                to be determined.

        Returns:
            int: The total number of frames in the video file.
        """
        # Todo we might update videos metadata here or when loading the video via
        #  `AddVideo`
        counter = 0
        with av.open(str(video_file.absolute())) as container:
            container.streams.video[0].thread_type = "AUTO"
            for _ in container.decode(video=0):
                counter += 1
        return counter

    def _can_look_ahead(
        self,
        video_path: Path,
        frame_to_read: int,
        framerate: Fraction,
        time_base: Fraction,
    ) -> bool:
        """
        Determines whether it is possible to look ahead in the video based on the given
        frame and timing information.

        Args:
            video_path (Path): Path to the video file.
            frame_to_read (int): Frame number to be read from the video.
            framerate (Fraction): Frame rate of the video.
            time_base (Fraction): Time base for timestamp calculations.

        Returns:
            bool: True if it's possible to look ahead to the given frame, False
                otherwise.

        """
        look_ahead_container = self.__get_clip(video_path.absolute())
        self._seek_to_nearest_frame(look_ahead_container, frame_to_read, framerate)
        look_ahead_frame = self._decode_frame(
            look_ahead_container, frame_to_read, framerate, time_base
        )
        sec_frame = round(framerate * look_ahead_frame.pts * time_base)
        return sec_frame <= frame_to_read

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

    @staticmethod
    def _seek_to_nearest_frame(
        container: InputContainer, frame_to_read: int, framerate: Fraction
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
            container = av.open(str(video_path.absolute()))
            container.streams.video[0].thread_type = "AUTO"
            return container
        except IOError as e:
            raise InvalidVideoError(f"{str(video_path)} is not a valid video") from e

    def get_frame_number_for(self, video_path: Path, delta: timedelta) -> int:
        return floor(self.get_fps(video_path) * delta.total_seconds())
