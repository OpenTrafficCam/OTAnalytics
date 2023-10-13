from pathlib import Path

import cv2
from cv2 import VideoCapture
from PIL import Image

from OTAnalytics.domain.track import PilImage, TrackImage
from OTAnalytics.domain.video import VideoReader

GRAYSCALE = "L"


class InvalidVideoError(Exception):
    pass


class FrameDoesNotExistError(Exception):
    pass


class OpenCvVideoReader(VideoReader):
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
        cap = self.__get_clip(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_to_load = min(index, total_frames)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_to_load)
        is_read, frame = cap.read()
        cap.release()
        return PilImage(Image.fromarray(frame).convert(GRAYSCALE))

    @staticmethod
    def __get_clip(video_path: Path) -> VideoCapture:
        try:
            return VideoCapture(str(video_path.absolute()))
        except IOError as e:
            raise InvalidVideoError(f"{str(video_path)} is not a valid video") from e
