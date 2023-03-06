from pathlib import Path

from application.datastore import SectionParser, TrackParser
from domain.section import Section
from domain.track import Track


class OttrkParser(TrackParser):
    def parse(self, file: Path) -> list[Track]:
        return []


class OtsectionParser(SectionParser):
    def parse(self, file: Path) -> list[Section]:
        return super().parse(file)
