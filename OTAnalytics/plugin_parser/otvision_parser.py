from pathlib import Path
from typing import Tuple

from OTAnalytics.application.datastore import (
    SectionParser,
    TrackParser,
    Video,
    VideoParser,
)
from OTAnalytics.domain.section import Section
from OTAnalytics.domain.track import Track, TrackId


class OttrkParser(TrackParser):
    def parse(self, file: Path) -> list[Track]:
        return []


class OtsectionParser(SectionParser):
    def parse(self, file: Path) -> list[Section]:
        return []


class OttrkVideoParser(VideoParser):
    def parse(self, file: Path) -> Tuple[list[TrackId], list[Video]]:
        return [], []
