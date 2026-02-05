from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable, Iterator

from OTAnalytics.application.datastore import (
    DetectionMetadata,
    TrackParser,
    VideoMetadata,
)
from OTAnalytics.application.state import TracksMetadata, VideosMetadata
from OTAnalytics.application.track_input_source import OttrkFileInputSource
from OTAnalytics.domain.progress import LazyProgressbarBuilder
from OTAnalytics.domain.track import (
    Detection,
    Track,
    TrackClassificationCalculator,
    TrackId,
)
from OTAnalytics.domain.track_dataset.track_dataset import TrackDataset
from OTAnalytics.plugin_parser import ottrk_dataformat as ottrk_format
from OTAnalytics.plugin_parser.otvision_parser import (
    TrackIdGenerator,
    TrackLengthLimit,
    create_python_track,
    parse_python_detection,
)
from OTAnalytics.plugin_progress.lazy_tqdm_progressbar import LazyTqdmBuilder


class StreamDetectionParser(ABC):
    """
    Parser the detections data in ottrk data format
    and convert them to a stream of `Track`s.
    """

    @abstractmethod
    def parse_tracks(
        self,
        input_file: str,
        detections: list[dict],
        metadata_video: dict,
        id_generator: TrackIdGenerator = TrackId,
    ) -> Iterator[Track]:
        """Parse the given detections into a stream of Tracks.

        When Detections with the "finished" flag are parsed,
        the according Track is assembled and provided via the stream.

        Args:
            input_file: (str): path of the file tie given detections were read from
            detections (list[dict]): the detections in dict format.
            metadata_video (dict): metadata of the track file in dict format.
            id_generator (TrackIdGenerator): generator used to create track ids.

        Returns:
            Iterator[Track]: a stream of Tracks, one per finished track.
        """
        raise NotImplementedError

    @abstractmethod
    def get_remaining_tracks(self) -> Iterator[Track]:
        """Get yet unparsed tracks,
        that did not show a detection with the "finished" flag."""
        raise NotImplementedError


class PythonStreamDetectionParser(StreamDetectionParser):
    """
    A StreamDetectionParser implementation producing Tracks consisting
    of PythonDetections.
    """

    def __init__(
        self,
        track_classification_calculator: TrackClassificationCalculator,
        track_length_limit: TrackLengthLimit,
    ) -> None:
        self._track_classification_calculator = track_classification_calculator
        self._track_length_limit = track_length_limit
        self._tracks_dict: dict[TrackId, list[Detection]] = dict()

    def parse_tracks(
        self,
        input_file: str,
        detections: list[dict],
        metadata_video: dict,
        id_generator: TrackIdGenerator = TrackId,
    ) -> Iterator[Track]:
        for det_dict in detections:
            det = parse_python_detection(
                metadata_video, id_generator, det_dict, input_file
            )

            # Group detections by track id
            if not self._tracks_dict.get(det.track_id):
                self._tracks_dict[det.track_id] = []
            self._tracks_dict[det.track_id].append(det)
            # the finished flag indicates the last detection of a track
            # so the detections can be assembled to a track object
            if det_dict[ottrk_format.FINISHED]:
                track_detections = self._tracks_dict[det.track_id]
                del self._tracks_dict[det.track_id]

                track = create_python_track(
                    det.track_id,
                    track_detections,
                    self._track_classification_calculator,
                    self._track_length_limit,
                )  # yield finished track
                if track is not None:
                    yield track

    # after all files have been processed,
    # yield all remaining tracks without finished flag
    def get_remaining_tracks(self) -> Iterator[Track]:
        for (
            track_id,
            detections,
        ) in self._tracks_dict.items():
            track = create_python_track(
                track_id,
                detections,
                self._track_classification_calculator,
                self._track_length_limit,
            )
            if track is not None:
                yield track


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


class StreamOttrkParser(StreamTrackParser):
    """
    Parse multiple ottrk files (sorted by 'recorder_start_date' in video metadata).
    Provides a stream of TrackDatasets, one per ottrk file.
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

    def parse(self, input_source: OttrkFileInputSource) -> Iterator[TrackDataset]:
        yield from self._parse_tracks(input_source)

    def _parse_tracks(
        self, input_source: OttrkFileInputSource
    ) -> Iterator[TrackDataset]:
        progressbar: Iterable[Path] = self._progressbar(
            input_source.produce(), unit="files", description="Processed ottrk files: "
        )

        for ottrk_file in progressbar:
            parse_result = self._track_parser.parse(ottrk_file)
            self._update_registered_metadata_collections(
                parse_result.detection_metadata, parse_result.video_metadata
            )
            yield parse_result.tracks
