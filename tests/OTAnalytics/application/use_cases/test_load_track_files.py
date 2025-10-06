from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock, Mock, call

from OTAnalytics.application.datastore import TracksParseResult
from OTAnalytics.application.use_cases.load_track_files import LoadTrackFiles
from OTAnalytics.domain.track import TrackId
from OTAnalytics.domain.video import Video

some_file = Path("some.file.ottrk")
other_file = Path("other.file.ottrk")


class TestLoadTrackFile:
    def test_load_multiple_files(self) -> None:
        classes = {"class1", "class2"}
        given = setup(
            track_ids=[TrackId("1"), TrackId("2")],
            video_files=[Path("video1.mp4"), Path("video2.mp4")],
            track_files=[some_file, other_file],
            existing_track_files=[],
            classes=classes,
        )
        target = create_target(given)

        target([some_file, other_file])

        given.track_parser.parse_files.assert_called_once_with([some_file, other_file])
        given.video_repository.add_all.assert_called_once_with(given.videos)
        given.track_repository.add_all.assert_called_once_with(
            given.parse_result.tracks
        )
        given.track_file_repository.add_all.assert_called_once_with(
            [some_file, other_file]
        )
        assert given.tracks_metadata.update_detection_classes.call_args_list == [
            call(classes),
            call(classes),
        ]

    def test_load_existing_track_file(self) -> None:
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

        # Should not parse files if they are already loaded
        given.track_parser.parse_files.assert_not_called()
        given.video_repository.add_all.assert_not_called()
        given.track_repository.add_all.assert_not_called()
        given.track_file_repository.add_all.assert_not_called()
        given.tracks_metadata.update_detection_classes.assert_not_called()

    def test_load_multiple_with_existing_track_file(self) -> None:
        """
        # Requirement https://openproject.platomo.de/projects/001-opentrafficcam-live/work_packages/2665

        @bug by randy-seng
        """  # noqa
        classes = {"class1"}
        given = setup(
            track_ids=[TrackId("1")],
            video_files=[Path("video1.mp4")],
            track_files=[other_file],
            existing_track_files=[some_file],
            classes=classes,
        )
        target = create_target(given)

        target([some_file, other_file])

        # Should only parse the file that's not already loaded
        given.track_parser.parse_files.assert_called_once_with([other_file])
        given.video_repository.add_all.assert_called_once_with(given.videos)
        given.track_repository.add_all.assert_called_once_with(
            given.parse_result.tracks
        )
        given.track_file_repository.add_all.assert_called_once_with([other_file])
        given.tracks_metadata.update_detection_classes.assert_called_once_with(classes)

    def test_load_empty_files_list(self) -> None:
        given = setup(
            track_ids=[],
            video_files=[],
            track_files=[],
            existing_track_files=[],
            classes=set(),
        )
        target = create_target(given)

        target([])

        # Should not call any methods when files list is empty
        given.track_parser.parse_files.assert_not_called()
        given.video_repository.add_all.assert_not_called()
        given.track_repository.add_all.assert_not_called()
        given.track_file_repository.add_all.assert_not_called()
        given.tracks_metadata.update_detection_classes.assert_not_called()

    def test_load_with_videos_metadata_update(self) -> None:
        given = setup(
            track_ids=[TrackId("1")],
            video_files=[Path("video1.mp4")],
            track_files=[some_file],
            existing_track_files=[],
            classes={"class1"},
        )
        target = create_target(given)

        target([some_file])

        # Should update videos metadata for each video
        for video_metadata in given.parse_result.videos_metadata:
            given.videos_metadata.update.assert_any_call(video_metadata)

    def test_load_with_detection_classes_update(self) -> None:
        given = setup(
            track_ids=[TrackId("1")],
            video_files=[Path("video1.mp4")],
            track_files=[some_file],
            existing_track_files=[],
            classes={"class1", "class2"},
        )
        target = create_target(given)

        target([some_file])

        # Should update detection classes for each detection metadata
        for detection_metadata in given.parse_result.detections_metadata:
            given.tracks_metadata.update_detection_classes.assert_any_call(
                detection_metadata.detection_classes
            )


@dataclass
class Given:
    track_ids: list[TrackId]
    videos: list[Video]
    classes: set[str]
    parse_result: TracksParseResult
    track_repository: Mock
    track_file_repository: Mock
    track_parser: Mock
    video_repository: Mock
    video_parser: Mock
    progressbar: Mock
    tracks_metadata: Mock
    videos_metadata: Mock
    order: MagicMock

    def __post_init__(self) -> None:
        self.order.track_parser = self.track_parser
        self.order.videos_metadata = self.videos_metadata
        self.order.video_repository = self.video_repository
        self.order.track_repository = self.track_repository
        self.order.video_parser = self.video_parser
        self.order.tracks_metadata = self.tracks_metadata


def setup(
    track_ids: list[TrackId],
    video_files: list[Path],
    track_files: list[Path],
    existing_track_files: list[Path],
    classes: set[str],
) -> Given:
    videos = create_videos(video_files)
    videos_metadata = [create_video_metadata(video_file) for video_file in video_files]
    detections_metadata = [create_detection_metadata(classes) for _ in track_files]

    track_dataset_result = Mock()
    type(track_dataset_result).track_ids = frozenset(track_ids)

    parse_result = Mock()
    parse_result.tracks = track_dataset_result
    parse_result.videos_metadata = videos_metadata
    parse_result.detections_metadata = detections_metadata

    given = Given(
        track_ids=track_ids,
        videos=videos,
        classes=classes,
        parse_result=parse_result,
        track_repository=Mock(),
        track_file_repository=Mock(),
        track_parser=Mock(),
        video_repository=Mock(),
        video_parser=Mock(),
        progressbar=Mock(),
        tracks_metadata=Mock(),
        videos_metadata=Mock(),
        order=MagicMock(),
    )
    given.track_file_repository.get_all.return_value = existing_track_files
    given.track_parser.parse_files.return_value = parse_result
    given.video_parser.parse.side_effect = videos
    given.progressbar.return_value = track_files
    return given


def create_videos(video_files: list[Path]) -> list[Video]:
    return [create_video(video_file) for video_file in video_files]


def create_video(video_file: Path) -> Video:
    video = Mock()
    video.path = video_file
    return video


def create_video_metadata(video_file: Path) -> Mock:
    video_metadata = Mock()
    video_metadata.path = video_file
    return video_metadata


def create_detection_metadata(classes: set[str]) -> Mock:
    detection_metadata = Mock()
    detection_metadata.detection_classes = classes
    return detection_metadata


def create_target(given: Given) -> LoadTrackFiles:
    return LoadTrackFiles(
        track_parser=given.track_parser,
        track_repository=given.track_repository,
        track_file_repository=given.track_file_repository,
        video_repository=given.video_repository,
        video_parser=given.video_parser,
        progressbar=given.progressbar,
        tracks_metadata=given.tracks_metadata,
        videos_metadata=given.videos_metadata,
    )
