from datetime import timedelta
from math import floor
from pathlib import Path

import av
from av.container import InputContainer
from av.frame import Frame
from domain.video import InvalidVideoError

from OTAnalytics.domain.track import PilImage, TrackImage
from OTAnalytics.domain.video import VideoReader

OFFSET = 2

GRAYSCALE = "L"


def av_to_image(frame: Frame) -> PilImage:
    return PilImage(frame.to_image().convert(GRAYSCALE))


class PyAvVideoReader(VideoReader):
    def get_fps(self, video_path: Path) -> float:
        with self.__get_clip(video_path) as container:
            return container.streams.video[0].average_rate

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

    def _read_frame(self, frame_to_read: int, video_path: Path) -> Frame:
        with self.__get_clip(video_path) as container:
            if len(container.streams.video) <= 0:
                raise InvalidVideoError(f"{str(video_path)} is not a video")
            video = container.streams.video[0]
            max_frames = video.frames
            frame_to_read = min(frame_to_read, max_frames - OFFSET)
            framerate = video.average_rate
            time_base = video.time_base
            time_in_video = int(frame_to_read / framerate)
            container.seek(time_in_video * av.time_base, backward=True)
            frame = next(container.decode(video=0))
            sec_frame = int(frame.pts * time_base * framerate)
            for _ in range(sec_frame, frame_to_read):
                frame = next(container.decode(video=0))
        return frame

    @staticmethod
    def __get_clip(video_path: Path) -> InputContainer:
        try:
            return av.open(str(video_path.absolute()))
        except IOError as e:
            raise InvalidVideoError(f"{str(video_path)} is not a valid video") from e

    def get_frame_number_for(self, video_path: Path, delta: timedelta) -> int:
        return floor(self.get_fps(video_path) * delta.total_seconds())
