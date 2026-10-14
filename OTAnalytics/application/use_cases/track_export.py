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
    export_directory: Path
    export_filename_stem: str
    export_format: list[TrackFileFormat]
    export_mode: ExportMode


class ExportTracks(ABC):
    @abstractmethod
    def export(
        self,
        specification: TrackExportSpecification,
    ) -> None:
        raise NotImplementedError
