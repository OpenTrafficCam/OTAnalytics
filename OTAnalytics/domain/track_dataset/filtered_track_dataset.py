from abc import abstractmethod
from datetime import datetime
from typing import Iterator, Optional

from OTAnalytics.domain.geometry import RelativeOffsetCoordinate
from OTAnalytics.domain.section import Section, SectionId
from OTAnalytics.domain.track import Track, TrackId
from OTAnalytics.domain.track_dataset.track_dataset import (
    IntersectionPoint,
    TrackDataset,
    TrackSegmentDataset,
)


class FilteredTrackDataset(TrackDataset):
    @abstractmethod
    def _filter(self) -> TrackDataset:
        raise NotImplementedError

    @property
    def track_ids(self) -> frozenset[TrackId]:
        return self._filter().track_ids

    @property
    def first_occurrence(self) -> datetime | None:
        return self._filter().first_occurrence

    @property
    def last_occurrence(self) -> datetime | None:
        return self._filter().last_occurrence

    @property
    def classifications(self) -> frozenset[str]:
        return self._filter().classifications

    @property
    def empty(self) -> bool:
        return self._filter().empty

    def __iter__(self) -> Iterator[Track]:
        yield from self._filter()

    def __len__(self) -> int:
        return len(self._filter())

    def get_for(self, id: TrackId) -> Optional[Track]:
        return self._filter().get_for(id)

    def as_list(self) -> list[Track]:
        return self._filter().as_list()

    def intersecting_tracks(
        self, sections: list[Section], offset: RelativeOffsetCoordinate
    ) -> set[TrackId]:
        return self._filter().intersecting_tracks(sections, offset)

    def intersection_points(
        self, sections: list[Section], offset: RelativeOffsetCoordinate
    ) -> dict[TrackId, list[tuple[SectionId, IntersectionPoint]]]:
        return self._filter().intersection_points(sections, offset)

    def contained_by_sections(
        self, sections: list[Section], offset: RelativeOffsetCoordinate
    ) -> dict[TrackId, list[tuple[SectionId, list[bool]]]]:
        return self._filter().contained_by_sections(sections, offset)

    def filter_by_min_detection_length(self, length: int) -> TrackDataset:
        return self._filter().filter_by_min_detection_length(length)

    def get_first_segments(self) -> TrackSegmentDataset:
        return self._filter().get_first_segments()

    def get_last_segments(self) -> TrackSegmentDataset:
        return self._filter().get_last_segments()

    def get_max_confidences_for(self, track_ids: list[str]) -> dict[str, float]:
        return self._filter().get_max_confidences_for(track_ids)


class FilterByClassTrackDataset(FilteredTrackDataset):
    @property
    @abstractmethod
    def include_classes(self) -> frozenset[str]:
        raise NotImplementedError

    @property
    @abstractmethod
    def exclude_classes(self) -> frozenset[str]:
        raise NotImplementedError
