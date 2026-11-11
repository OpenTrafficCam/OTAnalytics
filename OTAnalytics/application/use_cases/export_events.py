from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

from OTAnalytics.application.config import CONTEXT_FILE_TYPE_EVENTS
from OTAnalytics.application.export_formats.export_mode import ExportMode
from OTAnalytics.domain.event import Event
from OTAnalytics.domain.section import Section


class ExporterNotFoundError(Exception):
    pass


@dataclass(frozen=True)
class EventExportSpecification:
    export_directory: Path
    export_filename_stem: str
    export_mode: ExportMode


class EventListExporter(ABC):
    CONTEXT_FILE_TYPE = CONTEXT_FILE_TYPE_EVENTS
    """
    Export the events (and sections) from their repositories to external file formats
    like CSV or Excel.
    These formats are not meant to be imported again, cause during export,
    information will be lost.

    The given export specification defines the output format,
    the output file path and the export mode (overwrite, append, flush).
    """

    def export(
        self,
        events: Iterable[Event],
        sections: Iterable[Section],
        export_specification: EventExportSpecification,
    ) -> Path:
        save_file_path = self.derive_save_path_from(export_specification)
        self._export(save_file_path, events, sections, export_specification)
        return save_file_path

    @abstractmethod
    def _export(
        self,
        save_file_path: Path,
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

    def derive_save_path_from(
        self, export_specification: EventExportSpecification
    ) -> Path:
        return export_specification.export_directory / (
            f"{export_specification.export_filename_stem}.{self.CONTEXT_FILE_TYPE}"
            f"{self.get_extension()}"
        )


EventListExporterProvider = Callable[[str], EventListExporter]
