from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock, Mock, call, patch

from OTAnalytics.application.datastore import TrackParseResult
from OTAnalytics.application.use_cases.load_track_files import LoadTrackFiles
from OTAnalytics.domain.track import TrackId
from OTAnalytics.domain.video import Video

some_file = Path("some.file.ottrk")
other_file = Path("other.file.ottrk")


class TestLoadTrackFile:
    @patch("OTAnalytics.application.use_cases.load_track_files.LoadTrackFiles.load")
    def test_load_multiple_files(self, mock_load: Mock) -> None:
        given = setup(
            track_ids=[],
            video_files=[],
            track_files=[some_file, other_file],
            existing_track_files=[],
            classes=set(),
        )
        target = create_target(given)

        target([some_file, other_file])
        assert mock_load.call_args_list == [call(some_file), call(other_file)]

    @patch("OTAnalytics.application.use_cases.load_track_files.LoadTrackFiles.load")
    def test_load_existing_track_file(self, mock_load: Mock) -> None:
        """
        # Requirement https://openproject.platomo.de/projects/001-opentrafficcam-live/work_packages/2665

        @bug by randy-seng
        """  # noqa
        given = setup(
            track_ids=[],
            video_files=[],
            track_files=[some_file],
            existing_track_files=[some_file],
            classes=set(),
        )
        target = create_target(given)

        target([some_file])
        mock_load.assert_not_called()

    @patch("OTAnalytics.application.use_cases.load_track_files.LoadTrackFiles.load")
    def test_load_multiple_with_existing_track_file(self, mock_load: Mock) -> None:
        """
        # Requirement https://openproject.platomo.de/projects/001-opentrafficcam-live/work_packages/2665

        @bug by randy-seng
        """  # noqa
        given = setup(
            track_ids=[],
            video_files=[],
            track_files=[some_file, other_file],
            existing_track_files=[some_file],
            classes=set(),
        )
        target = create_target(given)

        target([some_file, other_file])
        mock_load.assert_called_with(other_file)

    def test_load(self) -> None:
        given = setup(
            track_ids=[TrackId("1")],
            video_files=[Path("video1.mp4")],
            track_files=[some_file],
            existing_track_files=[],
            classes={"class1", "class2"},
        )
        target = create_target(given)
        target.load(some_file)
        assert given.order.mock_calls == [
            call.track_parser.parse(some_file),
            call.track_video_parser.parse(
                some_file, given.track_ids, given.parse_result.video_metadata
            ),
            call.videos_metadata.update(given.parse_result.video_metadata),
            call.video_repository.add_all(given.videos),
            call.track_to_video_repository.add_all(given.track_ids, given.videos),
            call.track_repository.add_all(given.parse_result.tracks),
            call.tracks_metadata.update_detection_classes(
                given.parse_result.detection_metadata.detection_classes
            ),
        ]


@dataclass
class Given:
    track_ids: list[TrackId]
    videos: list[Video]
    classes: set[str]
    parse_result: TrackParseResult
    track_repository: Mock = Mock()
    track_file_repository: Mock = Mock()
    track_parser: Mock = Mock()
    track_video_parser: Mock = Mock()
    video_repository: Mock = Mock()
    track_to_video_repository: Mock = Mock()
    progressbar: Mock = Mock()
    tracks_metadata: Mock = Mock()
    videos_metadata: Mock = Mock()
    order: MagicMock = MagicMock()

    def __post_init__(self) -> None:
        self.order.track_parser = self.track_parser
        self.order.videos_metadata = self.videos_metadata
        self.order.track_video_parser = self.track_video_parser
        self.order.video_repository = self.video_repository
        self.order.track_repository = self.track_repository
        self.order.track_to_video_repository = self.track_to_video_repository
        self.order.tracks_metadata = self.tracks_metadata


def setup(
    track_ids: list[TrackId],
    video_files: list[Path],
    track_files: list[Path],
    existing_track_files: list[Path],
    classes: set[str],
) -> Given:
    videos = create_videos(video_files)
    detection_metadata = create_detection_metadata(classes)
    track_dataset_result = Mock()
    type(track_dataset_result).track_ids = frozenset(track_ids)
    parse_result = Mock()
    parse_result.tracks = track_dataset_result
    parse_result.detection_metadata = detection_metadata
    parse_result.video_metadata = Mock()
    given = Given(track_ids, videos, classes, parse_result)
    given.track_file_repository.get_all.return_value = existing_track_files
    given.track_parser.parse.return_value = parse_result
    given.track_video_parser.parse.return_value = track_ids, videos
    given.progressbar.return_value = track_files
    return given


def create_videos(video_files: list[Path]) -> list[Video]:
    return [create_video(video_file) for video_file in video_files]


def create_video(video_file: Path) -> Video:
    video = Mock()
    video.path = video_file
    return video


def create_detection_metadata(classes: set[str]) -> Mock:
    detection_metadata = Mock()
    detection_metadata.detection_classes = classes
    return detection_metadata


def create_target(given: Given) -> LoadTrackFiles:
    return LoadTrackFiles(
        track_parser=given.track_parser,
        track_video_parser=given.track_video_parser,
        track_repository=given.track_repository,
        track_file_repository=given.track_file_repository,
        video_repository=given.video_repository,
        track_to_video_repository=given.track_to_video_repository,
        progressbar=given.progressbar,
        tracks_metadata=given.tracks_metadata,
        videos_metadata=given.videos_metadata,
    )
