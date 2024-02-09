from dataclasses import dataclass
from datetime import datetime
from math import ceil
from typing import Callable, Iterable, Optional, Sequence

from more_itertools import batched
from shapely import LineString

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
    TrackBuilder,
    TrackBuilderError,
    TrackClassificationCalculator,
    TrackHasNoDetectionError,
    TrackId,
)
from OTAnalytics.domain.track_dataset import (
    TRACK_GEOMETRY_FACTORY,
    FilteredTrackDataset,
    IntersectionPoint,
    TrackDataset,
    TrackGeometryDataset,
)
from OTAnalytics.domain.types import EventType
from OTAnalytics.plugin_datastore.track_geometry_store.pygeos_store import (
    PygeosTrackGeometryDataset,
)
from OTAnalytics.plugin_datastore.track_store import extract_hostname
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
        self.calculator = calculator
        self.track_geometry_factory = track_geometry_factory
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
    ) -> "PythonTrackDataset":
        return PythonTrackDataset(
            {track.id: track for track in tracks}, calculator=calculator
        )

    def add_all(self, other: Iterable[Track]) -> "PythonTrackDataset":
        if isinstance(other, PythonTrackDataset):
            return self.__merge(other._tracks)
        new_tracks = {track.id: track for track in other}
        return self.__merge(new_tracks)

    def __merge(self, other: dict[TrackId, Track]) -> "PythonTrackDataset":
        merged_tracks: dict[TrackId, Track] = {}
        for track_id, other_track in other.items():
            existing_detections = self._get_existing_detections(track_id)
            all_detections = existing_detections + other_track.detections
            sort_dets_by_occurrence = sorted(
                all_detections, key=lambda det: det.occurrence
            )
            classification = self.calculator.calculate(all_detections)
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

    def remove(self, track_id: TrackId) -> "PythonTrackDataset":
        new_tracks = self._tracks.copy()
        del new_tracks[track_id]
        updated_geometry_datasets = self._remove_from_geometry_datasets({track_id})
        return PythonTrackDataset(new_tracks, updated_geometry_datasets)

    def remove_multiple(self, track_ids: set[TrackId]) -> "PythonTrackDataset":
        new_tracks = self._tracks.copy()
        for track_id in track_ids:
            del new_tracks[track_id]
        updated_geometry_datasets = self._remove_from_geometry_datasets(track_ids)
        return PythonTrackDataset(new_tracks, updated_geometry_datasets)

    def _remove_from_geometry_datasets(
        self, track_ids: Iterable[TrackId]
    ) -> dict[RelativeOffsetCoordinate, TrackGeometryDataset]:
        updated = {}
        for offset, geometry_dataset in self._geometry_datasets.items():
            updated[offset] = geometry_dataset.remove(track_ids)
        return updated

    def clear(self) -> "PythonTrackDataset":
        return PythonTrackDataset()

    def as_list(self) -> list[Track]:
        return list(self._tracks.values())

    def split(self, batches: int) -> Sequence["PythonTrackDataset"]:
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
                    calculator=self.calculator,
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

    def filter_by_min_detection_length(self, length: int) -> "PythonTrackDataset":
        filtered_tracks = {
            _id: track
            for _id, track in self._tracks.items()
            if len(track.detections) >= length
        }
        return PythonTrackDataset(filtered_tracks, calculator=self.calculator)

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
            geometry_dataset = self.track_geometry_factory(self, offset)
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
    ) -> tuple["PythonTrackDataset", set[TrackId]]:
        shapely_mapper = ShapelyMapper()

        section_geometry = shapely_mapper.map_coordinates_to_line_string(
            section.get_coordinates()
        )
        intersecting_track_ids = self.intersecting_tracks([section], offset)

        cut_tracks = []
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


class FilteredPythonTrackDataset(FilteredTrackDataset):
    @property
    def include_classes(self) -> frozenset[str]:
        return self._include_classes

    @property
    def exclude_classes(self) -> frozenset[str]:
        return self._exclude_classes

    def __init__(
        self,
        other: PythonTrackDataset,
        include_classes: frozenset[str],
        exclude_classes: frozenset[str],
    ) -> None:
        self._other = other
        self._include_classes = include_classes
        self._exclude_classes = exclude_classes

    def _filter(self) -> PythonTrackDataset:
        """Filter TrackDataset by classifications.

        IMPORTANT: Classifications contained in the include_classes will not be
        removed even if they appear in the set of exclude_classes.
        Furthermore, the whitelist will not be applied if empty.

        Returns:
            PythonTrackDataset: the filtered dataset.
        """
        if not self.include_classes and not self._exclude_classes:
            return self._other

        if self.include_classes:
            logger().info(
                "Apply 'include-classes' filter to filter tracks: "
                f"{self.include_classes}"
                "\n'exclude-classes' filter is not used"
            )
            filtered_dataset = self._get_dataset_with_classes(
                list(self._other.classifications & self.include_classes)
            )
        elif self.exclude_classes:
            logger().info(
                "Apply 'exclude-classes' filter to filter tracks: "
                f"{self.exclude_classes}"
            )
            filtered_dataset = self._get_dataset_with_classes(
                list(self._other.classifications - self.exclude_classes)
            )
        else:
            return self._other
        return filtered_dataset

    def _get_dataset_with_classes(self, classes: list[str]) -> PythonTrackDataset:
        tracks_to_keep: dict[TrackId, Track] = dict()
        tracks_to_remove: list[TrackId] = list()

        for _track in self._other.as_list():
            if _track.classification in classes:
                tracks_to_keep[_track.id] = _track
            else:
                tracks_to_remove.append(_track.id)

        updated_geometry_datasets = self._other._remove_from_geometry_datasets(
            tracks_to_remove
        )
        return PythonTrackDataset(
            tracks_to_keep,
            updated_geometry_datasets,
            self._other.calculator,
            self._other.track_geometry_factory,
        )

    def wrap(self, other: PythonTrackDataset) -> "TrackDataset":
        return FilteredPythonTrackDataset(
            other, self.include_classes, self.exclude_classes
        )

    def add_all(self, other: Iterable[Track]) -> "TrackDataset":
        return self.wrap(self._other.add_all(other))

    def remove(self, track_id: TrackId) -> "TrackDataset":
        return self.wrap(self._other.remove(track_id))

    def remove_multiple(self, track_ids: set[TrackId]) -> "TrackDataset":
        return self.wrap(self._other.remove_multiple(track_ids))

    def clear(self) -> "TrackDataset":
        return self.wrap(self._other.clear())

    def split(self, chunks: int) -> Sequence["TrackDataset"]:
        return [self.wrap(dataset) for dataset in self._other.split(chunks)]

    def calculate_geometries_for(
        self, offsets: Iterable[RelativeOffsetCoordinate]
    ) -> None:
        self._other.calculate_geometries_for(offsets)

    def cut_with_section(
        self, section: Section, offset: RelativeOffsetCoordinate
    ) -> tuple["TrackDataset", set[TrackId]]:
        dataset, original_track_ids = self._other.cut_with_section(section, offset)
        return self.wrap(dataset), original_track_ids


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
