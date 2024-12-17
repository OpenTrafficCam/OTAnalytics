from abc import ABC, abstractmethod

import pandas
from pandas import DataFrame

from OTAnalytics.domain.track import (
    CLASSIFICATION,
    CONFIDENCE,
    TRACK_CLASSIFICATION,
    TRACK_ID,
)

PERCENTILE = "percentile"
CLASSIFICATION_LENGTH = "classification_length"
Q_N = "Q_N"
DETECTION_RATE = "detection_rate"
DENOMINATOR = "denominator"


class DetectionRateCalculationStrategy(ABC):
    @abstractmethod
    def calculate(self, data: DataFrame) -> DataFrame:
        raise NotImplementedError


class DetectionRateByPercentile(DetectionRateCalculationStrategy):
    def __init__(self, percentile_value: float = 0.9) -> None:
        self._percentile_value = percentile_value

    def calculate(self, data: DataFrame) -> DataFrame:
        local_data = data.reset_index()[
            [TRACK_ID, TRACK_CLASSIFICATION, CLASSIFICATION, CONFIDENCE]
        ].set_index([TRACK_ID])
        track_classification = (
            local_data[TRACK_CLASSIFICATION]
            .reset_index()
            .drop_duplicates()
            .set_index(TRACK_ID)
        )
        percentile = local_data.groupby([TRACK_ID, CLASSIFICATION])[
            CONFIDENCE
        ].quantile(q=self._percentile_value, interpolation="higher")
        percentile.name = PERCENTILE
        classification_length = local_data.groupby([TRACK_ID, CLASSIFICATION])[
            CONFIDENCE
        ].count()
        classification_length.name = CLASSIFICATION_LENGTH

        merged = pandas.merge(
            left=percentile,
            right=classification_length,
            left_index=True,
            right_index=True,
            how="inner",
        )
        if len(percentile) != len(merged) != len(classification_length):
            raise IndexError("Grouping resulted in different sized data frames.")

        merged[Q_N] = merged[PERCENTILE] * merged[CLASSIFICATION_LENGTH]
        denominator = merged[Q_N].groupby([TRACK_ID]).agg("sum")
        denominator.name = DENOMINATOR
        merged = merged.merge(denominator, left_index=True, right_index=True)
        tracks = merged.reset_index().set_index([TRACK_ID])
        tracks = tracks.merge(track_classification, left_index=True, right_index=True)
        tracks = tracks.loc[tracks[CLASSIFICATION] == tracks[TRACK_CLASSIFICATION], :]
        tracks[DETECTION_RATE] = tracks[PERCENTILE] * tracks[Q_N] / tracks[DENOMINATOR]
        tracks = tracks.reset_index().set_index([TRACK_ID, TRACK_CLASSIFICATION])
        return tracks.loc[:, [DETECTION_RATE]]


class DetectionRateByMaxConfidence(DetectionRateCalculationStrategy):
    def calculate(self, data: DataFrame) -> DataFrame:
        data = data.loc[data[TRACK_CLASSIFICATION] == data[CLASSIFICATION], :]
        complete_len = data.groupby([TRACK_ID]).agg({CONFIDENCE: "max"})
        track_classification = (
            data.droplevel(1)[TRACK_CLASSIFICATION]
            .reset_index()
            .drop_duplicates()
            .set_index(TRACK_ID)
        )
        merged = pandas.merge(
            track_classification,
            complete_len,
            how="left",
            left_index=True,
            right_index=True,
        )
        merged.rename(columns={CONFIDENCE: DETECTION_RATE}, inplace=True)
        return merged.reset_index().set_index([TRACK_ID, TRACK_CLASSIFICATION])


class DetectionRateByLength(DetectionRateCalculationStrategy):
    def calculate(self, data: DataFrame) -> DataFrame:
        complete_len = data.groupby([TRACK_ID]).agg({CONFIDENCE: len})
        max_class_len = (
            data[data[CLASSIFICATION] == data[TRACK_CLASSIFICATION]]
            .groupby([TRACK_ID, CLASSIFICATION])[CONFIDENCE]
            .agg(len)
            .droplevel(1)
        )
        merged = pandas.merge(
            max_class_len, complete_len, left_index=True, right_index=True
        )
        merged[DETECTION_RATE] = merged[f"{CONFIDENCE}_x"] / merged[f"{CONFIDENCE}_y"]
        track_classification = (
            data.droplevel(1)[TRACK_CLASSIFICATION]
            .reset_index()
            .drop_duplicates()
            .set_index(TRACK_ID)
        )
        merged = merged.merge(
            track_classification, how="left", left_index=True, right_index=True
        )
        merged = merged.reset_index().set_index([TRACK_ID, TRACK_CLASSIFICATION])
        return merged.loc[:, [DETECTION_RATE]]
