from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterator, Optional, Sequence

from pyparsing import Iterable

from OTAnalytics.application.datastore import (
    DetectionMetadata,
    TrackParser,
    TrackParseResult,
    VideoMetadata,
)
from OTAnalytics.application.logger import logger
from OTAnalytics.application.state import TracksMetadata, VideosMetadata
from OTAnalytics.domain.track import (
    Detection,
    Track,
    TrackClassificationCalculator,
    TrackDataset,
    TrackHasNoDetectionError,
    TrackId,
    TrackRepository,
)
from OTAnalytics.plugin_datastore.python_track_store import PythonDetection, PythonTrack
from OTAnalytics.plugin_parser import ottrk_dataformat as ottrk_format
from OTAnalytics.plugin_parser.otvision_parser import (
    DEFAULT_TRACK_LENGTH_LIMIT,
    DetectionParser,
    OttrkFormatFixer,
    TrackIdGenerator,
    TrackLengthLimit,
    _parse_bz2,
)

RawDetectionData = list[dict]
RawVideoMetadata = dict
RawFileData = tuple[RawDetectionData, RawVideoMetadata]


class StreamingDetectionParser(
    DetectionParser
):  # code duplication with PythonDetectionParser, hard to extract due to yield!
    """
    Parse the detections of an ottrk file lazily
    and convert them into a `StreamingTrackDataset`.
    (implementation similar to PythonDetectionParser)
    """

    def __init__(
        self,
        track_classification_calculator: TrackClassificationCalculator,
        track_repository: TrackRepository,
        track_length_limit: TrackLengthLimit = DEFAULT_TRACK_LENGTH_LIMIT,
    ):
        self._track_classification_calculator = track_classification_calculator
        self._track_repository = track_repository
        self._track_length_limit = track_length_limit

    def parse_multi_tracks(self, files_data: Iterator[RawFileData]) -> TrackDataset:
        """Parse detections of multiple files lazily
        and convert into a single (stream based) TrackDataset.

        Args:
            files_data (Iterator[RawFileData]):
                a (lazy) iterator of the raw ottrk file data

        Returns:
            TrackDataset: a stream based TrackDataset
        """
        return StreamingTrackDataset(iterator=self._parse_multi_lazy(files_data))

    def parse_tracks(
        self,
        dets: RawDetectionData,
        metadata_video: RawVideoMetadata,
        id_generator: TrackIdGenerator = TrackId,
    ) -> TrackDataset:
        """Parse detections of single ottrk file lazily
        and convert into a single (stream based) TrackDataset.

        Args:
            dets (RawDetectionData): raw detection data
            metadata_video (RawVideoMetadata): raw video metadata

        Returns:
            TrackDataset: a stream based TrackDataset
        """
        return StreamingTrackDataset(iterator=self._parse_lazy(dets, metadata_video))

    def _parse_multi_lazy(self, files_data: Iterator[RawFileData]) -> Iterator[Track]:
        """Create a lazy detection parser yielding all tracks
        from the given raw file data.

        Args:
            files_data (Iterator[RawFileData]): the raw file data to be parsed

        Yields:
            Iterator[Track]: a lazy iterator of all tracks in all given files
        """
        for dets, metadata_video in files_data:
            yield from self._parse_lazy(dets, metadata_video)

    def _parse_lazy(
        self, dets: RawDetectionData, metadata_video: RawVideoMetadata
    ) -> Iterator[Track]:
        """Create a lazy detection parser yielding all tracks
        from the given raw detection data.

        Args:
            dets (RawDetectionData): the raw detection data to be parsed to tracks
            metadata_video (RawVideoMetadata): the raw video metadata to be applied

        Yields:
            Iterator[Track]: a lazy iterator of all contained tracks
        """
        det_list_iterator = self._parse_detections(dets, metadata_video)

        for track_id, detections in det_list_iterator:
            existing_detections = self._get_existing_detections(
                track_id
            )  # TODO Frage: existing detections
            all_detections = existing_detections + detections
            track_length = len(all_detections)
            if (
                self._track_length_limit.lower_bound
                <= track_length
                <= self._track_length_limit.upper_bound
            ):
                sort_dets_by_occurrence = sorted(
                    all_detections, key=lambda det: det.occurrence
                )
                classification = self._track_classification_calculator.calculate(
                    detections
                )
                try:
                    current_track = PythonTrack(
                        _id=track_id,
                        _classification=classification,
                        _detections=sort_dets_by_occurrence,
                    )

                    yield current_track

                except TrackHasNoDetectionError as build_error:
                    # Skip tracks with no detections
                    logger().warning(build_error)
            else:
                logger().debug(
                    f"Trying to construct track (track_id={track_id}). "
                    f"Number of detections ({track_length} detections) is outside "
                    f"the allowed bounds ({self._track_length_limit})."
                )

    def _get_existing_detections(self, track_id: TrackId) -> list[Detection]:
        """
        Returns the detections of an already existing track with the same id or
        an empty list

        Args:
            track_id (TrackId): track id to search for

        Returns:
            list[Detection]: detections of the already existing track or an empty list
        """
        if existing_track := self._track_repository.get_for(track_id):
            return existing_track.detections
        return []

    def _parse_detections(
        self, det_list: RawDetectionData, metadata_video: RawVideoMetadata
    ) -> Iterator[tuple[TrackId, list[Detection]]]:
        """Convert dict to Detection objects and group them by their track id."""
        tracks_dict: dict[TrackId, list[Detection]] = {}
        for det_dict in det_list:
            det = PythonDetection(
                _classification=det_dict[ottrk_format.CLASS],
                _confidence=det_dict[ottrk_format.CONFIDENCE],
                _x=det_dict[ottrk_format.X],
                _y=det_dict[ottrk_format.Y],
                _w=det_dict[ottrk_format.W],
                _h=det_dict[ottrk_format.H],
                _frame=det_dict[ottrk_format.FRAME],
                _occurrence=datetime.fromtimestamp(
                    float(det_dict[ottrk_format.OCCURRENCE]), tz=timezone.utc
                ),
                _interpolated_detection=det_dict[ottrk_format.INTERPOLATED_DETECTION],
                _track_id=TrackId(str(det_dict[ottrk_format.TRACK_ID])),
                _video_name=metadata_video[ottrk_format.FILENAME]
                + metadata_video[ottrk_format.FILETYPE],
            )
            if not tracks_dict.get(det.track_id):
                tracks_dict[det.track_id] = []

            tracks_dict[det.track_id].append(det)  # Group detections by track id

            if det_dict[ottrk_format.FINISHED]:
                detections = tracks_dict[det.track_id]
                del tracks_dict[det.track_id]
                yield (det.track_id, detections)  # yield finished track

        for track_id, detections in tracks_dict.items():
            yield (track_id, detections)  # yield remaining track


class StreamingTrackDataset(TrackDataset):
    """A TrackDataSet based on a lazy Track stream iterator.
    Only provides a reduced set of operations.
    #TODO: check if cli application is possible with this reduced op-set
    """

    def __init__(self, iterator: Iterator[Track]) -> None:
        self._iterator = iterator

    def __iter__(self) -> Iterator[Track]:
        return self._iterator

    def add_all(self, other: Iterable[Track]) -> "TrackDataset":
        raise NotImplementedError

    def get_all_ids(self) -> Iterable[TrackId]:
        raise NotImplementedError

    def get_for(self, id: TrackId) -> Optional[Track]:
        raise NotImplementedError

    def remove(self, track_id: TrackId) -> "TrackDataset":
        raise NotImplementedError

    def clear(self) -> "TrackDataset":
        raise NotImplementedError

    def as_list(self) -> list[Track]:
        raise NotImplementedError

    def split(self, chunks: int) -> Sequence["TrackDataset"]:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError

    def filter_by_min_detection_length(self, length: int) -> "TrackDataset":
        return StreamingTrackDataset(
            FilterIteratorWrapper(length=length, delegate=self._iterator)
        )


class FilterIteratorWrapper(Iterator[Track]):
    """A Track iterator that applies a filter:
    Tracks of length less than a given threshold are not returned.

    Args:
        Iterator (Track): a track iterator to be filtered
    """

    def __init__(self, length: int, delegate: Iterator[Track]) -> None:
        self._length = length
        self._iterator = self._create_iterator(delegate)

    def __next__(self) -> Track:
        return self._iterator.__next__()

    def _create_iterator(self, delegate: Iterator[Track]) -> Iterator[Track]:
        for _track in delegate:
            if len(_track.detections) >= self._length:
                yield _track


class StreamingTrackParseResult(
    TrackParseResult
):  # this is a hacky quick fix since TrackParseResult is frozen,
    # maybe StreamingTrackParser cannot implement TrackParser interface exactly??
    # or register video/dectection metadata collection to be updated dynamically?
    def update_video_metadata(self, video_metadata: VideoMetadata) -> None:
        object.__setattr__(self, "video_metadata", video_metadata)

    def update_detection_metadata(self, detection_metadata: DetectionMetadata) -> None:
        object.__setattr__(self, "detection_metadata", detection_metadata)


class StreamingTrackParser(TrackParser):
    """_summary_

    Args:
        TrackParser (_type_): _description_
    """

    def __init__(
        self,
        streaming_detection_parser: StreamingDetectionParser,
        format_fixer: OttrkFormatFixer = OttrkFormatFixer(),
    ) -> None:
        self._format_fixer = format_fixer
        self._detection_parser = streaming_detection_parser

        self._registered_tracks_metadata: list[TracksMetadata] = []
        self._registered_videos_metadata: list[VideosMetadata] = []

        self._current_video_metadata: VideoMetadata
        self._current_detection_metadata: DetectionMetadata
        self._dir: Path
        self._result: StreamingTrackParseResult
        # _result contains single StreamingTrackDataset + current video / det metadata

    # maybe also allow to register observers to be notified when new file begins!
    def register_tracks_metadata(self, tracks_metadata: TracksMetadata) -> None:
        self._registered_tracks_metadata.append(tracks_metadata)

    def register_videos_metadata(self, videos_metadata: VideosMetadata) -> None:
        self._registered_videos_metadata.append(videos_metadata)

    def _update_registered_metadata_collections(
        self,
        new_detection_metadata: DetectionMetadata,
        new_video_metadata: VideoMetadata,
    ) -> None:
        self._current_detection_metadata = new_detection_metadata
        self._current_video_metadata = new_video_metadata

        for tracks_metadata in self._registered_tracks_metadata:
            tracks_metadata.update_detection_classes(
                new_detection_metadata.detection_classes
            )

        for videos_metadata in self._registered_videos_metadata:
            videos_metadata.update(new_video_metadata)

        if self._result is not None:
            self._result.update_detection_metadata(new_detection_metadata)
            self._result.update_video_metadata(new_video_metadata)

    def parse(self, dir: Path) -> TrackParseResult:
        if self._result is not None:
            raise RuntimeError(
                f"StreamingTrackParser cannot parse '{dir}' "
                + f"as it was already applied to '{self._dir}'!"
            )

        tracks = self._detection_parser.parse_multi_tracks(self._parse_files(dir))

        self._dir = dir

        self._result = StreamingTrackParseResult(
            tracks, self._current_detection_metadata, self._current_video_metadata
        )  # is null possible here?

        return self._result

    def _parse_files(self, dir: Path) -> Iterator[RawFileData]:
        for file_path in self._get_ottrk_files(dir):
            yield self._parse_file(file_path)

    def _get_ottrk_files(self, dir: Path) -> list[Path]:
        return list(
            filter(
                lambda p: p.is_file(), sorted(dir.glob("*.ottrk"), key=lambda p: p.name)
            )
        )

    def _parse_file(self, ottrk_file: Path) -> RawFileData:
        ottrk_dict = _parse_bz2(ottrk_file)
        fixed_ottrk = self._format_fixer.fix(ottrk_dict)
        dets_list: list[dict] = fixed_ottrk[ottrk_format.DATA][
            ottrk_format.DATA_DETECTIONS
        ]
        metadata_video = ottrk_dict[ottrk_format.METADATA][ottrk_format.VIDEO]

        video_metadata = self._parse_video_metadata(metadata_video)
        # tracks = self._detection_parser.parse_tracks(dets_list, metadata_video)
        detection_metadata = self._parse_metadata(ottrk_dict[ottrk_format.METADATA])

        self._update_registered_metadata_collections(detection_metadata, video_metadata)
        return dets_list, metadata_video

    def _parse_video_metadata(
        self, metadata_video: RawVideoMetadata
    ) -> VideoMetadata:  # code duplication, maybe inherit OTTrackParser?
        video_path = (
            metadata_video[ottrk_format.FILENAME]
            + metadata_video[ottrk_format.FILETYPE]
        )
        recorded_start_date = datetime.fromtimestamp(
            float(metadata_video[ottrk_format.RECORDED_START_DATE]), timezone.utc
        )
        expected_duration = (
            timedelta(seconds=metadata_video[ottrk_format.EXPECTED_DURATION])
            if ottrk_format.EXPECTED_DURATION in metadata_video.keys()
            else None
        )
        recorded_fps = float(metadata_video[ottrk_format.RECORDED_FPS])
        actual_fps = (
            float(metadata_video[ottrk_format.ACTUAL_FPS])
            if ottrk_format.ACTUAL_FPS in metadata_video.keys()
            else None
        )
        number_of_frames = int(metadata_video[ottrk_format.NUMBER_OF_FRAMES])
        return VideoMetadata(
            path=video_path,
            recorded_start_date=recorded_start_date,
            expected_duration=expected_duration,
            recorded_fps=recorded_fps,
            actual_fps=actual_fps,
            number_of_frames=number_of_frames,
        )

    def _parse_metadata(self, metadata_detection: dict) -> DetectionMetadata:
        detection_classes_entry: dict[str, str] = metadata_detection[
            ottrk_format.METADATA_DETECTION
        ][ottrk_format.MODEL][ottrk_format.CLASSES]
        detection_classes = frozenset(
            classification for classification in detection_classes_entry.values()
        )
        return DetectionMetadata(detection_classes)
