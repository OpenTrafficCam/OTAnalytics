from abc import ABC, abstractmethod
from typing import  AsyncIterator

from OTAnalytics.application.datastore import (
    TrackParser
)
from tqdm.asyncio import tqdm

from OTAnalytics.application.datastore import DetectionMetadata, VideoMetadata
from OTAnalytics.application.state import TracksMetadata, VideosMetadata
from OTAnalytics.application.track_input_source import OttrkFileInputSource
from OTAnalytics.domain.progress import LazyProgressbarBuilder
from OTAnalytics.domain.track_dataset.track_dataset import TrackDataset
from OTAnalytics.plugin_progress.lazy_tqdm_progressbar import LazyTqdmBuilder


class StreamTrackParser(ABC):
    @abstractmethod
    def parse(self, input_source: OttrkFileInputSource) -> AsyncIterator[TrackDataset]:
        """
        Parse multiple track files and provide
        the parsed Tracks in form of a lazy stream.
        """
        raise NotImplementedError

    @abstractmethod
    def register_tracks_metadata(self, tracks_metadata: TracksMetadata) -> None:
        """Register TracksMetadata to be updated when a new ottrk file is parsed."""
        raise NotImplementedError

    @abstractmethod
    def register_videos_metadata(self, videos_metadata: VideosMetadata) -> None:
        """Register VideosMetadata to be updated when a new ottrk file is parsed."""
        raise NotImplementedError


class StreamOttrkParser(StreamTrackParser):
    """
    Parse multiple ottrk files (sorted by 'recorder_start_date' in video metadata).
    Provides a stream of TrackDatasets, one per ottrk file, plus a final dataset
    for unfinished tracks.
    Allows to register TracksMetadata and VideosMetadata objects to be updated
    with new metadata every time a new ottrk file is parsed.

    Args:
        track_parser (TrackParser): a track parser used per file.
        registered_tracks_metadata (list[TracksMetadata], optional):
            TracksMetadata objects to be updated with each parsed files metadata.
            Defaults to [].
        registered_videos_metadata (list[VideosMetadata], optional):
            VideosMetadata objects to be updated with each parsed files metadata.
            Defaults to [].
        progressbar (LazyProgressbarBuilder, optional):
            a progressbar builder to show progress of processed files.
            Defaults to LazyTqdmProgressbarBuilder().
    """

    def __init__(
        self,
        track_parser: TrackParser,
        registered_tracks_metadata: list[TracksMetadata] = [],
        registered_videos_metadata: list[VideosMetadata] = [],
        progressbar: LazyProgressbarBuilder = LazyTqdmBuilder(),
    ) -> None:
        self._track_parser = track_parser
        self._registered_tracks_metadata: set[TracksMetadata] = set(
            registered_tracks_metadata
        )
        self._registered_videos_metadata: set[VideosMetadata] = set(
            registered_videos_metadata
        )
        self._progressbar = progressbar

    def register_tracks_metadata(self, tracks_metadata: TracksMetadata) -> None:
        """Register TracksMetadata to be updated when a new ottrk file is parsed."""
        self._registered_tracks_metadata.add(tracks_metadata)

    def register_videos_metadata(self, videos_metadata: VideosMetadata) -> None:
        """Register VideosMetadata to be updated when a new ottrk file is parsed."""
        self._registered_videos_metadata.add(videos_metadata)

    def _update_registered_metadata_collections(
        self,
        new_detection_metadata: DetectionMetadata,
        new_video_metadata: VideoMetadata,
    ) -> None:

        for tracks_metadata in self._registered_tracks_metadata:
            tracks_metadata.update_detection_classes(
                new_detection_metadata.detection_classes
            )

        for videos_metadata in self._registered_videos_metadata:
            videos_metadata.update(new_video_metadata)

    async def parse(
        self, input_source: OttrkFileInputSource
    ) -> AsyncIterator[TrackDataset]:
        async for track_dataset in self._parse_tracks(input_source):
            yield track_dataset

    async def _parse_tracks(
        self, input_source: OttrkFileInputSource
    ) -> AsyncIterator[TrackDataset]:
        remaining_tracks: TrackDataset | None = None
        async for ottrk_file in tqdm(input_source.produce(), unit="files", desc="Processed ottrk files: ")
            parse_result = self._track_parser.parse(ottrk_file)
            self._update_registered_metadata_collections(
                parse_result.detection_metadata, parse_result.video_metadata
            )
            combined_tracks = parse_result.tracks
            if remaining_tracks is not None and not remaining_tracks.empty:
                combined_tracks = remaining_tracks.add_all(parse_result.tracks)
            finished_tracks, remaining_tracks = combined_tracks.split_finished()
            if not finished_tracks.empty:
                yield finished_tracks

        if remaining_tracks is not None and not remaining_tracks.empty:
            yield remaining_tracks
