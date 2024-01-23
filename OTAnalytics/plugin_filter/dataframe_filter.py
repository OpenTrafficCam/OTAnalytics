from datetime import datetime
from typing import Iterable, Optional

from pandas import DataFrame, Series

from OTAnalytics.domain import track
from OTAnalytics.domain.filter import Conjunction, Filter, FilterBuilder, Predicate


class DataFrameConjunction(Conjunction[DataFrame, DataFrame]):
    """Represents the conjunction of two DataFrame predicates.

    Args:
        first_predicate (Predicate[DataFrame, DataFrame]): first predicate to
            conjunct with
        second_predicate (Predicate[DataFrame, DataFrame]): second predicate to
            conjunct with
    """

    def __init__(
        self,
        first_predicate: Predicate[DataFrame, DataFrame],
        second_predicate: Predicate[DataFrame, DataFrame],
    ) -> None:
        super().__init__(first_predicate, second_predicate)

    def test(self, to_test: DataFrame) -> DataFrame:
        return self._second_predicate.test(self._first_predicate.test(to_test))

    def conjunct_with(
        self, other: Predicate[DataFrame, DataFrame]
    ) -> Predicate[DataFrame, DataFrame]:
        return DataFrameConjunction(self, other)


class DataFramePredicate(Predicate[DataFrame, DataFrame]):
    """Checks DataFrame entries against predicate.

    Entries that do not fulfill predicate are filtered out.
    """

    def conjunct_with(
        self, other: Predicate[DataFrame, DataFrame]
    ) -> Predicate[DataFrame, DataFrame]:
        return DataFrameConjunction(self, other)


class DataFrameFilter(Filter[DataFrame, DataFrame]):
    def __init__(self, predicate: Predicate[DataFrame, DataFrame]) -> None:
        """A `DataFrame` filter.

        Args:
            predicate (Predicate[DataFrame, DataFrame]): the predicate to test
                the DataFrame against
        """
        self._predicate = predicate

    def apply(self, data: Iterable[DataFrame]) -> Iterable[DataFrame]:
        return [self._predicate.test(df) for df in data]


class NoOpDataFrameFilter(Filter[DataFrame, DataFrame]):
    """Returns the DataFrame as is without any filtering."""

    def apply(self, iterable: Iterable[DataFrame]) -> Iterable[DataFrame]:
        return iterable


INDEX_LEVEL_OCCURRENCE = 1


class DataFrameStartsAtOrAfterDate(DataFramePredicate):
    """Checks if the DataFrame rows start at or after date.

    Args:
        column_name (str): the DataFrame column name to apply the predicate to
        start_date (datetime): the start date to evaluate against (inclusive)
    """

    def __init__(
        self,
        column_name: str,
        start_date: datetime,
    ) -> None:
        self.column_name: str = column_name
        self._start_date = start_date

    def test(self, to_test: DataFrame) -> DataFrame:
        if not list(to_test.index.names) == [track.TRACK_ID, track.OCCURRENCE]:
            raise ValueError(
                f"{track.TRACK_ID} and {track.OCCURRENCE} "
                "must be index of DataFrame for filtering to work."
            )
        return to_test[
            to_test.index.get_level_values(INDEX_LEVEL_OCCURRENCE) >= self._start_date
        ]


class DataFrameEndsBeforeOrAtDate(DataFramePredicate):
    """Checks if the DataFrame rows ends before or at date.

    Args:
        column_name (str): the DataFrame column name to apply the predicate to
        end_date (datetime): the end date to evaluate against (inclusive)
    """

    def __init__(
        self,
        column_name: str,
        end_date: datetime,
    ) -> None:
        self.column_name: str = column_name
        self._end_date = end_date

    def test(self, to_test: DataFrame) -> DataFrame:
        if not list(to_test.index.names) == [track.TRACK_ID, track.OCCURRENCE]:
            raise ValueError(
                f"{track.TRACK_ID} and {track.OCCURRENCE} "
                "must be index of DataFrame for filtering to work."
            )
        return to_test[
            to_test.index.get_level_values(INDEX_LEVEL_OCCURRENCE) <= self._end_date
        ]


class DataFrameHasClassifications(DataFramePredicate):
    """Checks if the DataFrame rows have classifications.

    Args:
        column_name (str): the DataFrame column name to apply the predicate to
        classifications (list[str]): the classifications
    """

    def __init__(
        self,
        column_name: str,
        classifications: set[str],
    ) -> None:
        self._column_name = column_name
        self._classifications = classifications

    def test(self, to_test: DataFrame) -> DataFrame:
        return to_test[to_test[self._column_name].isin(self._classifications)]


class DataFrameFilterBuilder(FilterBuilder[DataFrame, DataFrame]):
    """A builder used to build a `DataFrameFilter`."""

    def __init__(self) -> None:
        super().__init__()
        self._complex_predicate: Optional[Predicate[DataFrame, DataFrame]] = None
        self._classification_column: Optional[str] = None
        self._occurrence_column: Optional[str] = None

    def add_has_classifications_predicate(self, classifications: set[str]) -> None:
        if self._classification_column is None:
            return

        self._extend_complex_predicate(
            DataFrameHasClassifications(self._classification_column, classifications)
        )

    def add_starts_at_or_after_date_predicate(self, start_date: datetime) -> None:
        if self._occurrence_column is None:
            return

        self._extend_complex_predicate(
            DataFrameStartsAtOrAfterDate(self._occurrence_column, start_date)
        )

    def add_ends_before_or_at_date_predicate(self, end_date: datetime) -> None:
        if self._occurrence_column is None:
            return

        self._extend_complex_predicate(
            DataFrameEndsBeforeOrAtDate(self._occurrence_column, end_date)
        )

    def set_classification_column(self, classification_name: str) -> None:
        self._classification_column = classification_name

    def set_occurrence_column(self, occurrence_column: str) -> None:
        self._occurrence_column = occurrence_column

    def build(self) -> None:
        if self._complex_predicate is None:
            self._result = NoOpDataFrameFilter()
        else:
            self._result = DataFrameFilter(self._complex_predicate)

    def _reset(self) -> None:
        self._complex_predicate = None
        self._occurrence_column = None
        self._classification_column = None
        self._result = None

    def _extend_complex_predicate(
        self, predicate: Predicate[DataFrame, Series]
    ) -> None:
        if self._complex_predicate:
            self._complex_predicate = self._complex_predicate.conjunct_with(predicate)
        else:
            self._complex_predicate = predicate
