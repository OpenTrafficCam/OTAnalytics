from dataclasses import dataclass
from datetime import datetime
from math import ceil
from typing import Callable, Iterable, Optional, Sequence

from more_itertools import batched

from OTAnalytics.application.logger import logger
from OTAnalytics.domain.common import DataclassValidation
from OTAnalytics.domain.event import Event
from OTAnalytics.domain.geometry import (
    ImageCoordinate,
    RelativeOffsetCoordinate,
    calculate_direction_vector,
)
from OTAnalytics.domain.section import Section, SectionId
from OTAnalytics.domain.track import (
    Detection,
    Track,
    TrackClassificationCalculator,
    TrackHasNoDetectionError,
    TrackId,
)
from OTAnalytics.domain.track_dataset import (
    TRACK_GEOMETRY_FACTORY,
    IntersectionPoint,
    TrackDataset,
    TrackGeometryDataset,
)
from OTAnalytics.domain.types import EventType
from OTAnalytics.plugin_datastore.track_geometry_store.pygeos_store import (
    PygeosTrackGeometryDataset,
)
from OTAnalytics.plugin_datastore.track_store import extract_hostname


@dataclass(frozen=True)
class PythonDetection(Detection, DataclassValidation):
    """Represents a detection belonging to a `Track`.

    The detection uses the xywh bounding box format.


    Raises:
        ValueError: confidence not in [0,1]
        ValueError: x < 0
        ValueError: y < 0
        ValueError: w < 0
        ValueError: h < 0
        ValueError: frame < 0
        ValueError: track_id < 0


    Args:
        _classification (str): class of detection.
        _confidence (float): the confidence.
        _x (float): the x coordinate component of the bounding box.
        _y (float): the y coordinate component of the bounding box.
        _w (float): the width component of the bounding box.
        _h (float): the height component of the bounding box.
        _frame (int): the frame that the detection belongs to.
        _occurrence (datetime): the time of the detection's occurrence.
        _interpolated_detection (bool): whether this detection is interpolated.
        _track_id (TrackId): the track id this detection belongs to.
        _video_name (str): name of video that this detection belongs.
    """

    _classification: str
    _confidence: float
    _x: float
    _y: float
    _w: float
    _h: float
    _frame: int
    _occurrence: datetime
    _interpolated_detection: bool
    _track_id: TrackId
    _video_name: str

    @property
    def classification(self) -> str:
        return self._classification

    @property
    def confidence(self) -> float:
        return self._confidence

    @property
    def x(self) -> float:
        return self._x

    @property
    def y(self) -> float:
        return self._y

    @property
    def w(self) -> float:
        return self._w

    @property
    def h(self) -> float:
        return self._h

    @property
    def frame(self) -> int:
        return self._frame

    @property
    def occurrence(self) -> datetime:
        return self._occurrence

    @property
    def interpolated_detection(self) -> bool:
        return self._interpolated_detection

    @property
    def track_id(self) -> TrackId:
        return self._track_id

    @property
    def video_name(self) -> str:
        return self._video_name

    def _validate(self) -> None:
        self._validate_confidence_greater_equal_zero()
        self._validate_bbox_values()
        self._validate_frame_id_greater_equal_one()

    def _validate_confidence_greater_equal_zero(self) -> None:
        if self.confidence < 0 or self.confidence > 1:
            raise ValueError("confidence must be in range [0,1]")

    def _validate_bbox_values(self) -> None:
        if self.x < 0:
            raise ValueError("x must be greater equal 0")
        if self.y < 0:
            raise ValueError("y must be greater equal 0")
        if self.w < 0:
            raise ValueError("w must be greater equal 0")
        if self.h < 0:
            raise ValueError("h must be greater equal 0")

    def _validate_frame_id_greater_equal_one(self) -> None:
        if self.frame < 1:
            raise ValueError("frame number must be greater equal 1")


@dataclass(frozen=True)
class PythonTrack(Track, DataclassValidation):
    """Represents the track of an object as seen in the task of object tracking
    (computer vision).

    Args:
        _id (TrackId): the track id.
        _classification: the max classification of this track.
        _detections (list[Detection]): the detections belonging to this track.

    Raises:
        ValueError: if detections are not sorted by `occurrence`.
        ValueError: if an empty detections list has been passed.
    """

    _id: TrackId
    _classification: str
    _detections: list[Detection]

    @property
    def id(self) -> TrackId:
        return self._id

    @property
    def classification(self) -> str:
        return self._classification

    @property
    def detections(self) -> list[Detection]:
        return self._detections

    def get_detection(self, index: int) -> Detection:
        return self._detections[index]

    def _validate(self) -> None:
        self._validate_track_has_detections()
        self._validate_detections_sorted_by_occurrence()

    def _validate_track_has_detections(self) -> None:
        if not self._detections:
            raise TrackHasNoDetectionError(
                self.id,
                (
                    f"Trying to construct track (track_id={self.id.id})"
                    " with no detections."
                ),
            )

    def _validate_detections_sorted_by_occurrence(self) -> None:
        if self._detections != sorted(self._detections, key=lambda det: det.occurrence):
            raise ValueError("detections must be sorted by occurrence")

    @property
    def first_detection(self) -> Detection:
        """Get first detection of track.

        Returns:
            Detection: the first detection.
        """
        return self._detections[0]

    @property
    def last_detection(self) -> Detection:
        """Get last detection of track.

        Returns:
            Detection: the last detection.
        """
        return self._detections[-1]


class ByMaxConfidence(TrackClassificationCalculator):
    """Determine a track's classification by its detections max confidence."""

    def calculate(self, detections: list[Detection]) -> str:
        classifications: dict[str, float] = {}
        for detection in detections:
            if classifications.get(detection.classification):
                classifications[detection.classification] += detection.confidence
            else:
                classifications[detection.classification] = detection.confidence

        return max(classifications, key=lambda x: classifications[x])


class PythonTrackDataset(TrackDataset):
    """Pure Python implementation of a TrackDataset."""

    def __init__(
        self,
        values: Optional[dict[TrackId, Track]] = None,
        geometry_datasets: dict[RelativeOffsetCoordinate, TrackGeometryDataset]
        | None = None,
        calculator: TrackClassificationCalculator = ByMaxConfidence(),
        track_geometry_factory: TRACK_GEOMETRY_FACTORY = (
            PygeosTrackGeometryDataset.from_track_dataset
        ),
    ) -> None:
        if values is None:
            values = {}
        self._tracks = values
        self._calculator = calculator
        self._track_geometry_factory = track_geometry_factory
        if geometry_datasets is None:
            self._geometry_datasets = dict[
                RelativeOffsetCoordinate, TrackGeometryDataset
            ]()
        else:
            self._geometry_datasets = geometry_datasets

    @staticmethod
    def from_list(
        tracks: list[Track],
        calculator: TrackClassificationCalculator = ByMaxConfidence(),
    ) -> TrackDataset:
        return PythonTrackDataset(
            {track.id: track for track in tracks}, calculator=calculator
        )

    def add_all(self, other: Iterable[Track]) -> "TrackDataset":
        if isinstance(other, PythonTrackDataset):
            return self.__merge(other._tracks)
        new_tracks = {track.id: track for track in other}
        return self.__merge(new_tracks)

    def __merge(self, other: dict[TrackId, Track]) -> TrackDataset:
        merged_tracks: dict[TrackId, Track] = {}
        for track_id, other_track in other.items():
            existing_detections = self._get_existing_detections(track_id)
            all_detections = existing_detections + other_track.detections
            sort_dets_by_occurrence = sorted(
                all_detections, key=lambda det: det.occurrence
            )
            classification = self._calculator.calculate(all_detections)
            try:
                current_track = PythonTrack(
                    _id=track_id,
                    _classification=classification,
                    _detections=sort_dets_by_occurrence,
                )
                merged_tracks[current_track.id] = current_track
            except TrackHasNoDetectionError as build_error:
                logger().exception(build_error, exc_info=True)
        merged = self._tracks | merged_tracks
        updated_geometry_dataset = self._add_to_geometry_dataset(merged_tracks.values())
        return PythonTrackDataset(merged, updated_geometry_dataset)

    def _add_to_geometry_dataset(
        self, new_tracks: Iterable[Track]
    ) -> dict[RelativeOffsetCoordinate, TrackGeometryDataset]:
        updated = dict[RelativeOffsetCoordinate, TrackGeometryDataset]()
        for offset, geometries in self._geometry_datasets.items():
            updated[offset] = geometries.add_all(new_tracks)
        return updated

    def _get_existing_detections(self, track_id: TrackId) -> list[Detection]:
        """
        Returns the detections of an already existing track with the same id or
        an empty list

        Args:
            track_id (TrackId): track id to search for

        Returns:
            list[Detection]: detections of the already existing track or an empty list
        """
        if existing_track := self._tracks.get(track_id):
            return existing_track.detections
        return []

    def get_all_ids(self) -> Iterable[TrackId]:
        return self._tracks.keys()

    def get_for(self, id: TrackId) -> Optional[Track]:
        return self._tracks.get(id)

    def remove(self, track_id: TrackId) -> TrackDataset:
        new_tracks = self._tracks.copy()
        del new_tracks[track_id]
        updated_geometry_datasets = self._remove_from_geometry_datasets({track_id})
        return PythonTrackDataset(new_tracks, updated_geometry_datasets)

    def _remove_from_geometry_datasets(
        self, track_ids: set[TrackId]
    ) -> dict[RelativeOffsetCoordinate, TrackGeometryDataset]:
        updated = {}
        for offset, geometry_dataset in self._geometry_datasets.items():
            updated[offset] = geometry_dataset.remove(track_ids)
        return updated

    def clear(self) -> TrackDataset:
        return PythonTrackDataset()

    def as_list(self) -> list[Track]:
        return list(self._tracks.values())

    def split(self, batches: int) -> Sequence["TrackDataset"]:
        dataset_size = len(self._tracks)
        batch_size = ceil(dataset_size / batches)

        dataset_batches = []
        for batch in batched(self._tracks.items(), batch_size):
            current_batch = dict(batch)
            current_geometry_datasets = self._get_geometries_for(current_batch.keys())
            dataset_batches.append(
                PythonTrackDataset(
                    current_batch,
                    current_geometry_datasets,
                    calculator=self._calculator,
                )
            )
        return dataset_batches

    def _get_geometries_for(
        self, track_ids: Iterable[TrackId]
    ) -> dict[RelativeOffsetCoordinate, TrackGeometryDataset]:
        _ids = [track_id.id for track_id in track_ids]
        return {
            offset: geometry_dataset.get_for(_ids)
            for offset, geometry_dataset in self._geometry_datasets.items()
        }

    def __len__(self) -> int:
        return len(self._tracks)

    def filter_by_min_detection_length(self, length: int) -> "TrackDataset":
        filtered_tracks = {
            _id: track
            for _id, track in self._tracks.items()
            if len(track.detections) >= length
        }
        return PythonTrackDataset(filtered_tracks, calculator=self._calculator)

    def intersecting_tracks(
        self, sections: list[Section], offset: RelativeOffsetCoordinate
    ) -> set[TrackId]:
        geometry_dataset = self._get_geometry_dataset_for(offset)
        return geometry_dataset.intersecting_tracks(sections)

    def _get_geometry_dataset_for(
        self, offset: RelativeOffsetCoordinate
    ) -> TrackGeometryDataset:
        """Retrieves track geometries for given offset.

        If offset does not exist, a new TrackGeometryDataset with the applied offset
        will be created and saved.

        Args:
            offset (RelativeOffsetCoordinate): the offset to retrieve track geometries
                for.

        Returns:
            TrackGeometryDataset: the track geometry dataset with the given offset
                applied.
        """
        if (geometry_dataset := self._geometry_datasets.get(offset, None)) is None:
            geometry_dataset = self._track_geometry_factory(self, offset)
            self._geometry_datasets[offset] = geometry_dataset
        return geometry_dataset

    def intersection_points(
        self, sections: list[Section], offset: RelativeOffsetCoordinate
    ) -> dict[TrackId, list[tuple[SectionId, IntersectionPoint]]]:
        geometry_dataset = self._get_geometry_dataset_for(offset)
        return geometry_dataset.intersection_points(sections)

    def contained_by_sections(
        self, sections: list[Section], offset: RelativeOffsetCoordinate
    ) -> dict[TrackId, list[tuple[SectionId, list[bool]]]]:
        geometry_dataset = self._get_geometry_dataset_for(offset)
        return geometry_dataset.contained_by_sections(sections)

    def calculate_geometries_for(
        self, offsets: Iterable[RelativeOffsetCoordinate]
    ) -> None:
        for offset in offsets:
            if offset not in self._geometry_datasets.keys():
                self._geometry_datasets[offset] = self._get_geometry_dataset_for(offset)

    def apply_to_first_segments(self, consumer: Callable[[Event], None]) -> None:
        for track in self.as_list():
            event = self.__create_enter_scene_event(track)
            consumer(event)

    def __create_enter_scene_event(self, track: Track) -> Event:
        return Event(
            road_user_id=track.id.id,
            road_user_type=track.classification,
            hostname=extract_hostname(track.first_detection.video_name),
            occurrence=track.first_detection.occurrence,
            frame_number=track.first_detection.frame,
            section_id=None,
            event_coordinate=ImageCoordinate(
                track.first_detection.x, track.first_detection.y
            ),
            event_type=EventType.ENTER_SCENE,
            direction_vector=calculate_direction_vector(
                track.first_detection.x,
                track.first_detection.y,
                track.detections[1].x,
                track.detections[1].y,
            ),
            video_name=track.first_detection.video_name,
        )

    def apply_to_last_segments(self, consumer: Callable[[Event], None]) -> None:
        for track in self.as_list():
            event = self.__create_leave_scene_event(track)
            consumer(event)

    def __create_leave_scene_event(self, track: Track) -> Event:
        return Event(
            road_user_id=track.id.id,
            road_user_type=track.classification,
            hostname=extract_hostname(track.last_detection.video_name),
            occurrence=track.last_detection.occurrence,
            frame_number=track.last_detection.frame,
            section_id=None,
            event_coordinate=ImageCoordinate(
                track.last_detection.x, track.last_detection.y
            ),
            event_type=EventType.LEAVE_SCENE,
            direction_vector=calculate_direction_vector(
                track.detections[-2].x,
                track.detections[-2].y,
                track.last_detection.x,
                track.last_detection.y,
            ),
            video_name=track.last_detection.video_name,
        )

    def cut_with_section(
        self, section: Section, offset: RelativeOffsetCoordinate
    ) -> tuple[TrackDataset, set[TrackId]]:
        raise NotImplementedError
