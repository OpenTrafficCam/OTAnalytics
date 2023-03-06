from pathlib import Path
from unittest.mock import Mock

from OTAnalytics.application.datastore import Datastore


class TestDatastore:
    def test_load_track_file(self) -> None:
        some_track = Mock()
        track_parser = Mock()
        track_parser.parse.return_value = [some_track]
        section_parser = Mock()
        store = Datastore(
            track_parser=track_parser,
            section_parser=section_parser,
        )
        some_file = Path("some.file.ottrk")

        store.load_track_file(some_file)

        track_parser.parse.assert_called_with(some_file)
        assert some_track in store._track_repository.get_all()
