from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable

from OTAnalytics.domain.event import Event
from OTAnalytics.domain.section import Section


class ExporterNotFoundError(Exception):
    pass


class EventListExporter(ABC):
    """
    Export the events (and sections) from their repositories to external file formats
    like CSV or Excel.
    These formats are not meant to be imported again, cause during export,
    information will be lost.
    """

    @abstractmethod
    def export(
        self, events: Iterable[Event], sections: Iterable[Section], file: Path
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_extension(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_name(self) -> str:
        raise NotImplementedError
