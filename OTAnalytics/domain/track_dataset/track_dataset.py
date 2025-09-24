from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Iterable, Iterator, Optional, Sequence

from OTAnalytics.domain.event import (
    Event,
    EventBuilder,
    EventDataset,
    PythonEventDataset,
    SectionEventBuilder,
)
from OTAnalytics.domain.geometry import (
    Coordinate,
    RelativeOffsetCoordinate,
    calculate_direction_vector,
)
from OTAnalytics.domain.section import Section, SectionId
from OTAnalytics.domain.track import Track, TrackId
from OTAnalytics.domain.types import EventType

START_X: str = "start_x"
START_Y: str = "start_y"
START_W: str = "start_w"
START_H: str = "start_h"
START_OCCURRENCE: str = "start_occurrence"
START_FRAME: str = "start_frame"
START_VIDEO_NAME: str = "start_video_name"
END_X: str = "end_x"
END_Y: str = "end_y"
END_W: str = "end_w"
END_H: str = "end_h"
END_OCCURRENCE: str = "end_occurrence"
END_FRAME: str = "end_frame"
END_VIDEO_NAME: str = "end_video_name"
CURRENT_X: str = "current_x"
CURRENT_Y: str = "current_y"
PREVIOUS_X: str = "previous_x"
PREVIOUS_Y: str = "previous_y"


class TrackDoesNotExistError(Exception):
    pass


def contains_true(section_data: list[tuple[SectionId, list[bool]]]) -> bool:
    for _, bool_list in section_data:
        if any(bool_list):
            return True
    return False


@dataclass(frozen=True, order=True)
class IntersectionPoint:
    upper_index: int
    relative_position: float

    @property
    def lower_index(self) -> int:
        """
        Returns the lower index based on the current upper index value, ensuring the
        result is at least zero.

        This property calculates the lower index by subtracting one from the
        'upper_index' attribute. If the result is less than zero, it returns zero
        instead, ensuring the index does not go negative.

        Returns:
            int: The lower index value computed as `upper_index - 1` or 0 if the result
            would be negative.
        """
        return max(self.upper_index - 1, 0)


class TrackSegmentDataset(ABC):
    """Collection of track segments. A track segment consists of a start and an end
    point with additional information about the corresponding detection.
    """

    @abstractmethod
    def apply(self, consumer: Callable[[dict], None]) -> None:
        """Apply the given consumer to the track segments."""
        raise NotImplementedError


class TrackIdSet(ABC):

    @abstractmethod
    def __eq__(self, other: Any) -> bool:
        raise NotImplementedError

    @abstractmethod
    def __iter__(self) -> Iterator[TrackId]:
        raise NotImplementedError

    @abstractmethod
    def __len__(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def intersection(self, other: "TrackIdSet") -> "TrackIdSet":
        raise NotImplementedError

    @abstractmethod
    def union(self, other: "TrackIdSet") -> "TrackIdSet":
        raise NotImplementedError

    @abstractmethod
    def difference(self, other: "TrackIdSet") -> "TrackIdSet":
        raise NotImplementedError


class TrackIdSetFactory(ABC):
    @abstractmethod
    def create(self, track_ids: Iterable[TrackId] | Iterable[str]) -> TrackIdSet:
        raise NotImplementedError


class EmptyTrackIdSet(TrackIdSet):
    def __eq__(self, other: Any) -> bool:
        return isinstance(other, EmptyTrackIdSet)

    def __iter__(self) -> Iterator[TrackId]:
        return iter([])

    def __len__(self) -> int:
        return 0

    def intersection(self, other: "TrackIdSet") -> "TrackIdSet":
        return self

    def union(self, other: "TrackIdSet") -> "TrackIdSet":
        return other

    def difference(self, other: "TrackIdSet") -> "TrackIdSet":
        return self


def concat(
    track_id_sets: Iterable[TrackIdSet],
) -> TrackIdSet:
    """Concatenate multiple track ID sets into a single track ID set."""
    result: TrackIdSet = EmptyTrackIdSet()
    for current in track_id_sets:
        result = result.union(current)
    return result


class TrackDataset(ABC):
    @property
    @abstractmethod
    def track_ids(self) -> TrackIdSet:
        raise NotImplementedError

    @property
    @abstractmethod
    def first_occurrence(self) -> datetime | None:
        raise NotImplementedError

    @property
    @abstractmethod
    def last_occurrence(self) -> datetime | None:
        raise NotImplementedError

    @property
    @abstractmethod
    def classifications(self) -> frozenset[str]:
        raise NotImplementedError

    @property
    @abstractmethod
    def empty(self) -> bool:
        raise NotImplementedError

    def __iter__(self) -> Iterator[Track]:
        yield from self.as_list()

    @abstractmethod
    def __len__(self) -> int:
        """Number of tracks in the dataset."""
        raise NotImplementedError

    @abstractmethod
    def add_all(self, other: Iterable[Track]) -> "TrackDataset":
        raise NotImplementedError

    @abstractmethod
    def get_for(self, id: TrackId) -> Optional[Track]:
        """
        Retrieve a track for the given id.

        Args:
            id (TrackId): id to search for

        Returns:
            Optional[Track]: track if it exists
        """
        raise NotImplementedError

    @abstractmethod
    def remove(self, track_id: TrackId) -> "TrackDataset":
        raise NotImplementedError

    @abstractmethod
    def remove_multiple(self, track_ids: TrackIdSet) -> "TrackDataset":
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> "TrackDataset":
        """
        Return an empty version of the current TrackDataset.
        """
        raise NotImplementedError

    @abstractmethod
    def as_list(self) -> list[Track]:
        raise NotImplementedError

    @abstractmethod
    def intersecting_tracks(
        self, sections: list[Section], offset: RelativeOffsetCoordinate
    ) -> TrackIdSet:
        """Return a set of tracks intersecting a set of sections.

        Args:
            sections (list[Section]): the list of sections to intersect.
            offset (RelativeOffsetCoordinate): the offset to be applied to the tracks.

        Returns:
            set[TrackId]: the track ids intersecting the given sections.
        """
        raise NotImplementedError

    @abstractmethod
    def intersection_points(
        self, sections: list[Section], offset: RelativeOffsetCoordinate
    ) -> "IntersectionPointsDataset":
        """
        Return the intersection points wrapped in an IntersectionPointsDataset.

        Args:
            sections (list[Section]): the sections to intersect with.
            offset (RelativeOffsetCoordinate): the offset to be applied to the tracks.

        Returns:
            IntersectionPointsDataset: the intersection points dataset.
        """
        raise NotImplementedError

    @abstractmethod
    def contained_by_sections(
        self, sections: list[Section], offset: RelativeOffsetCoordinate
    ) -> dict[TrackId, list[tuple[SectionId, list[bool]]]]:
        """Return whether track coordinates are contained by the given sections.

        Args:
             sections (list[Section]): the sections.
             offset (RelativeOffsetCoordinate): the offset to be applied to the tracks.

        Returns:
            dict[TrackId, list[tuple[SectionId, list[bool]]]]: boolean mask of track
                coordinates contained by given sections.
        """
        raise NotImplementedError

    @abstractmethod
    def split(self, chunks: int) -> Sequence["TrackDataset"]:
        raise NotImplementedError

    @abstractmethod
    def filter_by_min_detection_length(self, length: int) -> "TrackDataset":
        """Filter tracks by the minimum length of detections.

        Args:
            length (int): minimum number detections a track should have.

        Returns:
             TrackDataset: the filtered dataset.
        """
        raise NotImplementedError

    @abstractmethod
    def calculate_geometries_for(
        self, offsets: Iterable[RelativeOffsetCoordinate]
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_first_segments(self) -> TrackSegmentDataset:
        """Get first segments of each track."""
        raise NotImplementedError

    @abstractmethod
    def get_last_segments(self) -> TrackSegmentDataset:
        """Get last segments of each track"""
        raise NotImplementedError

    @abstractmethod
    def cut_with_section(
        self, section: Section, offset: RelativeOffsetCoordinate
    ) -> tuple["TrackDataset", TrackIdSet]:
        """Use section to cut track with TrackDataset.

        Args:
            section (Section): the section to cut the TrackDataset with.
            offset (RelativeOffsetCoordinate): the offset to be applied to the tracks.

        Returns:
            tuple[TrackDataset, TrackIdSet]: the dataset containing the cut tracks
                and the original track ids that have been cut.
        """
        raise NotImplementedError

    @abstractmethod
    def get_max_confidences_for(self, track_ids: TrackIdSet) -> dict[str, float]:
        """Get max confidences for given track ids.

        Args:
            track_ids: the track ids to get the max confidences for.

        Returns:
            dict[TrackId, float]: the max confidence values for the track ids.

        Raises:
            TrackDoesNotExistError: if given track id does not exist within dataset.
        """
        raise NotImplementedError

    @abstractmethod
    def revert_cuts_for(
        self, original_track_ids: TrackIdSet
    ) -> tuple["TrackDataset", TrackIdSet, TrackIdSet]:
        """
        Reverses the effects of track cutting operations for the specified original
        track IDs.

        Args:
            original_track_ids (frozenset[TrackId]): Set of original track IDs to be
                restored from their cut segments.

        Returns:
            tuple[TrackDataset, frozenset[TrackId], frozenset[TrackId]:
                1. A new dataset where the specified tracks have been reverted to their
                    original IDs (uncut state).
                2. The reverted track IDs.
                3. The cut track IDs that were removed during the reversion process.
        """
        raise NotImplementedError

    @abstractmethod
    def remove_by_original_ids(
        self, original_ids: TrackIdSet
    ) -> tuple["TrackDataset", TrackIdSet]:
        """
        Remove tracks with the specified original IDs and return a new dataset.

        Args:
            original_ids (TrackIdSet): The original IDs of tracks to remove

        Returns:
            tuple[TrackDataset, TrackIdSet]:
                1. A new dataset without the specified tracks
                2. The set of actual track IDs that were removed during the removal
                    process.
        """
        raise NotImplementedError

    def ids_inside(self, sections: list[Section]) -> TrackIdSet:
        raise NotImplementedError


class TrackGeometryDataset(ABC):
    """Dataset containing track geometries.

    Only tracks of size greater equal two are contained in the dataset.
    Tracks of size less than two will not be contained in the dataset
    since it is not possible to construct a track with less than two
    coordinates.
    """

    @property
    @abstractmethod
    def track_ids(self) -> set[str]:
        """Get track ids of tracks stored in dataset.

        Returns:
            set[str]: the track ids stored.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def offset(self) -> RelativeOffsetCoordinate:
        raise NotImplementedError

    @property
    @abstractmethod
    def empty(self) -> bool:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def from_track_dataset(
        dataset: TrackDataset, offset: RelativeOffsetCoordinate
    ) -> "TrackGeometryDataset":
        raise NotImplementedError

    @abstractmethod
    def add_all(self, tracks: Iterable[Track]) -> "TrackGeometryDataset":
        """Add tracks to existing dataset.

        Pre-existing tracks will be overwritten.

        Args:
            tracks (Iterable[Track]): the tracks to add.

        Returns:
            TrackGeometryDataset: the dataset with tracks added.

        """
        raise NotImplementedError

    @abstractmethod
    def remove(self, ids: Sequence[str]) -> "TrackGeometryDataset":
        """Remove track geometries with given ids from dataset.

        Args:
            ids (Sequence[str]): the track geometries to remove.

        Returns:
            TrackGeometryDataset: the dataset with tracks removed.
        """
        raise NotImplementedError

    @abstractmethod
    def get_for(self, track_ids: list[str]) -> "TrackGeometryDataset":
        """Get geometries for given track ids if they exist.

        Ids that do not exist will not be included in the dataset.

        Args:
            track_ids (list[str]): the track ids.

        Returns:
            TrackGeometryDataset: the dataset with tracks.
        """
        raise NotImplementedError

    @abstractmethod
    def intersecting_tracks(self, sections: list[Section]) -> TrackIdSet:
        """Return a set of tracks intersecting a set of sections.

        Args:
            sections (list[Section]): the list of sections to intersect.

        Returns:
            TrackIdSet: the track ids intersecting the given sections.
        """
        raise NotImplementedError

    @abstractmethod
    def intersection_points(
        self, sections: list[Section]
    ) -> dict[TrackId, list[tuple[SectionId, IntersectionPoint]]]:
        """
        Return the intersection points resulting from the tracks and the
        given sections.

        Args:
            sections (list[Section]): the sections to intersect with.

        Returns:
            dict[TrackId, list[tuple[SectionId]]]: the intersection points.
        """
        raise NotImplementedError

    @abstractmethod
    def contained_by_sections(
        self, sections: list[Section]
    ) -> dict[TrackId, list[tuple[SectionId, list[bool]]]]:
        """Return whether track coordinates are contained by the given sections.

        Args:
             sections (list[Section]): the sections.

        Returns:
            dict[TrackId, list[tuple[SectionId, list[bool]]]]: boolean mask
                of track coordinates contained by given sections.
        """
        raise NotImplementedError

    @abstractmethod
    def __eq__(self, other: Any) -> bool:
        raise NotImplementedError


class IntersectionPointsDataset(ABC):
    """Dataset containing intersection points between tracks and sections."""

    @abstractmethod
    def items(
        self,
    ) -> Iterator[tuple[TrackId, list[tuple[SectionId, IntersectionPoint]]]]:
        """Iterate over track IDs and their intersection points.

        Returns:
            Iterator yielding (track_id, intersection_points) tuples.
        """
        raise NotImplementedError

    @abstractmethod
    def keys(self) -> Iterator[TrackId]:
        """Get all track IDs that have intersection points.

        Returns:
            Iterator over track IDs.
        """
        raise NotImplementedError

    @abstractmethod
    def get(self, track_id: TrackId) -> list[tuple[SectionId, IntersectionPoint]]:
        """Get intersection points for a specific track ID.

        Args:
            track_id: The track ID to get intersection points for.

        Returns:
            List of (section_id, intersection_point) tuples for the track.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def empty(self) -> bool:
        """Check if the dataset is empty.

        Returns:
            True if no intersection points exist, False otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def __len__(self) -> int:
        """Get the number of tracks with intersection points.

        Returns:
            Number of tracks that have intersection points.
        """
        raise NotImplementedError

    @abstractmethod
    def __contains__(self, track_id: TrackId) -> bool:
        """Check if a track ID has intersection points.

        Args:
            track_id: The track ID to check.

        Returns:
            True if the track has intersection points, False otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def create_events(
        self,
        offset: RelativeOffsetCoordinate,
        event_builder: EventBuilder = SectionEventBuilder(),
    ) -> EventDataset:
        raise NotImplementedError


class PythonIntersectionPointsDataset(IntersectionPointsDataset):
    """Dataset containing intersection points between tracks and sections."""

    def __init__(
        self,
        data: dict[TrackId, list[tuple[SectionId, IntersectionPoint]]],
        track_dataset: TrackDataset,
    ) -> None:
        """Initialize the intersection points dataset.

        Args:
            data: Dictionary mapping track IDs to lists of intersection points
                 with section IDs.
        """
        self._data = data
        self._track_dataset = track_dataset

    def items(
        self,
    ) -> Iterator[tuple[TrackId, list[tuple[SectionId, IntersectionPoint]]]]:
        """Iterate over track IDs and their intersection points.

        Returns:
            Iterator yielding (track_id, intersection_points) tuples.
        """
        return iter(self._data.items())

    def keys(self) -> Iterator[TrackId]:
        """Get all track IDs that have intersection points.

        Returns:
            Iterator over track IDs.
        """
        return iter(self._data.keys())

    def get(self, track_id: TrackId) -> list[tuple[SectionId, IntersectionPoint]]:
        """Get intersection points for a specific track ID.

        Args:
            track_id: The track ID to get intersection points for.

        Returns:
            List of (section_id, intersection_point) tuples for the track.
        """
        return self._data.get(track_id, [])

    @property
    def empty(self) -> bool:
        """Check if the dataset is empty.

        Returns:
            True if no intersection points exist, False otherwise.
        """
        return len(self._data) == 0

    def __len__(self) -> int:
        """Get the number of tracks with intersection points.

        Returns:
            Number of tracks that have intersection points.
        """
        return len(self._data)

    def __contains__(self, track_id: TrackId) -> bool:
        """Check if a track ID has intersection points.

        Args:
            track_id: The track ID to check.

        Returns:
            True if the track has intersection points, False otherwise.
        """
        return track_id in self._data

    def create_events(
        self,
        offset: RelativeOffsetCoordinate,
        event_builder: EventBuilder = SectionEventBuilder(),
    ) -> EventDataset:
        events: list[Event] = []
        for track_id, intersection_points in self.items():
            if not (track := self._track_dataset.get_for(track_id)):
                raise IntersectionError(
                    "Track not found. Unable to create intersection event "
                    f"for track {track_id}."
                )
            event_builder.add_road_user_type(track.classification)
            for section_id, intersection_point in intersection_points:
                event_builder.add_section_id(section_id)
                detection = track.get_detection(intersection_point.upper_index)
                previous_detection = track.get_detection(intersection_point.lower_index)
                current_coord = detection.get_coordinate(offset)
                prev_coord = previous_detection.get_coordinate(offset)
                direction_vector = calculate_direction_vector(
                    prev_coord.x,
                    prev_coord.y,
                    current_coord.x,
                    current_coord.y,
                )
                interpolated_occurrence = self._get_interpolated_occurrence(
                    previous=previous_detection.occurrence,
                    current=detection.occurrence,
                    relative_position=intersection_point.relative_position,
                )
                interpolated_event_coordinate = self._get_interpolated_event_coordinate(
                    previous=prev_coord,
                    current=current_coord,
                    relative_position=intersection_point.relative_position,
                )
                event_builder.add_event_type(EventType.SECTION_ENTER)
                event_builder.add_direction_vector(direction_vector)
                event_builder.add_event_coordinate(current_coord.x, current_coord.y)
                event_builder.add_interpolated_occurrence(interpolated_occurrence)
                event_builder.add_interpolated_event_coordinate(
                    interpolated_event_coordinate.x, interpolated_event_coordinate.y
                )
                events.append(event_builder.create_event(detection))

        return PythonEventDataset(events)

    def _get_interpolated_occurrence(
        self, previous: datetime, current: datetime, relative_position: float
    ) -> datetime:
        return previous + (current - previous) * relative_position

    def _get_interpolated_event_coordinate(
        self, previous: Coordinate, current: Coordinate, relative_position: float
    ) -> Coordinate:
        interpolated_x = previous.x + relative_position * (current.x - previous.x)
        interpolated_y = previous.y + relative_position * (current.y - previous.y)
        return Coordinate(interpolated_x, interpolated_y)


TRACK_GEOMETRY_FACTORY = Callable[
    [TrackDataset, RelativeOffsetCoordinate], TrackGeometryDataset
]


class IntersectionError(Exception):
    pass
