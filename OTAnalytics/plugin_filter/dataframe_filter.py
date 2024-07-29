from datetime import datetime
from typing import Iterable, Optional

from pandas import DataFrame, Series

from OTAnalytics.application.plotting import GetCurrentFrame
from OTAnalytics.application.use_cases.video_repository import GetVideos
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
        if track.OCCURRENCE not in to_test.index.names:
            raise ValueError(
                f"{track.OCCURRENCE} "
                "must be index of DataFrame for filtering to work."
            )
        return to_test[
            to_test.index.get_level_values(track.OCCURRENCE) >= self._start_date
        ]


class DataFrameStartsAtOrAfterFrame(DataFramePredicate):
    """Checks if the DataFrame rows start at or after frame.

    Args:
        column_name (str): the DataFrame column name to apply the predicate to
        frame (int): the frame number to evaluate against (inclusive)
    """

    def __init__(
        self,
        column_name: str,
        frame: int,
        video_of_start_date: str,
        videos_after: list[str],
    ) -> None:
        self.column_name: str = column_name
        self._frame = frame
        self._video_of_start_date = video_of_start_date
        self._videos_after = videos_after

    def test(self, to_test: DataFrame) -> DataFrame:
        video_start_date_filter = (to_test[track.FRAME] >= self._frame) & (
            to_test[track.VIDEO_NAME] == self._video_of_start_date
        )
        videos_after_date_filter = to_test[track.VIDEO_NAME].isin(self._videos_after)
        date_filter = video_start_date_filter | videos_after_date_filter
        return to_test[date_filter]


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
        if track.OCCURRENCE not in to_test.index.names:
            raise ValueError(
                f"{track.OCCURRENCE} "
                "must be index of DataFrame for filtering to work."
            )
        return to_test[
            to_test.index.get_level_values(track.OCCURRENCE) <= self._end_date
        ]


class DataFrameEndsBeforeOrAtFrame(DataFramePredicate):
    """Checks if the DataFrame rows ends before or at frame.

    Args:
        column_name (str): the DataFrame column name to apply the predicate to
        frame (int): the frame number to evaluate against (inclusive)
    """

    def __init__(
        self,
        column_name: str,
        frame: int,
        video_of_end_date: str,
        videos_before: list[str],
    ) -> None:
        self.column_name: str = column_name
        self._frame = frame
        self._video_of_end_date = video_of_end_date
        self._videos_before = videos_before

    def test(self, to_test: DataFrame) -> DataFrame:
        video_end_date_filter = (to_test[track.FRAME] <= self._frame) & (
            to_test[track.VIDEO_NAME] == self._video_of_end_date
        )
        videos_before_date_filter = to_test[track.VIDEO_NAME].isin(self._videos_before)
        date_filter = video_end_date_filter | videos_before_date_filter
        return to_test[date_filter]


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
        return to_test.loc[to_test[self._column_name].isin(self._classifications)]


class DataFrameFilterBuilder(FilterBuilder[DataFrame, DataFrame]):
    """A builder used to build a `DataFrameFilter`."""

    def __init__(self, current_frame: GetCurrentFrame, get_videos: GetVideos) -> None:
        super().__init__()
        self._current_frame = current_frame
        self._get_videos = get_videos
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

        current_frame = self._current_frame.get_frame_number_for(start_date)
        videos_after = [video.name for video in self._get_videos.get_after(start_date)]
        current_video = self._get_videos.get(start_date)
        current_video_name = current_video.name if current_video else videos_after[0]
        self._extend_complex_predicate(
            DataFrameStartsAtOrAfterFrame(
                column_name=track.FRAME,
                frame=current_frame,
                video_of_start_date=current_video_name,
                videos_after=videos_after,
            )
            # DataFrameStartsAtOrAfterDate(self._occurrence_column, start_date)
        )

    def add_ends_before_or_at_date_predicate(self, end_date: datetime) -> None:
        if self._occurrence_column is None:
            return

        current_frame = self._current_frame.get_frame_number_for(end_date)
        videos_before = [video.name for video in self._get_videos.get_before(end_date)]
        current_video = self._get_videos.get(end_date)
        current_video_name = current_video.name if current_video else videos_before[-1]
        self._extend_complex_predicate(
            DataFrameEndsBeforeOrAtFrame(
                column_name=track.FRAME,
                frame=current_frame,
                video_of_end_date=current_video_name,
                videos_before=videos_before,
            )
            # DataFrameEndsBeforeOrAtDate(self._occurrence_column, end_date)
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
