import bz2
from abc import ABC, abstractmethod
from itertools import islice
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator

import ijson

from OTAnalytics.application.datastore import DetectionMetadata, VideoMetadata
from OTAnalytics.application.state import TracksMetadata, VideosMetadata
from OTAnalytics.domain.progress import ProgressbarBuilder
from OTAnalytics.domain.track import (
    Detection,
    Track,
    TrackClassificationCalculator,
    TrackId,
)
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
from OTAnalytics.plugin_parser.otvision_parser import (
    OttrkFormatFixer,
    OttrkParser,
    TrackIdGenerator,
    TrackLengthLimit,
    create_python_track,
    parse_python_detection,
)
from OTAnalytics.plugin_progress.tqdm_progressbar import TqdmBuilder

RawDetectionData = list[dict]
RawVideoMetadata = dict
RawFileData = tuple[RawDetectionData, RawVideoMetadata, TrackIdGenerator]


def parse_json_bz2_events(path: Path) -> Iterable[tuple[str, str, str]]:
    """
    Provide lazy data stream reading the bzip2 compressed file
    at the given path and interpreting it as json objects.
    """
    with bz2.BZ2File(path) as stream:
        yield from ijson.parse(stream)


def metadata_from_json_events(parse_events: Iterable[tuple[str, str, str]]) -> dict:
    """
    Extract the metadata block of the ottrk data format
    from the given json parser event stream.
    """
    result: dict
    for data in ijson.items(parse_events, "metadata"):
        result = data
        break
    return result


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


class StreamDetectionParser(ABC):
    """
    Parser the detections data in ottrk data format
    and convert them to a stream of `TrackDataset`s.
    """

    @abstractmethod
    def parse_tracks(
        self,
        input_file: str,
        detections: list[dict],
        metadata_video: dict,
        id_generator: TrackIdGenerator = TrackId,
    ) -> Iterator[Track]:
        """Parse the given detections into a stream of TrackDatasets.

        When Detections with the "finished" flag are parsed,
        the according Track is assembled and provided via the stream.

        Args:
            input_file: (str): path of the file tie given detections were read from
            detections (list[dict]): the detections in dict format.
            metadata_video (dict): metadata of the track file in dict format.
            id_generator (TrackIdGenerator): generator used to create track ids.

        Returns:
            Iterator[TrackDataset]: a stream of TackDatasets, one per Track.
        """
        raise NotImplementedError

    @abstractmethod
    def get_remaining_tracks(self) -> Iterator[Track]:
        """Get yet unparsed tracks,
        that did not show a detection with the "finished" flag."""
        raise NotImplementedError


class PythonStreamDetectionParser(StreamDetectionParser):
    """
    A StreamDetectionParser implementation producing SingletonTrackDatasets
    each containing a single PythonTracks consisting of PythonDetections.
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
            )  # yield remaining track
            if track is not None:
                yield track


class StreamTrackParser(ABC):
    @abstractmethod
    def parse(self, files: set[Path]) -> Iterator[TrackDataset]:
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
    Provides a stream of SingletonTackDatasets each containing a single Track.
    Allows to register TracksMetadata and VideosMetadata objects to be updated
    with new metadata every time a new ottrk file is parsed.

    Args:
        detection_parser (StreamDetectionParser): a stream detection parser
        format_fixer (OttrkFormatFixer, optional): a format fixer for ottrk files.
            Defaults to OttrkFormatFixer().
        registered_tracks_metadata (list[TracksMetadata], optional):
            TracksMetadata objects to be updated with each parsed files metadata.
            Defaults to [].
        registered_videos_metadata (list[VideosMetadata], optional):
            VideosMetadata objects to be updated with each parsed files metadata.
            Defaults to [].
        progressbar (ProgressbarBuilder, optional):
            a progressbar builder to show progress of processed files.
            Defaults to TqdmBuilder().
        track_dataset_factory (TrackDataSetFactory, optional):
            a factory to create a new track dataset from a list of Tracks.
            Defaults to PandasTrackDataset.from_list(tracks,
            ShapelyTrackGeometryDataset.from_track_dataset, PandasByMaxConfidence()).
        chunk_size (int, optional): defines the number of tracks to be collected,
            before yielding a TrackDataset containing at most that many Tracks.
            Defaults to 1.
    """

    def __init__(
        self,
        detection_parser: StreamDetectionParser,
        format_fixer: OttrkFormatFixer = OttrkFormatFixer(),
        registered_tracks_metadata: list[TracksMetadata] = [],
        registered_videos_metadata: list[VideosMetadata] = [],
        progressbar: ProgressbarBuilder = TqdmBuilder(),
        track_dataset_factory: TrackDatasetFactory = default_track_dataset_factory,
        chunk_size: int = 5,
    ) -> None:
        self._detection_parser = detection_parser
        self._tracks_dict: dict[TrackId, list[Detection]] = {}
        self._format_fixer = format_fixer
        self._registered_tracks_metadata: set[TracksMetadata] = set(
            registered_tracks_metadata
        )
        self._registered_videos_metadata: set[VideosMetadata] = set(
            registered_videos_metadata
        )
        self._progressbar = progressbar
        self._track_dataset_factory = track_dataset_factory
        self._chunk_size = chunk_size

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

    def parse(self, files: set[Path]) -> Iterator[TrackDataset]:
        iterator = iter(self._parse_tracks(files))
        while True:
            chunk = list(islice(iterator, self._chunk_size))
            if chunk:
                yield self._track_dataset_factory(chunk)
            else:
                return  # explicitly end generator, raises StopIteration exception

    def _parse_tracks(self, files: set[Path]) -> Iterator[Track]:
        sorted_files = self._sort_files(files)
        progressbar: Iterable[Path] = self._progressbar(
            sorted_files, unit="files", description="Processed ottrk files: "
        )

        for ottrk_file in progressbar:
            ottrk_dict = parse_json_bz2(ottrk_file)

            fixed_ottrk = self._format_fixer.fix(ottrk_dict)
            det_list: list[dict] = fixed_ottrk[ottrk_format.DATA][
                ottrk_format.DATA_DETECTIONS
            ]
            metadata = ottrk_dict[ottrk_format.METADATA]
            metadata_video = metadata[ottrk_format.VIDEO]

            detection_metadata = OttrkParser.parse_metadata(metadata)
            video_metadata = OttrkParser.parse_video_metadata(metadata_video)
            id_generator = OttrkParser.create_id_generator_from(metadata)
            self._update_registered_metadata_collections(
                detection_metadata, video_metadata
            )

            del ottrk_dict
            del fixed_ottrk
            del metadata

            yield from self._detection_parser.parse_tracks(
                input_file=str(ottrk_file),
                detections=det_list,
                metadata_video=metadata_video,
                id_generator=id_generator,
            )
            del det_list

        # after all files are processed, yield remaining, unfinished tracks
        yield from self._detection_parser.get_remaining_tracks()

    def _sort_files(self, files: set[Path]) -> list[Path]:
        """
        Sort ottrk files by recorded_start_date in video metadata,
        only considers files with .ottrk extension
        """
        return list(
            sorted(filter(lambda p: p.is_file(), files), key=self._start_date_metadata)
        )

    def _start_date_metadata(self, file: Path) -> float:
        json_events = parse_json_bz2_events(file)
        metadata = metadata_from_json_events(json_events)
        metadata = self._format_fixer.fix_metadata(metadata)
        return float(metadata[ottrk_format.VIDEO][ottrk_format.RECORDED_START_DATE])
