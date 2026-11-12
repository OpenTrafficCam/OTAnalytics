from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class GeoTrackExportSpecification:
    """Where to write the geo track file of a chunk.

    Attributes:
        export_directory: directory the file is written to.
        export_filename_stem: file name prefix, the timestamp is appended.
    """

    export_directory: Path
    export_filename_stem: str


class ExportGeoTracks(ABC):
    """Export reduced trajectories (id, class, geo coordinate, time)."""

    @abstractmethod
    def export(self, specification: GeoTrackExportSpecification) -> Path | None:
        """Write the geo tracks of all tracks in the repository.

        Returns:
            Path | None: the written file or None if no detection has a geo
                coordinate (nothing is written then).
        """
        raise NotImplementedError
