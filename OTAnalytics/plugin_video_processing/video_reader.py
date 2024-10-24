from datetime import timedelta
from fractions import Fraction
from math import floor
from pathlib import Path

import av
from av import VideoFrame
from av.container import InputContainer

from OTAnalytics.domain.track import PilImage, TrackImage
from OTAnalytics.domain.video import InvalidVideoError, VideoReader

OFFSET = 1

GRAYSCALE = "L"


def av_to_image(frame: VideoFrame) -> PilImage:
    return PilImage(frame.to_image().convert(GRAYSCALE))


class PyAvVideoReader(VideoReader):
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
        frame = self._read_frame(frame_number, video_path)
        return av_to_image(frame)

    def _read_frame(self, frame_to_read: int, video_path: Path) -> VideoFrame:
        with self.__get_clip(video_path) as container:
            if len(container.streams.video) <= 0:
                raise InvalidVideoError(f"{str(video_path)} is not a video")
            video = container.streams.video[0]
            max_frames = video.frames
            frame_to_read = min(frame_to_read, max_frames - OFFSET)
            framerate = self.__get_fps(container, video_path)
            time_base = (
                video.time_base if video.time_base else Fraction(av.time_base, 1)
            )
            time_in_video = int(frame_to_read / framerate)
            container.seek(time_in_video * av.time_base, backward=True)
            decode = container.decode(video=0)
            frame = next(decode)
            sec_frame = int(framerate * frame.pts * time_base)
            for _ in range(sec_frame, frame_to_read):
                frame = next(decode)
        return frame

    @staticmethod
    def __get_clip(video_path: Path) -> InputContainer:
        try:
            return av.open(str(video_path.absolute()))
        except IOError as e:
            raise InvalidVideoError(f"{str(video_path)} is not a valid video") from e

    def get_frame_number_for(self, video_path: Path, delta: timedelta) -> int:
        return floor(self.get_fps(video_path) * delta.total_seconds())
