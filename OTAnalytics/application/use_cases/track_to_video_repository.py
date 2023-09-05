from OTAnalytics.application.datastore import TrackToVideoRepository


class ClearAllTrackToVideos:
    """Clear the track to video repository.

    Args:
        track_to_video_repository (TrackToVideoRepository): the repository to clear.
    """

    def __init__(self, track_to_video_repository: TrackToVideoRepository) -> None:
        self._track_to_video_repository = track_to_video_repository

    def __call__(self) -> None:
        """Clear the track to video repository."""
        self._track_to_video_repository.clear()
