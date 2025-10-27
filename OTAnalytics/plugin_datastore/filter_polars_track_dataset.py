from abc import abstractmethod
from typing import Iterable, Sequence

import polars as pl

from OTAnalytics.application.logger import logger
from OTAnalytics.domain import track
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate
from OTAnalytics.domain.section import Section
from OTAnalytics.domain.track import Track, TrackId
from OTAnalytics.domain.track_dataset.filtered_track_dataset import (
    FilterByClassTrackDataset,
    FilteredTrackDataset,
)
from OTAnalytics.domain.track_dataset.track_dataset import TrackIdSet
from OTAnalytics.plugin_datastore.polars_track_store import (
    POLARS_TRACK_GEOMETRY_FACTORY,
    PolarsDataFrameProvider,
    PolarsTrackClassificationCalculator,
    PolarsTrackDataset,
    get_rows_by_track_ids,
)
from OTAnalytics.plugin_datastore.track_store import MINIMUM_DETECTIONS, RANK


class FilteredPolarsTrackDataset(
    FilteredTrackDataset, PolarsTrackDataset, PolarsDataFrameProvider
):

    @property
    def track_geometry_factory(self) -> POLARS_TRACK_GEOMETRY_FACTORY:
        return self._other.track_geometry_factory

    @property
    def calculator(self) -> PolarsTrackClassificationCalculator:
        return self._other.calculator

    def __init__(self, other: PolarsTrackDataset) -> None:
        self._other = other

    def add_all(self, other: Iterable[Track]) -> PolarsTrackDataset:
        return self.wrap(self._other.add_all(other))

    def remove(self, track_id: TrackId) -> PolarsTrackDataset:
        return self.wrap(self._other.remove(track_id))

    def remove_multiple(self, track_ids: TrackIdSet) -> PolarsTrackDataset:
        return self.wrap(self._other.remove_multiple(track_ids))

    def clear(self) -> PolarsTrackDataset:
        return self.wrap(self._other.clear())

    def split(self, chunks: int) -> Sequence[PolarsTrackDataset]:
        return [self.wrap(dataset) for dataset in self._other.split(chunks)]

    def calculate_geometries_for(
        self, offsets: Iterable[RelativeOffsetCoordinate]
    ) -> None:
        self._other.calculate_geometries_for(offsets)

    def cut_with_section(
        self, section: Section, offset: RelativeOffsetCoordinate
    ) -> tuple[PolarsTrackDataset, TrackIdSet]:
        dataset, original_track_ids = self._other.cut_with_section(section, offset)
        return self.wrap(dataset), original_track_ids

    def ids_inside(self, sections: list[Section]) -> TrackIdSet:
        return self._filter().ids_inside(sections)

    @abstractmethod
    def _filter(self) -> PolarsTrackDataset:
        raise NotImplementedError

    @abstractmethod
    def wrap(self, other: PolarsTrackDataset) -> PolarsTrackDataset:
        raise NotImplementedError

    def get_data(self) -> pl.DataFrame:
        return self._filter().get_data()

    def revert_cuts_for(
        self, original_track_ids: TrackIdSet
    ) -> tuple[PolarsTrackDataset, TrackIdSet, TrackIdSet]:
        reverted_dataset, reverted_ids, cut_ids = self._other.revert_cuts_for(
            original_track_ids
        )
        return self.wrap(reverted_dataset), reverted_ids, cut_ids

    def remove_by_original_ids(
        self, original_ids: TrackIdSet
    ) -> tuple["PolarsTrackDataset", TrackIdSet]:
        updated_dataset, removed_ids = self._other.remove_by_original_ids(original_ids)
        return self.wrap(updated_dataset), removed_ids


class FilterByClassPolarsTrackDataset(
    FilteredPolarsTrackDataset, FilterByClassTrackDataset
):
    @property
    def include_classes(self) -> frozenset[str]:
        return self._include_classes

    @property
    def exclude_classes(self) -> frozenset[str]:
        return self._exclude_classes

    def __init__(
        self,
        other: PolarsTrackDataset,
        include_classes: frozenset[str],
        exclude_classes: frozenset[str],
    ) -> None:
        super().__init__(other)
        self._include_classes = include_classes
        self._exclude_classes = exclude_classes
        self._cache: PolarsTrackDataset | None = None

    def _filter(self) -> PolarsTrackDataset:
        """Filter TrackDataset by classifications.

        IMPORTANT: Classifications contained in the include_classes will not be
        removed even if they appear in the set of exclude_classes.
        Furthermore, the whitelist will not be applied if empty.

        Returns:
            TrackDataset: the filtered dataset.
        """
        if not self.include_classes and not self._exclude_classes:
            return self._other

        if self._cache is not None:
            return self._cache

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
        self._cache = filtered_dataset
        return filtered_dataset

    def _get_dataset_with_classes(self, classes: list[str]) -> PolarsTrackDataset:
        if self._other.empty:
            return self._other
        dataset = self._other.get_data()
        mask = dataset[track.TRACK_CLASSIFICATION].is_in(classes)
        filtered_df = dataset.filter(mask)
        # The polars DataFrame filtering approach ensures data consistency.
        # When filtering by track classes, we invalidate the entire geometry cache
        # rather than attempting selective removal. This approach is acceptable
        # because track removal only occurs when cutting tracks, which is a rare use
        # case.

        return PolarsTrackDataset(
            track_geometry_factory=self._other.track_geometry_factory,
            dataset=filtered_df,
            geometry_datasets=None,
            calculator=self._other.calculator,
        )

    def wrap(self, other: PolarsTrackDataset) -> PolarsTrackDataset:
        return FilterByClassPolarsTrackDataset(
            other, self.include_classes, self.exclude_classes
        )


class FilterByIdPolarsTrackDataset(FilteredPolarsTrackDataset):
    """
    Represents a dataset that filters tracks by specific track IDs.

    This class provides functionality to filter a Polars-based track dataset by a
    list of track IDs. It utilizes caching to optimize repeated filtering operations,
    manages dataset consistency, and ensures efficient geometry cache invalidation
    for cases such as track removal.
    """

    def __init__(self, other: PolarsTrackDataset, track_ids: list[str]) -> None:
        super().__init__(other)
        self._included_track_ids = track_ids
        self._cache: PolarsTrackDataset | None = None

    def _filter(self) -> PolarsTrackDataset:
        """
        Filters the track dataset based on included track IDs.

        This method applies a filter on a dataset to include only the tracks
        specified in `_included_track_ids`. If there are no specified track IDs,
        it returns the original dataset (`_other`). It employs caching to store the
        filtered dataset for future use.

        Returns:
            TrackDataset: The filtered dataset containing only the specified track IDs.
                If no track IDs are provided, the original dataset is returned.
        """
        if not self._included_track_ids:
            return self._other

        if self._cache is not None:
            return self._cache

        if self._included_track_ids:
            logger().info(
                "Apply 'track-ids' filter to filter tracks: "
                f"{self._included_track_ids}"
            )
            filtered_dataset = self._get_dataset_with(
                track_ids=self._included_track_ids
            )
        else:
            return self._other
        self._cache = filtered_dataset
        return filtered_dataset

    def _get_dataset_with(self, track_ids: list[str]) -> PolarsTrackDataset:
        if self._other.empty:
            return self._other
        dataset = self._other.get_data()
        filtered_df = get_rows_by_track_ids(dataset, track_ids)
        # The polars DataFrame filtering approach ensures data consistency.
        # When filtering by track IDs, we invalidate the entire geometry cache
        # rather than attempting selective removal. This approach is acceptable
        # because track removal only occurs when cutting tracks, which is a rare use
        # case.

        return PolarsTrackDataset(
            track_geometry_factory=self._other.track_geometry_factory,
            dataset=filtered_df,
            geometry_datasets=None,
            calculator=self._other.calculator,
        )

    def wrap(self, other: PolarsTrackDataset) -> PolarsTrackDataset:
        return FilterByIdPolarsTrackDataset(other, self._included_track_ids)


class FilterLastNDetectionsPolarsTrackDataset(FilteredPolarsTrackDataset):
    def __init__(self, other: PolarsTrackDataset, n: int) -> None:
        super().__init__(other)
        self._n = n
        self._cache: PolarsTrackDataset | None = None

    def _filter(self) -> PolarsTrackDataset:
        """
        Filters the track dataset based on included track IDs.

        This method applies a filter on a dataset to include only the tracks
        specified in `_included_track_ids`. If there are no specified track IDs,
        it returns the original dataset (`_other`). It employs caching to store the
        filtered dataset for future use.

        Returns:
            TrackDataset: The filtered dataset containing only the specified track IDs.
                If no track IDs are provided, the original dataset is returned.
        """
        if self._cache is not None:
            return self._cache

        logger().info(
            f"Limit number of detections per track to last {self._n} of them."
        )
        filtered_dataset = self._get_filtered_dataset()
        self._cache = filtered_dataset
        return filtered_dataset

    def _get_filtered_dataset(self) -> PolarsTrackDataset:
        if self._other.empty:
            return self._other
        dataset = self._other.get_data()
        filtered_df = get_exactly_two_latest_occurrences_per_id(dataset, self._n)
        # The polars DataFrame filtering approach ensures data consistency.
        # When filtering by number of detections, we invalidate the entire geometry
        # cache rather than attempting selective removal. This approach is acceptable
        # because track removal only occurs when cutting tracks, which is a rare use
        # case.

        return PolarsTrackDataset(
            track_geometry_factory=self._other.track_geometry_factory,
            dataset=filtered_df,
            geometry_datasets=None,
            calculator=self._other.calculator,
        )

    def wrap(self, other: PolarsTrackDataset) -> PolarsTrackDataset:
        return FilterLastNDetectionsPolarsTrackDataset(other, self._n)


def get_latest_occurrences(dataframe: pl.DataFrame, last_n: int) -> pl.DataFrame:
    result = dataframe.with_columns(
        [
            pl.col(track.OCCURRENCE)
            .rank("ordinal", descending=True)
            .over(track.TRACK_ID)
            .alias(RANK)
        ]
    )
    return result.filter(pl.col(RANK) <= last_n).drop(RANK)


def get_exactly_two_latest_occurrences_per_id(
    dataframe: pl.DataFrame, last_n: int
) -> pl.DataFrame:
    counts = dataframe.group_by(track.TRACK_ID).agg(pl.len().alias("count"))
    valid_ids = (
        counts.filter(pl.col("count") >= MINIMUM_DETECTIONS)
        .select(track.TRACK_ID)
        .to_series()
    )
    filtered_df = get_rows_by_track_ids(
        dataframe=dataframe, track_ids=valid_ids.to_list()
    )
    return get_latest_occurrences(filtered_df, last_n=last_n)
