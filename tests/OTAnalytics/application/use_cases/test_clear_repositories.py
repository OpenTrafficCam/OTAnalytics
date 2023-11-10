from unittest.mock import Mock

from OTAnalytics.application.use_cases.clear_repositories import ClearRepositories
from OTAnalytics.application.use_cases.event_repository import ClearAllEvents
from OTAnalytics.application.use_cases.flow_repository import ClearAllFlows
from OTAnalytics.application.use_cases.intersection_repository import (
    ClearAllIntersections,
)
from OTAnalytics.application.use_cases.section_repository import ClearAllSections
from OTAnalytics.application.use_cases.track_repository import ClearAllTracks
from OTAnalytics.application.use_cases.track_to_video_repository import (
    ClearAllTrackToVideos,
)
from OTAnalytics.application.use_cases.video_repository import ClearAllVideos


class TestClearRepositories:
    def test_clear_repositories(self) -> None:
        clear_all_events = Mock(spec=ClearAllEvents)
        clear_all_flows = Mock(spec=ClearAllFlows)
        clear_all_intersections = Mock(spec=ClearAllIntersections)
        clear_all_sections = Mock(spec=ClearAllSections)
        clear_all_track_to_videos = Mock(spec=ClearAllTrackToVideos)
        clear_all_tracks = Mock(spec=ClearAllTracks)
        clear_all_videos = Mock(spec=ClearAllVideos)

        clear_repositories = ClearRepositories(
            clear_all_events,
            clear_all_flows,
            clear_all_intersections,
            clear_all_sections,
            clear_all_track_to_videos,
            clear_all_tracks,
            clear_all_videos,
        )
        clear_repositories()
        clear_all_events.assert_called_once()
        clear_all_flows.assert_called_once()
        clear_all_intersections.clear.assert_called_once()
        clear_all_sections.assert_called_once()
        clear_all_track_to_videos.assert_called_once()
        clear_all_tracks.assert_called_once()
        clear_all_videos.assert_called_once()
