from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator

import ijson

from OTAnalytics.application.datastore import (
    DetectionMetadata,
    TrackParser,
    VideoMetadata,
)
from OTAnalytics.application.state import TracksMetadata, VideosMetadata
from OTAnalytics.application.track_input_source import OttrkFileInputSource
from OTAnalytics.domain.progress import LazyProgressbarBuilder
from OTAnalytics.domain.track import Track
from OTAnalytics.domain.track_dataset.track_dataset import TrackDataset
from OTAnalytics.plugin_datastore.track_geometry_store.shapely_store import (
    ShapelyTrackGeometryDataset,
)
from OTAnalytics.plugin_datastore.track_store import (
    PandasByMaxConfidence,
    PandasTrackDataset,
)
from OTAnalytics.plugin_parser import ottrk_dataformat as ottrk_format
from OTAnalytics.plugin_parser.json_parser import parse_json_bz2
from OTAnalytics.plugin_progress.lazy_tqdm_progressbar import LazyTqdmBuilder


def detection_stream_from_json_events(parse_events: Any) -> Iterator[dict]:
    """
    Extract the detection attributes from the deata.detections block
    of the ottrk data format from the given json parser event stream.
    """
    yield from ijson.items(parse_events, "data.detections.item")


def parse_json_bz2_ottrk_bulk(path: Path) -> tuple[dict, Iterator[dict]]:
    """
    Extract metadata block and list of detections attributes of the ottrk data format
    from the bzip2 compressed file at the given path by reading the whole file in bulk.
    """
    ottrk_dict = parse_json_bz2(path)
    dets_list: list[dict] = ottrk_dict[ottrk_format.DATA][ottrk_format.DATA_DETECTIONS]
    metadata = ottrk_dict[ottrk_format.METADATA]

    return metadata, iter(dets_list)


class StreamTrackParser(ABC):
    @abstractmethod
    def parse(self, input_source: OttrkFileInputSource) -> Iterator[TrackDataset]:
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


TrackDatasetFactory = Callable[[list[Track]], TrackDataset]


def default_track_dataset_factory(tracks: list[Track]) -> TrackDataset:
    return PandasTrackDataset.from_list(
        tracks=tracks,
        track_geometry_factory=ShapelyTrackGeometryDataset.from_track_dataset,
        calculator=PandasByMaxConfidence(),
    )


class StreamOttrkParser(StreamTrackParser):
    """
    Parse multiple ottrk files (sorted by 'recorder_start_date' in video metadata).
    Provides a stream of TrackDatasets, one per ottrk file containing all tracks
    from that file. Uses a TrackParser (e.g., OttrkParser) to handle per-file parsing.
    Allows to register TracksMetadata and VideosMetadata objects to be updated
    with new metadata every time a new ottrk file is parsed.

    Args:
        track_parser (TrackParser): a track parser to parse individual ottrk files
        registered_tracks_metadata (list[TracksMetadata], optional):
            TracksMetadata objects to be updated with each parsed files metadata.
            Defaults to [].
        registered_videos_metadata (list[VideosMetadata], optional):
            VideosMetadata objects to be updated with each parsed files metadata.
            Defaults to [].
        progressbar (LazyProgressbarBuilder, optional):
            a progressbar builder to show progress of processed files.
            Defaults to LazyTqdmProgressbarBuilder().
        track_dataset_factory (TrackDataSetFactory, optional):
            a factory to create a new track dataset from a list of Tracks.
            Defaults to PandasTrackDataset.from_list(tracks,
            ShapelyTrackGeometryDataset.from_track_dataset, PandasByMaxConfidence()).
    """

    def __init__(
        self,
        track_parser: TrackParser,
        registered_tracks_metadata: list[TracksMetadata] = [],
        registered_videos_metadata: list[VideosMetadata] = [],
        progressbar: LazyProgressbarBuilder = LazyTqdmBuilder(),
        track_dataset_factory: TrackDatasetFactory = default_track_dataset_factory,
    ) -> None:
        self._track_parser = track_parser
        self._registered_tracks_metadata: set[TracksMetadata] = set(
            registered_tracks_metadata
        )
        self._registered_videos_metadata: set[VideosMetadata] = set(
            registered_videos_metadata
        )
        self._progressbar = progressbar
        self._track_dataset_factory = track_dataset_factory

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

    def parse(self, input_source: OttrkFileInputSource) -> Iterator[TrackDataset]:
        yield from self._parse_tracks(input_source)

    def _parse_tracks(
        self, input_source: OttrkFileInputSource
    ) -> Iterator[TrackDataset]:
        progressbar: Iterable[Path] = self._progressbar(
            input_source.produce(), unit="files", description="Processed ottrk files: "
        )

        remaining_tracks: TrackDataset | None = None

        for ottrk_file in progressbar:
            result = self._track_parser.parse(ottrk_file)

            self._update_registered_metadata_collections(
                result.detection_metadata, result.video_metadata
            )

            # Combine parsed tracks with remaining tracks from previous iteration
            parsed_dataset = result.tracks
            if remaining_tracks is not None and not remaining_tracks.empty:
                combined_dataset = parsed_dataset.add_all(remaining_tracks)
            else:
                combined_dataset = parsed_dataset

            # Split into finished and remaining tracks
            finished_tracks, remaining_tracks = combined_dataset.split_finished()

            # Yield finished tracks if not empty
            if not finished_tracks.empty:
                yield finished_tracks

        # After loop completes, yield remaining tracks if any exist
        if remaining_tracks is not None and not remaining_tracks.empty:
            yield remaining_tracks
