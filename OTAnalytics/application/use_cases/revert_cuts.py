from OTAnalytics.domain.track_dataset.track_dataset import TrackIdSet
from OTAnalytics.domain.track_repository import TrackRepository


class RevertCuts:
    """Use case handling the reverting of cuts on tracks.

    This class provides functionality to revert cuts performed on tracks
    by their original track ids using a track repository.

    Args:
        track_repository(TrackRepository): Repository that manages track data.
    """

    def __init__(self, track_repository: TrackRepository) -> None:
        self._track_repository = track_repository

    def revert(self, original_ids: TrackIdSet) -> None:
        """Revert cuts for tracks with the specified original track IDs.

        This method reverts cuts for tracks identified by their original IDs
        by delegating to the track repository.

        Args:
            original_ids (TrackIdSet): original track IDs for which cuts should
                be reverted.
        """
        self._track_repository.revert_cuts_for(original_ids)
