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


class ClearRepositories:
    """Clear all repositories used within OTAnalytics.

    Args:
        clear_all_events (ClearAllEvents): use case to clear event repository.
        clear_all_flows (ClearAllFlows): use case to clear flow repository.
        clear_all_sections (ClearAllSections): use case to clear section repository.
        clear_all_track_to_videos (ClearAllTrackToVideos): use case to clear track
            to video repository.
        clear_all_tracks (ClearAllTracks): use case to clear track repository.
        clear_all_videos (ClearAllVideos): use case to clear video repository.
    """

    def __init__(
        self,
        clear_all_events: ClearAllEvents,
        clear_all_flows: ClearAllFlows,
        clear_all_intersections: ClearAllIntersections,
        clear_all_sections: ClearAllSections,
        clear_all_track_to_videos: ClearAllTrackToVideos,
        clear_all_tracks: ClearAllTracks,
        clear_all_videos: ClearAllVideos,
    ):
        self._clear_all_events = clear_all_events
        self._clear_all_flows = clear_all_flows
        self._clear_all_intersections = clear_all_intersections
        self._clear_all_sections = clear_all_sections
        self._clear_all_track_to_videos = clear_all_track_to_videos
        self._clear_all_tracks = clear_all_tracks
        self._clear_all_videos = clear_all_videos

    def __call__(self) -> None:
        """Clear all repositories used within OTAnalytics."""
        self._clear_all_events()
        self._clear_all_flows()
        self._clear_all_intersections.clear()
        self._clear_all_sections()
        self._clear_all_track_to_videos()
        self._clear_all_tracks()
        self._clear_all_videos()
