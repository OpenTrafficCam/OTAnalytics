from abc import abstractmethod
from typing import Iterable, Sequence

from pandas import DataFrame

from OTAnalytics.application.logger import logger
from OTAnalytics.domain import track
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate
from OTAnalytics.domain.section import Section
from OTAnalytics.domain.track import Track, TrackId
from OTAnalytics.domain.track_dataset.filtered_track_dataset import (
    FilterByClassTrackDataset,
    FilteredTrackDataset,
)
from OTAnalytics.domain.track_dataset.track_dataset import (
    TRACK_GEOMETRY_FACTORY,
    TrackIdSet,
)
from OTAnalytics.plugin_datastore.track_store import (
    LEVEL_TRACK_ID,
    MINIMUM_DETECTIONS,
    RANK,
    PandasDataFrameProvider,
    PandasTrackClassificationCalculator,
    PandasTrackDataset,
    get_rows_by_track_ids,
)


class FilteredPandasTrackDataset(
    FilteredTrackDataset, PandasTrackDataset, PandasDataFrameProvider
):

    @property
    def track_geometry_factory(self) -> TRACK_GEOMETRY_FACTORY:
        return self._other.track_geometry_factory

    @property
    def calculator(self) -> PandasTrackClassificationCalculator:
        return self._other.calculator

    def __init__(self, other: PandasTrackDataset) -> None:
        self._other = other

    def add_all(self, other: Iterable[Track]) -> PandasTrackDataset:
        return self.wrap(self._other.add_all(other))

    def remove(self, track_id: TrackId) -> PandasTrackDataset:
        return self.wrap(self._other.remove(track_id))

    def remove_multiple(self, track_ids: TrackIdSet) -> PandasTrackDataset:
        return self.wrap(self._other.remove_multiple(track_ids))

    def clear(self) -> PandasTrackDataset:
        return self.wrap(self._other.clear())

    def split(self, chunks: int) -> Sequence[PandasTrackDataset]:
        return [self.wrap(dataset) for dataset in self._other.split(chunks)]

    def calculate_geometries_for(
        self, offsets: Iterable[RelativeOffsetCoordinate]
    ) -> None:
        self._other.calculate_geometries_for(offsets)

    def cut_with_section(
        self, section: Section, offset: RelativeOffsetCoordinate
    ) -> tuple[PandasTrackDataset, TrackIdSet]:
        dataset, original_track_ids = self._other.cut_with_section(section, offset)
        return self.wrap(dataset), original_track_ids

    @abstractmethod
    def _filter(self) -> PandasTrackDataset:
        raise NotImplementedError

    @abstractmethod
    def wrap(self, other: PandasTrackDataset) -> PandasTrackDataset:
        raise NotImplementedError

    def get_data(self) -> DataFrame:
        return self._filter().get_data()

    def revert_cuts_for(
        self, original_track_ids: TrackIdSet
    ) -> tuple[PandasTrackDataset, TrackIdSet, TrackIdSet]:
        reverted_dataset, reverted_ids, cut_ids = self._other.revert_cuts_for(
            original_track_ids
        )
        return self.wrap(reverted_dataset), reverted_ids, cut_ids

    def remove_by_original_ids(
        self, original_ids: TrackIdSet
    ) -> tuple["PandasTrackDataset", TrackIdSet]:
        updated_dataset, removed_ids = self._other.remove_by_original_ids(original_ids)
        return self.wrap(updated_dataset), removed_ids


class FilterByClassPandasTrackDataset(
    FilteredPandasTrackDataset, FilterByClassTrackDataset
):
    @property
    def include_classes(self) -> frozenset[str]:
        return self._include_classes

    @property
    def exclude_classes(self) -> frozenset[str]:
        return self._exclude_classes

    def __init__(
        self,
        other: PandasTrackDataset,
        include_classes: frozenset[str],
        exclude_classes: frozenset[str],
    ) -> None:
        super().__init__(other)
        self._include_classes = include_classes
        self._exclude_classes = exclude_classes
        self._cache: PandasTrackDataset | None = None

    def _filter(self) -> PandasTrackDataset:
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

    def _get_dataset_with_classes(self, classes: list[str]) -> PandasTrackDataset:
        if self._other.empty:
            return self._other
        dataset = self._other.get_data()
        mask = dataset[track.TRACK_CLASSIFICATION].isin(classes)
        filtered_df = dataset[mask]
        # The pandas Index does not implement the Sequence interface, which causes
        # compatibility issues with the PandasTrackDataset._remove_from_geometry method
        # when trying to remove geometries for tracks that have been deleted.
        # To address this, we invalidate the entire geometry cache rather than
        # attempting selective removal.
        # This approach is acceptable because track removal only occurs when
        # cutting tracks, which is a rare use case.

        return PandasTrackDataset(
            track_geometry_factory=self._other.track_geometry_factory,
            dataset=filtered_df,
            geometry_datasets=None,
            calculator=self._other.calculator,
        )

    def wrap(self, other: PandasTrackDataset) -> PandasTrackDataset:
        return FilterByClassPandasTrackDataset(
            other, self.include_classes, self.exclude_classes
        )


class FilterByIdPandasTrackDataset(FilteredPandasTrackDataset):
    """
    Represents a dataset that filters tracks by specific track IDs.

    This class provides functionality to filter a Pandas-based track dataset by a
    list of track IDs. It utilizes caching to optimize repeated filtering operations,
    manages dataset consistency, and ensures efficient geometry cache invalidation
    for cases such as track removal.
    """

    def __init__(self, other: PandasTrackDataset, track_ids: list[str]) -> None:
        super().__init__(other)
        self._included_track_ids = track_ids
        self._cache: PandasTrackDataset | None = None

    def _filter(self) -> PandasTrackDataset:
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

    def _get_dataset_with(self, track_ids: list[str]) -> PandasTrackDataset:
        if self._other.empty:
            return self._other
        dataset = self._other.get_data()
        filtered_df = get_rows_by_track_ids(dataset, track_ids)
        # The pandas Index does not implement the Sequence interface, which causes
        # compatibility issues with the PandasTrackDataset._remove_from_geometry method
        # when trying to remove geometries for tracks that have been deleted.
        # To address this, we invalidate the entire geometry cache rather than
        # attempting selective removal.
        # This approach is acceptable because track removal only occurs when
        # cutting tracks, which is a rare use case.

        return PandasTrackDataset(
            track_geometry_factory=self._other.track_geometry_factory,
            dataset=filtered_df,
            geometry_datasets=None,
            calculator=self._other.calculator,
        )

    def wrap(self, other: PandasTrackDataset) -> PandasTrackDataset:
        return FilterByIdPandasTrackDataset(other, self._included_track_ids)


class FilterLastNDetectionsPandasTrackDataset(FilteredPandasTrackDataset):
    def __init__(self, other: PandasTrackDataset, n: int) -> None:
        super().__init__(other)
        self._n = n
        self._cache: PandasTrackDataset | None = None

    def _filter(self) -> PandasTrackDataset:
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

    def _get_filtered_dataset(self) -> PandasTrackDataset:
        if self._other.empty:
            return self._other
        dataset = self._other.get_data()
        filtered_df = get_exactly_two_latest_occurrences_per_id(dataset, self._n)
        # The pandas Index does not implement the Sequence interface, which causes
        # compatibility issues with the PandasTrackDataset._remove_from_geometry method
        # when trying to remove geometries for tracks that have been deleted.
        # To address this, we invalidate the entire geometry cache rather than
        # attempting selective removal.
        # This approach is acceptable because track removal only occurs when
        # cutting tracks, which is a rare use case.

        return PandasTrackDataset(
            track_geometry_factory=self._other.track_geometry_factory,
            dataset=filtered_df,
            geometry_datasets=None,
            calculator=self._other.calculator,
        )

    def wrap(self, other: PandasTrackDataset) -> PandasTrackDataset:
        return FilterLastNDetectionsPandasTrackDataset(other, self._n)


def get_latest_occurrences(dataframe: DataFrame, last_n: int) -> DataFrame:
    index_names = dataframe.index.names
    result = dataframe.reset_index()
    result.loc[:, RANK] = result.groupby(track.TRACK_ID)[track.OCCURRENCE].rank(
        method="first", ascending=False
    )
    result = result[result[RANK] <= last_n].drop(RANK, axis=1).reset_index(drop=True)
    return result.set_index(index_names)


def get_exactly_two_latest_occurrences_per_id(
    dataframe: DataFrame, last_n: int
) -> DataFrame:
    counts = dataframe.index.get_level_values(LEVEL_TRACK_ID).value_counts()
    valid_ids = counts[counts >= MINIMUM_DETECTIONS].index
    filtered_df = get_rows_by_track_ids(dataframe=dataframe, track_ids=valid_ids)
    return get_latest_occurrences(filtered_df, last_n=last_n)
