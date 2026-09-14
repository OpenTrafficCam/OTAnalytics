import asyncio
from pathlib import Path

from OTAnalytics.application.datastore import VideoParser
from OTAnalytics.application.logger import logger
from OTAnalytics.application.parser.track_parser import TrackParser, TracksParseResult
from OTAnalytics.application.state import TracksMetadata, VideosMetadata
from OTAnalytics.domain.progress import ProgressbarBuilder, RunningProgressbar
from OTAnalytics.domain.track_repository import TrackFileRepository, TrackRepository
from OTAnalytics.domain.video import VideoRepository

PARSING_DESCRIPTION = "Parsing track files"
PARSING_UNIT = "files"


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
        """Load and parse track files together with their videos, blocking.

        For use outside an event loop only, such as preloading files given on the
        command line at startup. Nothing is connected then, so there is nothing to
        yield to. Inside an event loop use `load` instead, which keeps the ui
        responsive.

        Args:
            files (list[Path]): files in ottrk format.

        Raises:
            RuntimeError: if called while an event loop is running.
        """
        if self._event_loop_is_running():
            raise RuntimeError(
                "Parsing track files blocks the event loop and freezes the ui."
                " Use load() instead."
            )
        if files_to_load := self._files_to_load(files):
            progressbar = self._start_progress(files_to_load)
            try:
                self._publish(self._parse(files_to_load), files_to_load)
            finally:
                progressbar.close()

    async def load(self, files: list[Path]) -> None:
        """Load and parse track files together with their videos.

        Parsing runs on a worker thread, so the ui keeps repainting while it runs.
        Everything that touches a repository stays on the event loop.

        Args:
            files (list[Path]): files in ottrk format.
        """
        if files_to_load := self._files_to_load(files):
            progressbar = self._start_progress(files_to_load)
            try:
                # parse_files must stay pure: no repository, no observer, no ui. It
                # runs on a worker thread here, and repositories notify observers
                # that mutate widgets, which is only safe on the event loop.
                parse_result = await asyncio.to_thread(self._parse, files_to_load)
                self._publish(parse_result, files_to_load)
            finally:
                progressbar.close()

    def _start_progress(self, files_to_load: list[Path]) -> RunningProgressbar:
        """Show that track files are being parsed until the caller closes it again.

        The parser reports nothing until it is done with all of the files, so this
        counts no progress. It says what is keeping the application busy, and it
        goes away once the files are loaded.

        Args:
            files_to_load (list[Path]): the files about to be parsed.

        Returns:
            RunningProgressbar: the progressbar to close once the files are loaded.
        """
        return self._progressbar.start(
            PARSING_DESCRIPTION, PARSING_UNIT, len(files_to_load)
        )

    @staticmethod
    def _event_loop_is_running() -> bool:
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return False
        return True

    def _files_to_load(self, files: list[Path]) -> list[Path]:
        """Select the files that are not loaded already.

        Args:
            files (list[Path]): files the caller asked to load.

        Returns:
            list[Path]: the files still to be parsed.
        """
        if not files:
            return []
        files_to_load = [
            file for file in files if not self._is_file_already_loaded(file)
        ]
        self._log_already_loaded_files(files, files_to_load)
        return files_to_load

    def _parse(self, files_to_load: list[Path]) -> TracksParseResult:
        """Parse the given track files. Pure: safe to run off the event loop.

        Args:
            files_to_load (list[Path]): files in ottrk format.

        Returns:
            TracksParseResult: the parsed tracks and their metadata.
        """
        logger().info(f"Loading {len(files_to_load)} track files and videos...")
        return self._track_parser.parse_files(files_to_load)

    def _publish(
        self, parse_result: TracksParseResult, files_to_load: list[Path]
    ) -> None:
        """Publish the parse result to the repositories. Event loop only.

        Each video is resolved relative to the parent folder of the track file it was
        parsed from, so track files from different folders each find their own video.
        This relies on `TrackParser.parse_files` returning exactly one `VideoMetadata`
        per input file, in input order; `strict=True` turns a violation of that into
        an error rather than silently dropping videos.

        Args:
            parse_result (TracksParseResult): what the parser produced.
            files_to_load (list[Path]): the files handed to the parser.
        """
        for video_metadata in parse_result.videos_metadata:
            self._videos_metadata.update(video_metadata)

        videos = [
            self._video_parser.parse(
                track_file.parent / video_metadata.path, video_metadata
            )
            for track_file, video_metadata in zip(
                files_to_load, parse_result.videos_metadata, strict=True
            )
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
