from OTAnalytics.domain.track import Track, TrackRepository


class GetAllTracks:
    """Get all tracks from the track repository.

    Args:
        track_repository (TrackRepository): the track repository to get the tracks from.
    """

    def __init__(self, track_repository: TrackRepository) -> None:
        self._track_repository = track_repository

    def __call__(self) -> list[Track]:
        return self._track_repository.get_all()


class AddAllTracks:
    """Add tracks to the track repository.

    Args:
        track_repository (TrackRepository): the track repository to add the tracks to.
    """

    def __init__(self, track_repository: TrackRepository) -> None:
        self._track_repository = track_repository

    def __call__(self, tracks: list[Track]) -> None:
        self._track_repository.add_all(tracks)


class ClearAllTracks:
    """Clear the track repository.

    Args:
        track_repository (TrackRepository): the track repository to be cleared.
    """

    def __init__(self, track_repository: TrackRepository) -> None:
        self._track_repository = track_repository

    def __call__(self) -> None:
        self._track_repository.clear()
