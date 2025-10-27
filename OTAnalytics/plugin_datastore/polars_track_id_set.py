from typing import Any, Iterable, Iterator

import polars as pl

from OTAnalytics.domain.track import TrackId, unpack
from OTAnalytics.domain.track_dataset.track_dataset import TrackIdSet, TrackIdSetFactory


class PolarsTrackIdSet(TrackIdSet):
    """
    Polars-based implementation of TrackIdSet using a Series for optimal performance.
    """

    def __init__(
        self, track_ids: Iterable[TrackId] | Iterable[str] | pl.Series | None = None
    ):
        if track_ids is None:
            self._series = pl.Series([], dtype=pl.String)
        elif isinstance(track_ids, pl.Series):
            self._series = track_ids.unique().sort()
        else:
            # Convert TrackId objects to strings
            id_strings = [unpack(track_id) for track_id in track_ids]
            self._series = pl.Series(id_strings, dtype=pl.String).unique().sort()

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, PolarsTrackIdSet):
            return self._series.equals(other._series)
        elif isinstance(other, TrackIdSet):
            return self.__eq__(PolarsTrackIdSet(other))
        return False

    def __iter__(self) -> Iterator[TrackId]:
        for id_str in self._series:
            yield TrackId(id_str)

    def __len__(self) -> int:
        return len(self._series)

    def intersection(self, other: "TrackIdSet") -> "TrackIdSet":
        if isinstance(other, PolarsTrackIdSet):
            # Efficient intersection using Polars operations
            intersected_series = self._series.filter(
                self._series.is_in(other._series)
            ).sort()
            return PolarsTrackIdSet(intersected_series)
        else:
            # Convert other to set of strings for intersection
            other_strings = {unpack(track_id) for track_id in other}
            intersected_series = self._series.filter(
                self._series.is_in(list(other_strings))
            ).sort()
            return PolarsTrackIdSet(intersected_series)

    def union(self, other: "TrackIdSet") -> "TrackIdSet":
        if isinstance(other, PolarsTrackIdSet):
            # Efficient union using Polars operations
            combined_series = pl.concat([self._series, other._series]).unique().sort()
            return PolarsTrackIdSet(combined_series)
        else:
            # Convert other to strings and combine
            other_strings = {unpack(track_id) for track_id in other}
            other_series = pl.Series(other_strings, dtype=pl.String)
            combined_series = pl.concat([self._series, other_series]).unique().sort()
            return PolarsTrackIdSet(combined_series)

    def difference(self, other: "TrackIdSet") -> "TrackIdSet":
        if isinstance(other, PolarsTrackIdSet):
            # Efficient difference using Polars operations
            difference_series = self._series.filter(
                ~self._series.is_in(other._series)
            ).sort()
            return PolarsTrackIdSet(difference_series)
        else:
            # Convert other to set of strings for difference
            other_strings = {unpack(track_id) for track_id in other}
            difference_series = self._series.filter(
                ~self._series.is_in(list(other_strings))
            ).sort()
            return PolarsTrackIdSet(difference_series)


class PolarsTrackIdSetFactory(TrackIdSetFactory):

    def create(self, track_ids: Iterable[TrackId] | Iterable[str]) -> TrackIdSet:
        return PolarsTrackIdSet(track_ids)
