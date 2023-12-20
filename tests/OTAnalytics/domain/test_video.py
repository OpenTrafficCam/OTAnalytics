from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, call, patch

import pytest

from OTAnalytics.domain.video import (
    PATH,
    DifferentDrivesException,
    SimpleVideo,
    Video,
    VideoListObserver,
    VideoReader,
    VideoRepository,
)

START_DATE = datetime(2023, 1, 1)


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
        video = SimpleVideo(video_reader, video_path, START_DATE)

        result = video.to_dict(config_path)

        assert result[PATH] == expected_video_path

    def test_resolve_relative_paths_on_different_drives(
        self, video_reader: Mock
    ) -> None:
        video_path = Mock(spec=Path)
        config_path = Mock(spec=Path)
        video = SimpleVideo(video_reader, video_path, START_DATE)

        with patch(
            "OTAnalytics.domain.video.splitdrive",
            side_effect=[("C:", "rest"), ("D:", "rest")],
        ):
            with pytest.raises(DifferentDrivesException):
                video.to_dict(config_path)


class TestVideoRepository:
    @pytest.fixture
    def video_1(self) -> Video:
        return self.__create_mock_video(1)

    @pytest.fixture
    def video_2(self) -> Video:
        return self.__create_mock_video(2)

    def __create_mock_video(self, suffix: int) -> Video:
        path = Path(f"./video_{suffix}")
        video = Mock(spec=Video)
        video.get_path.return_value = path
        return video

    def test_remove(self, video_reader: VideoReader, test_data_tmp_dir: Path) -> None:
        observer = Mock(spec=VideoListObserver)
        path = test_data_tmp_dir / "dummy.mp4"
        path.touch()
        video = SimpleVideo(video_reader, path, START_DATE)
        repository = VideoRepository()
        repository.register_videos_observer(observer)

        repository.add(video)

        assert repository.get(video.path) == video

        repository.remove([video])

        assert repository.get(video.path) is None
        assert observer.notify_videos.call_args_list == [call([video]), call([])]

    def test_order_of_videos_single_add(self, video_1: Video, video_2: Video) -> None:
        repository = VideoRepository()
        ordered_videos = [video_1, video_2]

        repository.add(video_2)
        repository.add(video_1)

        result = repository.get_all()

        assert result == ordered_videos

    def test_order_of_videos_multiple_add(self, video_1: Video, video_2: Video) -> None:
        repository = VideoRepository()
        unorderd_videos = [video_2, video_1]
        ordered_videos = [video_1, video_2]

        repository.add_all(unorderd_videos)

        result = repository.get_all()

        assert unorderd_videos != ordered_videos
        assert result == ordered_videos
