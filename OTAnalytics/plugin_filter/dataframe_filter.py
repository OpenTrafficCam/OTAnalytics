from datetime import datetime
from typing import Iterable, Optional

from pandas import DataFrame, Series

from OTAnalytics.domain.filter import (
    Conjunction,
    Filter,
    FilterBuilder,
    FilterBuildError,
    Predicate,
)


class DataFrameConjunction(Conjunction[DataFrame, Series]):
    """Represents the conjunction of two DataFrame predicates.

    Args:
        first_predicate (Predicate[DataFrame, Series]): first predicate to
            conjunct with
        second_predicate (Predicate[DataFrame, Series]): second predicate to
            conjunct with
    """

    def __init__(
        self,
        first_predicate: Predicate[DataFrame, Series],
        second_predicate: Predicate[DataFrame, Series],
    ) -> None:
        super().__init__(first_predicate, second_predicate)

    def test(self, to_test: DataFrame) -> Series:
        return (self._first_predicate.test(to_test)) & (
            self._second_predicate.test(to_test)
        )

    def conjunct_with(
        self, other: Predicate[DataFrame, Series]
    ) -> Predicate[DataFrame, Series]:
        return DataFrameConjunction(self, other)


class DataFramePredicate(Predicate[DataFrame, Series]):
    def conjunct_with(
        self, other: Predicate[DataFrame, Series]
    ) -> Predicate[DataFrame, Series]:
        return DataFrameConjunction(self, other)


class DataFrameFilter(Filter[DataFrame, Series]):
    def __init__(self, predicate: Predicate[DataFrame, Series]) -> None:
        """A `DataFrame` filter.

        Args:
            predicate (Predicate[DataFrame, Series]): the predicate to test
                the DataFrame against
        """
        self._predicate = predicate

    def apply(self, data: Iterable[DataFrame]) -> Iterable[DataFrame]:
        return [datum[self._predicate.test(datum)] for datum in data]


class NoOpDataFrameFilter(Filter[DataFrame, Series]):
    """Returns the DataFrame as is without any filtering."""

    def apply(self, iterable: Iterable[DataFrame]) -> Iterable[DataFrame]:
        return iterable


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

    def test(self, to_test: DataFrame) -> Series:
        return to_test[self.column_name] >= self._start_date


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

    def test(self, to_test: DataFrame) -> Series:
        return to_test[self.column_name] <= self._end_date


class DataFrameHasClassifications(DataFramePredicate):
    """Checks if the DataFrame rows have classifications.

    Args:
        column_name (str): the DataFrame column name to apply the predicate to
        classifications (list[str]): the classifications
    """

    def __init__(
        self,
        column_name: str,
        classifications: list[str],
    ) -> None:
        self._column_name = column_name
        self._classifications = classifications

    def test(self, to_test: DataFrame) -> Series:
        return to_test[self._column_name].isin(self._classifications)


class DataFrameFilterBuilder(FilterBuilder):
    """A builder used to build a `DataFrameFilter`."""

    def __init__(self) -> None:
        self._complex_predicate: Optional[Predicate[DataFrame, Series]] = None
        self._classification_column: Optional[str] = None
        self._occurrence_column: Optional[str] = None

    def build(self) -> Filter[DataFrame, Series]:
        if self._complex_predicate is None:
            return NoOpDataFrameFilter()
        return DataFrameFilter(self._complex_predicate)

    def add_has_classifications_predicate(self, classifications: list[str]) -> None:
        if self._classification_column is None:
            raise FilterBuildError(
                f"Unable to build '{DataFrameHasClassifications.__name__}' predicate. "
                "Builder property 'classification_column' is not set."
            )

        self._extend_complex_predicate(
            DataFrameHasClassifications(self._classification_column, classifications)
        )

    def add_starts_at_or_after_date_predicate(self, start_date: datetime) -> None:
        if self._occurrence_column is None:
            raise FilterBuildError(
                f"Unable to build '{DataFrameStartsAtOrAfterDate.__name__}' predicate. "
                "Builder property 'occurrence_column' is not set."
            )

        self._extend_complex_predicate(
            DataFrameStartsAtOrAfterDate(self._occurrence_column, start_date)
        )

    def add_ends_before_or_at_date_predicate(self, end_date: datetime) -> None:
        if self._occurrence_column is None:
            raise FilterBuildError(
                f"Unable to build '{DataFrameEndsBeforeOrAtDate.__name__}' predicate. "
                "Builder property 'occurrence_column' is not set."
            )

        self._extend_complex_predicate(
            DataFrameEndsBeforeOrAtDate(self._occurrence_column, end_date)
        )

    def set_classification_column(self, classification_name: str) -> None:
        self._classification_column = classification_name

    def set_occurrence_column(self, occurrence_column: str) -> None:
        self._occurrence_column = occurrence_column

    def _extend_complex_predicate(
        self, predicate: Predicate[DataFrame, Series]
    ) -> None:
        if self._complex_predicate:
            self._complex_predicate = self._complex_predicate.conjunct_with(predicate)
        else:
            self._complex_predicate = predicate
