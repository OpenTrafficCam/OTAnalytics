from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, call

import pytest

from OTAnalytics.domain.video import (
    PATH,
    SimpleVideo,
    Video,
    VideoListObserver,
    VideoMetadata,
    VideoReader,
    VideoRepository,
)
from tests.OTAnalytics.application.test_datastore import FIRST_START_DATE

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
        video = SimpleVideo(video_reader, video_path, None)

        result = video.to_dict(config_path)

        assert result[PATH] == expected_video_path


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
        video = SimpleVideo(video_reader, path, None)
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

    def test_get_by_date(self, video_1: Mock, video_2: Mock) -> None:
        video_1.contains.return_value = False
        video_2.contains.return_value = True

        repository = VideoRepository()
        repository.add_all([video_1, video_2])
        result = repository.get_by_date(START_DATE)
        assert result == [video_2]


class TestVideoMetadata:
    @pytest.fixture
    def metadata(self) -> VideoMetadata:
        recorded_fps = 20.0
        actual_fps = 20.0
        return VideoMetadata(
            path="video_path_1.mp4",
            recorded_start_date=FIRST_START_DATE,
            expected_duration=timedelta(seconds=3),
            recorded_fps=recorded_fps,
            actual_fps=actual_fps,
            number_of_frames=60,
        )

    def test_fully_specified_metadata(self, metadata: VideoMetadata) -> None:
        assert metadata.start == FIRST_START_DATE
        assert metadata.end == FIRST_START_DATE + timedelta(seconds=3)
        assert metadata.fps == 20.0

    def test_partially_specified_metadata(self) -> None:
        recorded_fps = 20.0
        metadata = VideoMetadata(
            path="video_path_1.mp4",
            recorded_start_date=FIRST_START_DATE,
            expected_duration=None,
            recorded_fps=recorded_fps,
            actual_fps=None,
            number_of_frames=60,
        )
        assert metadata.start == FIRST_START_DATE
        expected_video_end = FIRST_START_DATE + timedelta(seconds=3)
        assert metadata.end == expected_video_end
        assert metadata.fps == recorded_fps

    def test_contains(self, metadata: VideoMetadata) -> None:
        assert not metadata.contains(FIRST_START_DATE - timedelta(seconds=1))
        assert metadata.contains(FIRST_START_DATE)
        assert metadata.contains(FIRST_START_DATE + timedelta(seconds=2))
        assert not metadata.contains(FIRST_START_DATE + timedelta(seconds=3))
