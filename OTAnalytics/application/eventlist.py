from OTAnalytics.domain.event import Event
from OTAnalytics.domain.track_dataset import TrackDataset


class SceneActionDetector:
    """Detect when a road user enters or leaves the scene."""

    def detect(self, tracks: TrackDataset) -> list[Event]:
        """Detect all enter and leave scene events.

        Args:
            tracks (Iterable[Track]): the tracks under inspection

        Returns:
            Iterable[Event]: the scene events
        """
        events: list[Event] = []
        tracks.apply_to_first_segments(events.append)
        tracks.apply_to_last_segments(events.append)
        return events
