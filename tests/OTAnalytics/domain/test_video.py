from pathlib import Path
from unittest.mock import Mock, call

import pytest

from OTAnalytics.domain.video import (
    PATH,
    SimpleVideo,
    VideoListObserver,
    VideoReader,
    VideoRepository,
)


@pytest.fixture
def video_reader() -> Mock:
    return Mock(spec=VideoReader)


class TestVideo:
    def test_resolve_relative_paths(
        self, video_reader: Mock, test_data_tmp_dir: Path
    ) -> None:
        video_path = test_data_tmp_dir / Path("some/video/path/to/file")
        config_path = test_data_tmp_dir / Path("some/config/path/to/file")
        expected_video_path = str(Path("../../../../video/path/to/file"))
        video_path.parent.mkdir(parents=True)
        config_path.parent.mkdir(parents=True)
        video_path.touch()
        config_path.touch()
        video = SimpleVideo(path=video_path, video_reader=video_reader)

        result = video.to_dict(config_path)

        assert result[PATH] == expected_video_path


class TestVideoRepository:
    def test_remove(self, video_reader: VideoReader, test_data_tmp_dir: Path) -> None:
        observer = Mock(spec=VideoListObserver)
        path = test_data_tmp_dir / "dummy.mp4"
        path.touch()
        video = SimpleVideo(video_reader, path)
        repository = VideoRepository()
        repository.register_videos_observer(observer)

        repository.add(video)

        assert repository.get(video.path) == video

        repository.remove(video)

        assert repository.get(video.path) is None
        assert observer.notify_videos.call_args_list == [call([video]), call([])]
