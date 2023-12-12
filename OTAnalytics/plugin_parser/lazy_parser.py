from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, Optional, Sequence

from plugin_datastore.python_track_store import PythonDetection, PythonTrack
from pyparsing import Iterable

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
from OTAnalytics.plugin_parser import ottrk_dataformat as ottrk_format
from OTAnalytics.plugin_parser.otvision_parser import (
    DEFAULT_TRACK_LENGTH_LIMIT,
    DetectionParser,
    TrackLengthLimit,
)


class LazyDetectionParser(DetectionParser):
    def __init__(
        self,
        track_classification_calculator: TrackClassificationCalculator,
        track_repository: TrackRepository,
        track_length_limit: TrackLengthLimit = DEFAULT_TRACK_LENGTH_LIMIT,
    ):
        self._track_classification_calculator = track_classification_calculator
        self._track_repository = track_repository
        self._track_length_limit = track_length_limit
        self._path_cache: dict[str, Path] = {}

    def parse_tracks(self, dets: list[dict], metadata_video: dict) -> TrackDataset:
        return LazyTrackDataset(iterator=self._parse_lazy(dets, metadata_video))

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


class LazyTrackDataset(TrackDataset):
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
        return LazyTrackDataset(
            FilterIteratorWrapper(length=length, delegate=self._iterator)
        )


class FilterIteratorWrapper(Iterator[Track]):
    def __init__(self, length: int, delegate: Iterator[Track]) -> None:
        self._length = length
        self._iterator = self._create_iterator(delegate)

    def __next__(self) -> Track:
        return self._iterator.__next__()

    def _create_iterator(self, delegate: Iterator[Track]) -> Iterator[Track]:
        for _track in delegate:
            if len(_track.detections) >= self._length:
                yield _track
