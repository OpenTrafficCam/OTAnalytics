from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class EventFileDto:
    file: Path
    export_format: str
