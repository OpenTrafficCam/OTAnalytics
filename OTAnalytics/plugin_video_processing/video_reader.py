from datetime import timedelta
from math import floor
from pathlib import Path

from moviepy.video.io.VideoFileClip import VideoFileClip
from PIL import Image

from OTAnalytics.domain.track import PilImage, TrackImage
from OTAnalytics.domain.video import VideoReader


class InvalidVideoError(Exception):
    pass


class FrameDoesNotExistError(Exception):
    pass


class MoviepyVideoReader(VideoReader):
    def get_frame(self, video_path: Path, index: int) -> TrackImage:
        """Get image of video at `frame`.

        Args:
            video_path (Path): path to the video_path.
            index (int): the frame of the video to get.

        Raises:
            FrameDoesNotExistError: if frame does not exist.

        Returns:
            ndarray: the image as an multi-dimensional array.
        """
        clip = self.__get_clip(video_path)
        found = None
        max_frames = clip.fps * clip.duration
        frame_to_load = min(index, max_frames)
        found = clip.get_frame(frame_to_load / clip.fps)
        clip.close()
        return PilImage(Image.fromarray(found))

    def __get_clip(self, video_path: Path) -> VideoFileClip:
        try:
            return VideoFileClip(str(video_path.absolute()))
        except IOError as e:
            raise InvalidVideoError(f"{str(video_path)} is not a valid video") from e

    def get_frame_number_for(self, video_path: Path, delta: timedelta) -> int:
        clip = self.__get_clip(video_path)
        return floor(clip.fps * delta.total_seconds())
