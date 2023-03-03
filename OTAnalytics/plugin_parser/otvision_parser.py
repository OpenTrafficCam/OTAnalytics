from pathlib import Path

from application.datastore import TrackParser
from domain.track import Track


class OttrkParser(TrackParser):
    def parse(self, file: Path) -> list[Track]:
        return []
