from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from OTAnalytics.application.export_formats.export_mode import ExportMode

CSV: str = "csv"
OTTRK: str = "ottrk"


class TrackFileFormat(Enum):
    CSV = CSV
    OTTRK = OTTRK


@dataclass(frozen=True)
class TrackExportSpecification:
    save_path: Path
    export_format: list[TrackFileFormat]
    export_mode: ExportMode


class ExportTracks(ABC):
    @abstractmethod
    def export(
        self,
        specification: TrackExportSpecification,
    ) -> None:
        raise NotImplementedError


class MultiExportTracks(ExportTracks):
    """
    Class representing a multi-format track exporter.
    """

    def __init__(self, exporter: dict[TrackFileFormat, ExportTracks]) -> None:
        """
        Initialize the MultiExportTracks object with a dictionary of ExportTracks
        objects for different formats.

        Args: exporter (dict[TrackFileFormat, ExportTracks]): A dictionary containing
            ExportTracks objects for each format.
        """
        self._exporter = exporter

    def export(self, specification: TrackExportSpecification) -> None:
        """
        Exports tracks using the specified format.

        Args: specification (TrackExportSpecification): The export specification
            containing the format and other necessary details.
        """
        for export_format in specification.export_format:
            if export_format in self._exporter.keys():
                self._exporter[export_format].export(specification)
