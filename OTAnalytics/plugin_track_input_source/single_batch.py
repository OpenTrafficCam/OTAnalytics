from pathlib import Path
from typing import Iterator

from OTAnalytics.plugin_parser.otvision_parser import OttrkFormatFixer
from OTAnalytics.plugin_track_input_source.template import OttrkFileInputSourceTemplate


class SingleBatchOttrkFileInputSource(OttrkFileInputSourceTemplate):
    def __init__(self, format_fixer: OttrkFormatFixer, track_files: set[Path]) -> None:
        super().__init__(format_fixer)
        self._track_files = track_files

    def produce(self) -> Iterator[Path]:
        yield from self._sort_files(self._track_files)
