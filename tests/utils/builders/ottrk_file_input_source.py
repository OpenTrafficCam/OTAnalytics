from pathlib import Path
from typing import Iterable

from OTAnalytics.application.track_input_source import OttrkFileInputSource
from OTAnalytics.plugin_parser.otvision_parser import OttrkFormatFixer
from OTAnalytics.plugin_track_input_source.single_batch import (
    SingleBatchOttrkFileInputSource,
)


def create_ottrk_file_input_source(ottrk_files: Iterable[Path]) -> OttrkFileInputSource:
    return SingleBatchOttrkFileInputSource(
        format_fixer=OttrkFormatFixer(),
        track_files=set(ottrk_files),
    )
