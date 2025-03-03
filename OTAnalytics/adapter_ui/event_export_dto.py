from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class EventExportDto:
    file: Path
    export_format: str
