from dataclasses import dataclass
from datetime import datetime
from math import ceil
from typing import Callable, Iterable, Optional, Sequence

from more_itertools import batched
from shapely import LineString

from OTAnalytics.application.logger import logger
from OTAnalytics.domain.common import DataclassValidation
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate
from OTAnalytics.domain.section import Section, SectionId
from OTAnalytics.domain.track import (
    TRACK_CLASSIFICATION,
    TRACK_ID,
    Detection,
    Track,
    TrackBuilder,
    TrackBuilderError,
    TrackClassificationCalculator,
    TrackHasNoDetectionError,
    TrackId,
)
from OTAnalytics.domain.track_dataset import (
    END_FRAME,
    END_OCCURRENCE,
    END_VIDEO_NAME,
    END_X,
    END_Y,
    START_FRAME,
    START_OCCURRENCE,
    START_VIDEO_NAME,
    START_X,
    START_Y,
    TRACK_GEOMETRY_FACTORY,
    IntersectionPoint,
    TrackDataset,
    TrackGeometryDataset,
    TrackSegmentDataset,
)
from OTAnalytics.plugin_datastore.track_geometry_store.pygeos_store import (
    PygeosTrackGeometryDataset,
)
from OTAnalytics.plugin_intersect.shapely.mapping import ShapelyMapper


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


@dataclass(frozen=True)
class PythonTrackPoint:
    x: float
    y: float
    occurrence: datetime
    video_name: str
    frame: int

    @staticmethod
    def from_detection(detection: Detection) -> "PythonTrackPoint":
        return PythonTrackPoint(
            x=detection.x,
            y=detection.y,
            occurrence=detection.occurrence,
            video_name=detection.video_name,
            frame=detection.frame,
        )


@dataclass(frozen=True)
class PythonTrackSegment:
    track_id: str
    track_classification: str
    start: PythonTrackPoint
    end: PythonTrackPoint

    def as_dict(self) -> dict:
        return {
            TRACK_ID: self.track_id,
            TRACK_CLASSIFICATION: self.track_classification,
            START_X: self.start.x,
            START_Y: self.start.y,
            START_OCCURRENCE: self.start.occurrence,
            START_FRAME: self.start.frame,
            START_VIDEO_NAME: self.start.video_name,
            END_X: self.end.x,
            END_Y: self.end.y,
            END_OCCURRENCE: self.end.occurrence,
            END_FRAME: self.end.frame,
            END_VIDEO_NAME: self.end.video_name,
        }


def create_segment_for(
    track: Track, start: Detection, end: Detection
) -> PythonTrackSegment:
    return PythonTrackSegment(
        track_id=track.id.id,
        track_classification=track.classification,
        start=PythonTrackPoint.from_detection(start),
        end=PythonTrackPoint.from_detection(end),
    )


@dataclass(frozen=True)
class PythonTrackSegmentDataset(TrackSegmentDataset):
    segments: list[PythonTrackSegment]

    def apply(self, consumer: Callable[[dict], None]) -> None:
        for segment in self.segments:
            consumer(segment.as_dict())


class PythonTrackDataset(TrackDataset):
    """Pure Python implementation of a TrackDataset."""

    @property
    def track_ids(self) -> frozenset[TrackId]:
        return frozenset(self._tracks.keys())

    @property
    def first_occurrence(self) -> datetime | None:
        if not len(self):
            return None
        return min(
            [track.first_detection.occurrence for track in self._tracks.values()]
        )

    @property
    def last_occurrence(self) -> datetime | None:
        if not len(self):
            return None
        return max([track.last_detection.occurrence for track in self._tracks.values()])

    @property
    def classifications(self) -> frozenset[str]:
        return frozenset([track.classification for track in self._tracks.values()])

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

    def get_for(self, id: TrackId) -> Optional[Track]:
        return self._tracks.get(id)

    def remove(self, track_id: TrackId) -> TrackDataset:
        new_tracks = self._tracks.copy()
        del new_tracks[track_id]
        updated_geometry_datasets = self._remove_from_geometry_datasets({track_id})
        return PythonTrackDataset(new_tracks, updated_geometry_datasets)

    def remove_multiple(self, track_ids: set[TrackId]) -> "TrackDataset":
        new_tracks = self._tracks.copy()
        for track_id in track_ids:
            del new_tracks[track_id]
        updated_geometry_datasets = self._remove_from_geometry_datasets(track_ids)
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

    def get_first_segments(self) -> TrackSegmentDataset:
        segments = [self.__create_first_segment(track) for track in self.as_list()]

        return PythonTrackSegmentDataset(segments)

    @staticmethod
    def __create_first_segment(track: Track) -> PythonTrackSegment:
        start = track.get_detection(0)
        end = track.get_detection(1)
        return create_segment_for(track=track, start=start, end=end)

    def get_last_segments(self) -> TrackSegmentDataset:
        segments = [self.__create_last_segment(track) for track in self.as_list()]

        return PythonTrackSegmentDataset(segments)

    @staticmethod
    def __create_last_segment(track: Track) -> PythonTrackSegment:
        start = track.detections[-2]
        end = track.last_detection
        return create_segment_for(track=track, start=start, end=end)

    def cut_with_section(
        self, section: Section, offset: RelativeOffsetCoordinate
    ) -> tuple[TrackDataset, set[TrackId]]:
        if len(self) == 0:
            logger().info("No tracks to cut")
            return self, set()
        shapely_mapper = ShapelyMapper()

        section_geometry = shapely_mapper.map_coordinates_to_line_string(
            section.get_coordinates()
        )
        intersecting_track_ids = self.intersecting_tracks([section], offset)

        cut_tracks: list[Track] = []
        for track_id in intersecting_track_ids:
            cut_tracks.extend(
                self.__cut_with_section(
                    self._tracks[track_id], section_geometry, offset, shapely_mapper
                )
            )
        return (
            PythonTrackDataset.from_list(cut_tracks),
            intersecting_track_ids,
        )

    def __cut_with_section(
        self,
        track_to_cut: Track,
        section_geometry: LineString,
        offset: RelativeOffsetCoordinate,
        shapely_mapper: ShapelyMapper,
    ) -> list[Track]:
        cut_track_segments: list[Track] = []
        track_builder = SimpleCutTrackSegmentBuilder()
        for current_detection, next_detection in zip(
            track_to_cut.detections[0:-1], track_to_cut.detections[1:]
        ):
            current_coordinate = current_detection.get_coordinate(offset)
            next_coordinate = next_detection.get_coordinate(offset)
            track_segment_geometry = (
                shapely_mapper.map_domain_coordinates_to_line_string(
                    [current_coordinate, next_coordinate]
                )
            )
            if track_segment_geometry.intersects(section_geometry):
                new_track_segment = self._build_track(
                    track_builder,
                    f"{track_to_cut.id.id}_{len(cut_track_segments)}",
                    current_detection,
                )
                cut_track_segments.append(new_track_segment)
            else:
                track_builder.add_detection(current_detection)

        new_track_segment = self._build_track(
            track_builder,
            f"{track_to_cut.id.id}_{len(cut_track_segments)}",
            track_to_cut.last_detection,
        )
        cut_track_segments.append(new_track_segment)

        return cut_track_segments

    def _build_track(
        self, track_builder: TrackBuilder, track_id: str, detection: Detection
    ) -> Track:
        track_builder.add_id(track_id)
        track_builder.add_detection(detection)
        return track_builder.build()


class SimpleCutTrackSegmentBuilder(TrackBuilder):
    """Build tracks that have been cut with a cutting section.

    The builder will be reset after a successful build of a track.

    Args:
        class_calculator (TrackClassificationCalculator): the strategy to determine
            the max class of a track.
    """

    def __init__(
        self, class_calculator: TrackClassificationCalculator = ByMaxConfidence()
    ) -> None:
        self._track_id: TrackId | None = None
        self._detections: list[Detection] = []

        self._class_calculator = class_calculator

    def add_id(self, track_id: str) -> None:
        self._track_id = TrackId(track_id)

    def add_detection(self, detection: Detection) -> None:
        self._detections.append(detection)

    def build(self) -> Track:
        if self._track_id is None:
            raise TrackBuilderError(
                "Track builder setup error occurred. TrackId not set."
            )
        detections = self._build_detections()
        result = PythonTrack(
            self._track_id,
            self._class_calculator.calculate(detections),
            detections,
        )
        self.reset()
        return result

    def reset(self) -> None:
        self._track_id = None
        self._detections = []

    def _build_detections(self) -> list[Detection]:
        if self._track_id is None:
            raise TrackBuilderError(
                "Track builder setup error occurred. TrackId not set."
            )
        new_detections: list[Detection] = []
        for detection in self._detections:
            new_detections.append(
                PythonDetection(
                    detection.classification,
                    detection.confidence,
                    detection.x,
                    detection.y,
                    detection.w,
                    detection.h,
                    detection.frame,
                    detection.occurrence,
                    detection.interpolated_detection,
                    self._track_id,
                    detection.video_name,
                )
            )
        return new_detections
