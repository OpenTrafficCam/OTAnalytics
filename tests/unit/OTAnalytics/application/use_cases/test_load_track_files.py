import asyncio
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, Mock, call

import pytest

from OTAnalytics.application.parser.track_parser import (
    DetectionMetadata,
    TrackParser,
    TracksParseResult,
)
from OTAnalytics.application.use_cases.load_track_files import (
    PARSING_DESCRIPTION,
    PARSING_UNIT,
    LoadTrackFiles,
)
from OTAnalytics.domain.georeference import GeoreferenceMetadata
from OTAnalytics.domain.track import TrackId
from OTAnalytics.domain.track_dataset.track_dataset import (
    IncompatibleGeoreferenceMetadataError,
)
from OTAnalytics.domain.track_repository import TrackRepository
from OTAnalytics.domain.video import Video
from OTAnalytics.plugin_datastore.polars_track_store import (
    POLARS_TRACK_GEOMETRY_FACTORY,
    PolarsTrackDataset,
)
from OTAnalytics.plugin_datastore.track_geometry_store.polars_geometry_store import (
    PolarsTrackGeometryDataset,
)
from tests.utils.builders.track_builder import create_track

some_file = Path("some.file.ottrk")
other_file = Path("other.file.ottrk")

FOLDER_A = Path("folder_a")
FOLDER_B = Path("folder_b")

GEOREF_METADATA = GeoreferenceMetadata(
    geo_min_x=449199.096512522,
    geo_min_y=5699274.275524861,
    geo_max_x=449294.8688478645,
    geo_max_y=5699370.047860203,
    birds_eye_view_width=983,
    birds_eye_view_height=983,
    padding=20,
    crs="EPSG:25833",
)

ALTERNATE_GEOREF_METADATA = GeoreferenceMetadata(
    geo_min_x=1.0,
    geo_min_y=1.0,
    geo_max_x=101.0,
    geo_max_y=101.0,
    birds_eye_view_width=983,
    birds_eye_view_height=983,
    padding=20,
    crs="EPSG:25833",
)


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
        # Requirement https://openproject.platomo.de/wp/2665

        @bug by randy-seng
        """
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
        # Requirement https://openproject.platomo.de/wp/2665

        @bug by randy-seng
        """
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

    def test_load_passes_dataset_with_georeference_metadata_to_repository(
        self,
    ) -> None:
        given = setup(
            track_ids=[TrackId("1")],
            video_files=[Path("video1.mp4")],
            track_files=[some_file],
            existing_track_files=[],
            classes={"class1", "class2"},
            georeference_metadata=GEOREF_METADATA,
        )
        target = create_target(given)

        target([some_file])

        add_all_call = given.track_repository.add_all.call_args
        dataset_arg = add_all_call.args[0]
        assert dataset_arg.georeference_metadata == GEOREF_METADATA

    def test_two_loads_with_mismatched_metadata_raise(self) -> None:
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY = (
            PolarsTrackGeometryDataset.from_track_dataset
        )
        repository = TrackRepository(
            PolarsTrackDataset(track_geometry_factory=track_geometry_factory)
        )

        first_track = create_track("1", [(1, 1), (2, 2)], 1)
        first_tracks = PolarsTrackDataset.from_list(
            [first_track], track_geometry_factory
        ).with_georeference_metadata(GEOREF_METADATA)
        target_first = create_target_for_repo(
            repository=repository,
            parse_result=TracksParseResult(
                tracks=first_tracks,
                detections_metadata=[DetectionMetadata(frozenset(["car"]))],
                videos_metadata=[create_video_metadata(Path("video1.mp4"))],
            ),
        )
        target_first([some_file])

        second_track = create_track("2", [(3, 3), (4, 4)], 3)
        second_tracks = PolarsTrackDataset.from_list(
            [second_track], track_geometry_factory
        ).with_georeference_metadata(ALTERNATE_GEOREF_METADATA)
        target_second = create_target_for_repo(
            repository=repository,
            parse_result=TracksParseResult(
                tracks=second_tracks,
                detections_metadata=[DetectionMetadata(frozenset(["car"]))],
                videos_metadata=[create_video_metadata(Path("video2.mp4"))],
            ),
        )

        with pytest.raises(IncompatibleGeoreferenceMetadataError):
            target_second([other_file])

    @pytest.mark.parametrize(
        "track_files, expected_video_paths",
        [
            pytest.param(
                [FOLDER_A / "a.ottrk", FOLDER_B / "b.ottrk"],
                [FOLDER_A / "a.mp4", FOLDER_B / "b.mp4"],
                id="different_folders",
            ),
            pytest.param(
                [FOLDER_A / "a.ottrk", FOLDER_A / "b.ottrk"],
                [FOLDER_A / "a.mp4", FOLDER_A / "b.mp4"],
                id="same_folder",
            ),
        ],
    )
    def test_load_resolves_each_video_relative_to_its_own_track_file(
        self, track_files: list[Path], expected_video_paths: list[Path]
    ) -> None:
        """Each video is resolved under the parent of the track file it came from.

        # Requirement https://openproject.platomo.de/wp/10279
        """
        given = setup(
            track_ids=[TrackId("1"), TrackId("2")],
            video_files=[Path("a.mp4"), Path("b.mp4")],
            track_files=track_files,
            existing_track_files=[],
            classes={"class1"},
        )
        target = create_target(given)

        target(track_files)

        assert given.parsed_video_calls() == list(
            zip(expected_video_paths, given.parse_result.videos_metadata, strict=True)
        )

    def test_load_resolves_videos_against_the_files_actually_parsed(self) -> None:
        """Skipping an already loaded file must not shift video resolution.

        Videos are paired with the files handed to the parser, not with every
        file the caller passed in.

        # Requirement https://openproject.platomo.de/wp/10279
        """
        already_loaded = FOLDER_A / "a.ottrk"
        track_file_b = FOLDER_B / "b.ottrk"
        given = setup(
            track_ids=[TrackId("1")],
            video_files=[Path("b.mp4")],
            track_files=[track_file_b],
            existing_track_files=[already_loaded],
            classes={"class1"},
        )
        target = create_target(given)

        target([already_loaded, track_file_b])

        assert given.parsed_video_calls() == [
            (FOLDER_B / "b.mp4", given.parse_result.videos_metadata[0])
        ]


class TestLoadTrackFilesInsideAnEventLoop:
    """#Requirement https://openproject.platomo.de/wp/10282"""

    async def test_blocking_call_refuses_to_run_on_the_event_loop(self) -> None:
        """Parsing on the event loop freezes the webui for every connected client."""
        given = setup(
            track_ids=[TrackId("1")],
            video_files=[Path("video1.mp4")],
            track_files=[some_file],
            existing_track_files=[],
            classes={"class1"},
        )
        target = create_target(given)

        with pytest.raises(RuntimeError):
            target([some_file])

        given.track_parser.parse_files.assert_not_called()


class TestLoadTrackFilesOffTheEventLoop:
    """#Requirement https://openproject.platomo.de/wp/10282"""

    async def test_parses_only_the_files_not_already_loaded(self) -> None:
        given = setup(
            track_ids=[TrackId("1")],
            video_files=[Path("video1.mp4")],
            track_files=[other_file],
            existing_track_files=[some_file],
            classes={"class1"},
        )
        target = create_target(given)

        await target.load([some_file, other_file])

        given.track_parser.parse_files.assert_called_once_with([other_file])

    def test_publishes_in_the_same_order_as_the_blocking_call(self) -> None:
        classes = {"class1", "class2"}
        arguments = dict(
            track_ids=[TrackId("1"), TrackId("2")],
            video_files=[Path("video1.mp4"), Path("video2.mp4")],
            track_files=[some_file, other_file],
            existing_track_files=[],
            classes=classes,
        )
        blocking = setup(**arguments)  # type: ignore[arg-type]
        create_target(blocking)([some_file, other_file])

        awaited = setup(**arguments)  # type: ignore[arg-type]
        asyncio.run(create_target(awaited).load([some_file, other_file]))

        # the two runs hold distinct mocks, so compare what was called in what
        # order rather than the mock instances passed along
        assert call_names(awaited) == call_names(blocking)
        assert awaited.track_repository.add_all.call_count == 1

    async def test_parses_off_the_event_loop_and_publishes_on_it(self) -> None:
        """Repositories notify observers that mutate widgets, so publishing must
        stay on the event loop while the expensive parse does not."""
        given = setup(
            track_ids=[TrackId("1")],
            video_files=[Path("video1.mp4")],
            track_files=[some_file],
            existing_track_files=[],
            classes={"class1"},
        )
        threads: dict[str, threading.Thread] = {}
        given.track_parser.parse_files.side_effect = (
            lambda files: threads.setdefault("parse", threading.current_thread())
            and given.parse_result
        )
        given.track_repository.add_all.side_effect = lambda tracks: threads.setdefault(
            "publish", threading.current_thread()
        )
        target = create_target(given)

        await target.load([some_file])

        assert threads["parse"] is not threading.current_thread()
        assert threads["publish"] is threading.current_thread()

    async def test_parses_before_publishing_anything(self) -> None:
        given = setup(
            track_ids=[TrackId("1")],
            video_files=[Path("video1.mp4")],
            track_files=[some_file],
            existing_track_files=[],
            classes={"class1"},
        )
        published_during_parse: list[list] = []

        def record_publishes_so_far(files: list[Path]) -> Any:
            published_during_parse.append(
                list(given.track_repository.add_all.call_args_list)
            )
            return given.parse_result

        given.track_parser.parse_files.side_effect = record_publishes_so_far
        target = create_target(given)

        await target.load([some_file])

        assert published_during_parse == [[]]
        given.track_repository.add_all.assert_called_once()


class TestLoadTrackFilesShowsProgress:
    """#Requirement https://openproject.platomo.de/wp/10282"""

    def test_blocking_call_shows_a_progressbar_until_the_files_are_loaded(
        self,
    ) -> None:
        given = setup(
            track_ids=[TrackId("1"), TrackId("2")],
            video_files=[Path("video1.mp4"), Path("video2.mp4")],
            track_files=[some_file, other_file],
            existing_track_files=[],
            classes={"class1"},
        )
        target = create_target(given)

        target([some_file, other_file])

        given.progressbar.start.assert_called_once_with(
            PARSING_DESCRIPTION, PARSING_UNIT, 2
        )
        given.progressbar.start.return_value.close.assert_called_once_with()

    async def test_shows_a_progressbar_until_the_files_are_loaded(self) -> None:
        """Parsing off the event loop leaves the ui free to show what it is doing."""
        given = setup(
            track_ids=[TrackId("1")],
            video_files=[Path("video1.mp4")],
            track_files=[some_file],
            existing_track_files=[],
            classes={"class1"},
        )
        target = create_target(given)

        await target.load([some_file])

        given.progressbar.start.assert_called_once_with(
            PARSING_DESCRIPTION, PARSING_UNIT, 1
        )
        given.progressbar.start.return_value.close.assert_called_once_with()

    async def test_counts_only_the_files_it_is_going_to_parse(self) -> None:
        given = setup(
            track_ids=[TrackId("1")],
            video_files=[Path("video1.mp4")],
            track_files=[other_file],
            existing_track_files=[some_file],
            classes={"class1"},
        )
        target = create_target(given)

        await target.load([some_file, other_file])

        given.progressbar.start.assert_called_once_with(
            PARSING_DESCRIPTION, PARSING_UNIT, 1
        )

    async def test_opens_the_progressbar_before_parsing_and_closes_it_after(
        self,
    ) -> None:
        given = setup(
            track_ids=[TrackId("1")],
            video_files=[Path("video1.mp4")],
            track_files=[some_file],
            existing_track_files=[],
            classes={"class1"},
        )
        target = create_target(given)

        await target.load([some_file])

        assert call_names(given) == [
            "progressbar.start",
            "track_parser.parse_files",
            "videos_metadata.update",
            "video_parser.parse",
            "video_repository.add_all",
            "track_repository.add_all",
            "tracks_metadata.update_detection_classes",
            "progressbar.start().close",
        ]

    async def test_closes_the_progressbar_when_parsing_fails(self) -> None:
        """A progressbar left open would hide the ui behind it for good."""
        given = setup(
            track_ids=[TrackId("1")],
            video_files=[Path("video1.mp4")],
            track_files=[some_file],
            existing_track_files=[],
            classes={"class1"},
        )
        given.track_parser.parse_files.side_effect = ValueError("broken track file")
        target = create_target(given)

        with pytest.raises(ValueError):
            await target.load([some_file])

        given.progressbar.start.return_value.close.assert_called_once_with()

    async def test_shows_nothing_when_every_file_is_loaded_already(self) -> None:
        given = setup(
            track_ids=[],
            video_files=[],
            track_files=[],
            existing_track_files=[some_file],
            classes=set(),
        )
        target = create_target(given)

        await target.load([some_file])

        given.progressbar.start.assert_not_called()


def call_names(given: "Given") -> list[str]:
    """The collaborator methods called, in call order."""
    return [name for name, _, _ in given.order.mock_calls]


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

    def parsed_video_calls(self) -> list[tuple[Path, Any]]:
        """The (path, metadata) pairs handed to the video parser, in call order."""
        return [
            (call_args.args[0], call_args.args[1])
            for call_args in self.video_parser.parse.call_args_list
        ]

    def __post_init__(self) -> None:
        self.order.track_parser = self.track_parser
        self.order.videos_metadata = self.videos_metadata
        self.order.video_repository = self.video_repository
        self.order.track_repository = self.track_repository
        self.order.video_parser = self.video_parser
        self.order.tracks_metadata = self.tracks_metadata
        self.order.progressbar = self.progressbar


def setup(
    track_ids: list[TrackId],
    video_files: list[Path],
    track_files: list[Path],
    existing_track_files: list[Path],
    classes: set[str],
    georeference_metadata: GeoreferenceMetadata | None = None,
) -> Given:
    videos = create_videos(video_files)
    videos_metadata = [create_video_metadata(video_file) for video_file in video_files]
    detections_metadata = [create_detection_metadata(classes) for _ in track_files]

    track_dataset_result = Mock()
    type(track_dataset_result).track_ids = frozenset(track_ids)
    track_dataset_result.georeference_metadata = georeference_metadata

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


def create_target_for_repo(
    repository: TrackRepository,
    parse_result: TracksParseResult,
) -> LoadTrackFiles:
    """Build a LoadTrackFiles wired to a real TrackRepository.

    All collaborators except the repository (and a configured mock parser)
    are simple Mocks so the test exercises the metadata-compatibility check
    on the real PolarsTrackDataset path.
    """
    track_parser = Mock(spec=TrackParser)
    track_parser.parse_files.return_value = parse_result

    track_file_repository = Mock()
    track_file_repository.get_all.return_value = []

    video_parser = Mock()
    video_parser.parse.side_effect = [
        create_video(Path(str(metadata.path)))
        for metadata in parse_result.videos_metadata
    ]

    return LoadTrackFiles(
        track_parser=track_parser,
        track_repository=repository,
        track_file_repository=track_file_repository,
        video_repository=Mock(),
        video_parser=video_parser,
        progressbar=Mock(),
        tracks_metadata=Mock(),
        videos_metadata=Mock(),
    )
