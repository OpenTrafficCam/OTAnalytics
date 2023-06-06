from pathlib import Path
from unittest.mock import Mock

import pytest

from OTAnalytics.domain.video import PATH, Video, VideoReader


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
        video = Video(path=video_path, video_reader=video_reader)

        result = video.to_dict(config_path)

        assert result[PATH] == expected_video_path
