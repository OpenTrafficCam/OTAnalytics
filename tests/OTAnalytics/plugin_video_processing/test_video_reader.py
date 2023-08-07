from pathlib import Path

from OTAnalytics.domain.track import PilImage
from OTAnalytics.plugin_video_processing.video_reader import MoviepyVideoReader


class TestMoviepyVideoReader:
    video_reader = MoviepyVideoReader()

    def test_get_image_possible(self, cyclist_video: Path) -> None:
        image = self.video_reader.get_frame(cyclist_video, 1)
        assert isinstance(image, PilImage)

    def test_get_frame_out_of_bounds(self, cyclist_video: Path) -> None:
        image = self.video_reader.get_frame(cyclist_video, 100)
        assert isinstance(image, PilImage)
