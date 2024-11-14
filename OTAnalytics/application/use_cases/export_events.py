from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

from OTAnalytics.application.export_formats.export_mode import ExportMode
from OTAnalytics.domain.event import Event
from OTAnalytics.domain.section import Section


class ExporterNotFoundError(Exception):
    pass


@dataclass(frozen=True)
class EventExportSpecification:
    file: Path
    export_mode: ExportMode


class EventListExporter(ABC):
    """
    Export the events (and sections) from their repositories to external file formats
    like CSV or Excel.
    These formats are not meant to be imported again, cause during export,
    information will be lost.

    The given export specification defines the output format,
    the output file path and the export mode (overwrite, append, flush).
    """

    @abstractmethod
    def export(
        self,
        events: Iterable[Event],
        sections: Iterable[Section],
        export_specification: EventExportSpecification,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_extension(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_name(self) -> str:
        raise NotImplementedError


EventListExporterProvider = Callable[[str], EventListExporter]
