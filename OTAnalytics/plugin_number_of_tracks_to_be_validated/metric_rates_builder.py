from typing import Self

from pandas import DataFrame

from OTAnalytics.domain.track import TRACK_CLASSIFICATION

ADD_TO_VALIDATION_PERCENTAGE = 2.0


# SVZ_DATA = _to_dataframe(SVZ_CLASSIFICATION)


class MetricRatesBuilder:
    def __init__(self, base: dict) -> None:
        self._internal = base.copy()

    def build(self) -> dict:
        return self._internal

    def build_as_dataframe(self) -> DataFrame:
        return _to_dataframe(self._internal)

    def all_of(self, classification: str | list[str]) -> Self:
        classifications = (
            classification if isinstance(classification, list) else [classification]
        )
        for _classification in classifications:
            for group, threshold in self._internal[_classification].items():
                self._internal[_classification][group] = ADD_TO_VALIDATION_PERCENTAGE
        return self


def _to_dataframe(data: dict) -> DataFrame:
    dataframe = DataFrame.from_dict(data).T.reset_index()
    dataframe.rename(columns={"index": TRACK_CLASSIFICATION}, inplace=True)
    return dataframe
