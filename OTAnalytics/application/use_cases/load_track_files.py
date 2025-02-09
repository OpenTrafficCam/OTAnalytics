from pathlib import Path

from OTAnalytics.application.datastore import (
    TrackParser,
    TrackToVideoRepository,
    TrackVideoParser,
)
from OTAnalytics.application.logger import logger
from OTAnalytics.application.state import TracksMetadata, VideosMetadata
from OTAnalytics.domain.progress import ProgressbarBuilder
from OTAnalytics.domain.track_repository import TrackFileRepository, TrackRepository
from OTAnalytics.domain.video import VideoRepository


class LoadTrackFiles:
    def __init__(
        self,
        track_parser: TrackParser,
        track_video_parser: TrackVideoParser,
        track_repository: TrackRepository,
        track_file_repository: TrackFileRepository,
        video_repository: VideoRepository,
        track_to_video_repository: TrackToVideoRepository,
        progressbar: ProgressbarBuilder,
        tracks_metadata: TracksMetadata,
        videos_metadata: VideosMetadata,
    ) -> None:
        self._track_parser = track_parser
        self._track_video_parser = track_video_parser
        self._track_repository = track_repository
        self._track_file_repository = track_file_repository
        self._video_repository = video_repository
        self._track_to_video_repository = track_to_video_repository
        self._progressbar = progressbar
        self._tracks_metadata = tracks_metadata
        self._videos_metadata = videos_metadata

    def __call__(self, files: list[Path]) -> None:
        """
        Load and parse the given track file together with the corresponding video file.

        Args:
            files (Path): files in ottrk format.
        """
        raised_exceptions: list[Exception] = []
        for file in self._progressbar(
            files, unit="files", description="Processed ottrk files: "
        ):
            if self._is_file_already_loaded(file):
                logger().warning(f"File '{file}' already loaded. Skipping... ")
                continue
            try:

                self.load(file)
            except Exception as cause:
                raised_exceptions.append(cause)
        if raised_exceptions:
            raise ExceptionGroup(
                "Errors occurred while loading the track files:", raised_exceptions
            )

    def _is_file_already_loaded(self, file: Path) -> bool:
        return file in self._track_file_repository.get_all()

    def load(self, file: Path) -> None:
        """
        Load and parse the given track file together with the corresponding video file.

        Args:
            file (Path): file in ottrk format
        """
        parse_result = self._track_parser.parse(file)
        track_ids = list(parse_result.tracks.track_ids)
        track_ids, videos = self._track_video_parser.parse(
            file, track_ids, parse_result.video_metadata
        )
        self._videos_metadata.update(parse_result.video_metadata)
        self._video_repository.add_all(videos)
        self._track_to_video_repository.add_all(track_ids, videos)
        self._track_repository.add_all(parse_result.tracks)
        self._track_file_repository.add(file)
        self._tracks_metadata.update_detection_classes(
            parse_result.detection_metadata.detection_classes
        )
