import bz2
from abc import ABC
from pathlib import Path
from typing import Iterable

import ijson

from OTAnalytics.application.track_input_source import OttrkFileInputSource
from OTAnalytics.plugin_parser import ottrk_dataformat
from OTAnalytics.plugin_parser.otvision_parser import OttrkFormatFixer


class OttrkFileInputSourceTemplate(OttrkFileInputSource, ABC):
    def __init__(
        self,
        format_fixer: OttrkFormatFixer,
    ) -> None:
        super().__init__()
        self._format_fixer = format_fixer

    def _sort_files(self, ottrk_files: Iterable[Path]) -> list[Path]:
        """
        Sort ottrk files by recorded_start_date in video metadata,
        only considers files with .ottrk extension
        """
        return list(
            sorted(
                filter(lambda p: p.is_file(), ottrk_files),
                key=self._start_date_metadata,
            )
        )

    def _start_date_metadata(self, ottrk_file: Path) -> float:
        json_events = parse_json_bz2_events(ottrk_file)
        metadata = metadata_from_json_events(json_events)
        metadata = self._format_fixer.fix_metadata(metadata)
        return float(
            metadata[ottrk_dataformat.VIDEO][ottrk_dataformat.RECORDED_START_DATE]
        )


def parse_json_bz2_events(path: Path) -> Iterable[tuple[str, str, str]]:
    """
    Provide lazy data stream reading the bzip2 compressed file
    at the given path and interpreting it as json objects.
    """
    with bz2.BZ2File(path) as stream:
        yield from ijson.parse(stream)


def metadata_from_json_events(parse_events: Iterable[tuple[str, str, str]]) -> dict:
    """
    Extract the metadata block of the ottrk data format
    from the given json parser event stream.
    """
    result: dict
    for data in ijson.items(parse_events, "metadata"):
        result = data
        break
    return result
