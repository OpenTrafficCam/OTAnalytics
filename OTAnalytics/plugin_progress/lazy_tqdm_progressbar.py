from typing import Any, Iterator

from tqdm import tqdm

from OTAnalytics.domain.progress import LazyProgressbarBuilder, Progressbar


class LazyTqdmProgressBar(Progressbar):
    def __init__(self, iterator: Iterator, description: str, unit: str) -> None:
        self._iterator = iterator
        self.__description = description
        self.__unit = unit
        self.__current_iterator = self._get_iterator()

    def __iter__(self) -> Iterator:
        return self

    def _get_iterator(self) -> Iterator:
        return tqdm(
            iterable=self._iterator,
            desc=self.__description,
            unit=self.__unit,
        ).__iter__()

    def __next__(self) -> Any:
        return next(self.__current_iterator)


class LazyTqdmBuilder(LazyProgressbarBuilder):
    def __call__(
        self, iterator: Iterator, description: str, unit: str
    ) -> LazyTqdmProgressBar:
        return LazyTqdmProgressBar(iterator, description, " " + unit)
