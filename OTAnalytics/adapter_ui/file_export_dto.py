from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ExportFileDto:
    file: Path
    export_format: str
