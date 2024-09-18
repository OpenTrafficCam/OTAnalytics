from typing import Any, Iterator, Sequence

from tqdm import tqdm

from OTAnalytics.domain.progress import Progressbar, ProgressbarBuilder


class TqdmProgressBar(Progressbar):
    def __init__(self, sequence: Sequence, description: str, unit: str) -> None:
        self.__sequence = sequence
        self.__description = description
        self.__unit = unit
        self.__current_iterator = self.__get_iterator()

    def __iter__(self) -> Iterator:
        self.__current_iterator = self.__get_iterator()
        return self

    def __get_iterator(self) -> Iterator:
        return tqdm(
            iterable=self.__sequence,
            desc=self.__description,
            unit=self.__unit,
            total=len(self.__sequence),
        ).__iter__()

    def __next__(self) -> Any:
        return next(self.__current_iterator)


class TqdmBuilder(ProgressbarBuilder):
    def __call__(
        self, sequence: Sequence, description: str, unit: str
    ) -> TqdmProgressBar:
        return TqdmProgressBar(sequence, description, " " + unit)
