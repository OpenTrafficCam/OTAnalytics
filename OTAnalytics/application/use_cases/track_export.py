from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TrackExportSpecification:
    save_path: Path


class ExportTracks(ABC):
    @abstractmethod
    def export(self, specification: TrackExportSpecification) -> None:
        raise NotImplementedError
