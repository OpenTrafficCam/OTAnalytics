from pathlib import Path
from unittest.mock import Mock

from OTAnalytics.application.datastore import Datastore, Video
from OTAnalytics.domain.track import TrackId


class TestDatastore:
    def test_load_track_file(self) -> None:
        some_track = Mock()
        some_track.id = TrackId(1)
        some_video = Video(path=Path(""))
        track_parser = Mock()
        track_parser.parse.return_value = [some_track]
        section_parser = Mock()
        video_parser = Mock()
        video_parser.parse.return_value = [some_track.id], [some_video]
        store = Datastore(
            track_parser=track_parser,
            section_parser=section_parser,
            video_parser=video_parser,
        )
        some_file = Path("some.file.ottrk")

        store.load_track_file(some_file)

        track_parser.parse.assert_called_with(some_file)
        video_parser.parse.assert_called_with(some_file)
        assert some_track in store._track_repository.get_all()
        assert some_video == store._video_repository.get_video_for(some_track.id)
