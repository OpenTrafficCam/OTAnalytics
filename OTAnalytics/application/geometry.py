from abc import ABC, abstractmethod
from functools import singledispatchmethod
from typing import Generic, Iterable, TypeVar

from OTAnalytics.domain.geometry import RelativeOffsetCoordinate
from OTAnalytics.domain.track import Track

LINE = TypeVar("LINE")
AREA = TypeVar("AREA")


class GeometryBuilder(ABC, Generic[LINE, AREA]):
    @singledispatchmethod
    @abstractmethod
    def create_section(self) -> LINE | AREA:
        raise NotImplementedError

    @abstractmethod
    def create_track(self, track: Track, offset: RelativeOffsetCoordinate) -> LINE:
        raise NotImplementedError

    @abstractmethod
    def create_line_segments(self, geometry: LINE) -> Iterable[LINE]:
        raise NotImplementedError
