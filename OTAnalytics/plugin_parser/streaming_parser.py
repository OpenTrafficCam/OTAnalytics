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
    TrackLengthLimit,
    _parse_bz2,
)


class StreamingTrackParser(TrackParser):
    """Parse an ottrk file and convert its contents to our domain objects namely
    `Tracks`.

    Args:
        detection_parser (DetectionParser): parses the given detections.
        format_fixer (OttrkFormatFixer): to fix older ottrk version files.
    """

    def __init__(
        self,
        detection_parser: DetectionParser,
        format_fixer: OttrkFormatFixer = OttrkFormatFixer(),
    ) -> None:
        self._detection_parser = detection_parser
        self._format_fixer = format_fixer

    def parse(self, ottrk_file: Path) -> TrackParseResult:
        """Parse ottrk file and convert its content to domain level objects namely
        `Track`s.

        Args:
            ottrk_file (Path): the track file.

        Returns:
            TrackParseResult: contains tracks and track metadata.
        """
        ottrk_dict = _parse_bz2(ottrk_file)
        fixed_ottrk = self._format_fixer.fix(ottrk_dict)
        dets_list: list[dict] = fixed_ottrk[ottrk_format.DATA][
            ottrk_format.DATA_DETECTIONS
        ]
        metadata_video = ottrk_dict[ottrk_format.METADATA][ottrk_format.VIDEO]
        video_metadata = self._parse_video_metadata(metadata_video)
        tracks = self._detection_parser.parse_tracks(dets_list, metadata_video)
        detection_metadata = self._parse_metadata(ottrk_dict[ottrk_format.METADATA])
        return TrackParseResult(tracks, detection_metadata, video_metadata)

    def _parse_video_metadata(self, metadata_video: dict) -> VideoMetadata:
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


class StreamingDetectionParser(DetectionParser):
    def __init__(
        self,
        track_classification_calculator: TrackClassificationCalculator,
        track_repository: TrackRepository,
        track_length_limit: TrackLengthLimit = DEFAULT_TRACK_LENGTH_LIMIT,
    ):
        self._track_classification_calculator = track_classification_calculator
        self._track_repository = track_repository
        self._track_length_limit = track_length_limit

    def parse_tracks(self, dets: list[dict], metadata_video: dict) -> TrackDataset:
        return StreamingTrackDataset(iterator=self._parse_lazy(dets, metadata_video))

    def _parse_lazy(self, dets: list[dict], metadata_video: dict) -> Iterator[Track]:
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
        self, det_list: list[dict], metadata_video: dict
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
                yield (det.track_id, detections)


class StreamingTrackDataset(TrackDataset):
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
