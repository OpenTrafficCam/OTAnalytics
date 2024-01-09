from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, Iterable, Iterator, Optional, Sequence

from OTAnalytics.domain.event import Event
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate
from OTAnalytics.domain.section import Section, SectionId
from OTAnalytics.domain.track import Track, TrackId


@dataclass
class IntersectionPoint:
    index: int


class TrackDataset(ABC):
    def __iter__(self) -> Iterator[Track]:
        yield from self.as_list()

    @abstractmethod
    def add_all(self, other: Iterable[Track]) -> "TrackDataset":
        raise NotImplementedError

    @abstractmethod
    def get_all_ids(self) -> Iterable[TrackId]:
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
    def __len__(self) -> int:
        """Number of tracks in the dataset."""
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
    def apply_to_first_segments(self, consumer: Callable[[Event], None]) -> None:
        raise NotImplementedError

    @abstractmethod
    def apply_to_last_segments(self, consumer: Callable[[Event], None]) -> None:
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
    def remove(self, ids: Iterable[TrackId]) -> "TrackGeometryDataset":
        """Remove track geometries with given ids from dataset.

        Args:
            ids (Iterable[TrackId]): the track geometries to remove.

        Returns:
            TrackGeometryDataset: the dataset with tracks removed.
        """
        raise NotImplementedError

    @abstractmethod
    def get_for(self, track_ids: Iterable[str]) -> "TrackGeometryDataset":
        """Get geometries for given track ids if they exist.

        Ids that do not exist will not be included in the dataset.

        Args:
            track_ids (Iterable[str]): the track ids.

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


TRACK_GEOMETRY_FACTORY = Callable[
    [TrackDataset, RelativeOffsetCoordinate], TrackGeometryDataset
]
