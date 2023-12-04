from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, Mock, call, patch

from OTAnalytics.application.use_cases.load_track_files import LoadTrackFiles
from OTAnalytics.domain.track import TrackId
from OTAnalytics.domain.video import SimpleVideo

START_DATE = datetime(2023, 1, 1)


class TestLoadTrackFile:
    @patch("OTAnalytics.application.use_cases.load_track_files.LoadTrackFiles.load")
    def test_load_multiple_files(self, mock_load: Mock) -> None:
        some_file = Path("some.file.ottrk")
        other_file = Path("other.file.ottrk")
        progressbar = Mock()
        progressbar.return_value = [some_file, other_file]

        load_track_files = LoadTrackFiles(
            Mock(), Mock(), Mock(), Mock(), Mock(), Mock(), progressbar, Mock(), Mock()
        )
        load_track_files([some_file, other_file])
        assert mock_load.call_args_list == [call(some_file), call(other_file)]

    def test_load(self) -> None:
        track_repository = Mock()
        track_file_repository = Mock()
        track_parser = Mock()
        track_video_parser = Mock()
        video_repository = Mock()
        track_to_video_repository = Mock()
        progressbar = Mock()
        tracks_metadata = Mock()
        videos_metadata = Mock()

        some_track = Mock()
        some_track_id = TrackId("1")
        some_track.id = some_track_id
        some_video = SimpleVideo(
            video_reader=Mock(), path=Path(""), start_date=START_DATE
        )
        detection_metadata = Mock()
        parse_result = Mock()
        parse_result.tracks = [some_track]
        parse_result.metadata = detection_metadata
        track_parser.parse.return_value = parse_result
        track_video_parser.parse.return_value = [some_track_id], [some_video]

        order = MagicMock()
        order.track_parser = track_parser
        order.track_video_parser = track_video_parser
        order.video_repository = video_repository
        order.track_repository = track_repository
        order.track_to_video_repository = track_to_video_repository
        load_track_file = LoadTrackFiles(
            track_parser,
            track_video_parser,
            track_repository,
            track_file_repository,
            video_repository,
            track_to_video_repository,
            progressbar,
            tracks_metadata,
            videos_metadata,
        )
        some_file = Path("some.file.ottrk")
        load_track_file.load(some_file)

        assert order.mock_calls == [
            call.track_parser.parse(some_file),
            call.track_video_parser.parse(some_file, [some_track_id]),
            call.video_repository.add_all([some_video]),
            call.track_to_video_repository.add_all([some_track_id], [some_video]),
            call.track_repository.add_all([some_track]),
        ]
