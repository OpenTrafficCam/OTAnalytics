from pathlib import Path

from OTAnalytics.application.datastore import TrackParser, VideoParser
from OTAnalytics.application.logger import logger
from OTAnalytics.application.state import TracksMetadata, VideosMetadata
from OTAnalytics.domain.progress import ProgressbarBuilder
from OTAnalytics.domain.track_repository import TrackFileRepository, TrackRepository
from OTAnalytics.domain.video import VideoRepository


class LoadTrackFiles:
    def __init__(
        self,
        track_parser: TrackParser,
        track_repository: TrackRepository,
        track_file_repository: TrackFileRepository,
        video_repository: VideoRepository,
        video_parser: VideoParser,
        progressbar: ProgressbarBuilder,
        tracks_metadata: TracksMetadata,
        videos_metadata: VideosMetadata,
    ) -> None:
        self._track_parser = track_parser
        self._track_repository = track_repository
        self._track_file_repository = track_file_repository
        self._video_repository = video_repository
        self._video_parser = video_parser
        self._progressbar = progressbar
        self._tracks_metadata = tracks_metadata
        self._videos_metadata = videos_metadata

    def __call__(self, files: list[Path]) -> None:
        """
        Load and parse the given track file together with the corresponding video file.

        Args:
            files (Path): files in ottrk format.
        """
        if not files:
            return
        parent_folder = files[0].parent
        files_to_load = [
            file for file in files if not self._is_file_already_loaded(file)
        ]
        self._log_already_loaded_files(files, files_to_load)
        if not files_to_load:
            return
        logger().info(f"Loading {len(files_to_load)} track files and videos...")
        parse_result = self._track_parser.parse_files(files_to_load)
        for video_metadata in parse_result.videos_metadata:
            self._videos_metadata.update(video_metadata)

        videos = [
            self._video_parser.parse(
                parent_folder / video_metadata.path, video_metadata
            )
            for video_metadata in parse_result.videos_metadata
        ]
        self._video_repository.add_all(videos)
        self._track_repository.add_all(parse_result.tracks)
        self._track_file_repository.add_all(files_to_load)
        for detection_metadata in parse_result.detections_metadata:
            self._tracks_metadata.update_detection_classes(
                detection_metadata.detection_classes
            )
        logger().info(f"Loaded {len(files_to_load)} track files and videos...")

    def _is_file_already_loaded(self, file: Path) -> bool:
        return file in self._track_file_repository.get_all()

    def _log_already_loaded_files(
        self, files: list[Path], files_to_load: list[Path]
    ) -> None:
        already_loaded_files = set(files) - set(files_to_load)
        for file in already_loaded_files:
            logger().warning(f"File '{file}' already loaded. Skipping... ")
