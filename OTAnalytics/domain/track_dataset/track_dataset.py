from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Iterable, Iterator, Optional, Sequence

from OTAnalytics.domain.geometry import RelativeOffsetCoordinate
from OTAnalytics.domain.section import Section, SectionId
from OTAnalytics.domain.track import Track, TrackId

START_X: str = "start_x"
START_Y: str = "start_y"
START_OCCURRENCE: str = "start_occurrence"
START_FRAME: str = "start_frame"
START_VIDEO_NAME: str = "start_video_name"
END_X: str = "end_x"
END_Y: str = "end_y"
END_OCCURRENCE: str = "end_occurrence"
END_FRAME: str = "end_frame"
END_VIDEO_NAME: str = "end_video_name"


class TrackDoesNotExistError(Exception):
    pass


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


class TrackDataset(ABC):
    @property
    @abstractmethod
    def track_ids(self) -> frozenset[TrackId]:
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
    def remove_multiple(self, track_ids: set[TrackId]) -> "TrackDataset":
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
    ) -> set[TrackId]:
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
    ) -> dict[TrackId, list[tuple[SectionId, IntersectionPoint]]]:
        """
        Return the intersection points resulting from the tracks and the
        given sections.

        Args:
            sections (list[Section]): the sections to intersect with.
            offset (RelativeOffsetCoordinate): the offset to be applied to the tracks.

        Returns:
            dict[TrackId, list[tuple[SectionId]]]: the intersection points.
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
    ) -> tuple["TrackDataset", set[TrackId]]:
        """Use section to cut track with TrackDataset.

        Args:
            section (Section): the section to cut the TrackDataset with.
            offset (RelativeOffsetCoordinate): the offset to be applied to the tracks.

        Returns:
            tuple[TrackDataset, set[TrackId]]: the dataset containing the cut tracks
                and the original track ids that have been cut.
        """
        raise NotImplementedError

    @abstractmethod
    def get_max_confidences_for(self, track_ids: list[str]) -> dict[str, float]:
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
        self, original_track_ids: frozenset[TrackId]
    ) -> tuple["TrackDataset", frozenset[TrackId], frozenset[TrackId]]:
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
        self, original_ids: frozenset[TrackId]
    ) -> tuple["TrackDataset", frozenset[TrackId]]:
        """
        Remove tracks with the specified original IDs and return a new dataset.

        Args:
            original_ids (frozenset[TrackId]): The original IDs of tracks to remove

        Returns:
            tuple[TrackDataset, frozenset[TrackId]]:
                1. A new dataset without the specified tracks
                2. The set of actual track IDs that were removed during the removal
                    process.
        """
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
    def intersecting_tracks(self, sections: list[Section]) -> set[TrackId]:
        """Return a set of tracks intersecting a set of sections.

        Args:
            sections (list[Section]): the list of sections to intersect.

        Returns:
            set[TrackId]: the track ids intersecting the given sections.
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


TRACK_GEOMETRY_FACTORY = Callable[
    [TrackDataset, RelativeOffsetCoordinate], TrackGeometryDataset
]
