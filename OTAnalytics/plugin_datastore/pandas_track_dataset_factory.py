from typing import Protocol

from OTAnalytics.domain.track_dataset.track_dataset import (
    TRACK_GEOMETRY_FACTORY,
    TrackDataset,
)
from OTAnalytics.plugin_datastore.track_store import (
    PandasTrackClassificationCalculator,
    PandasTrackDataset,
)


class PandasTrackDatasetFactory(Protocol):
    def from_dataset(self, other: TrackDataset) -> PandasTrackDataset: ...


class TypeCheckingPandasTrackDatasetFactory:
    """Factory class for creating PandasTrackDataset objects from TrackDataset objects.

    Args:
        track_geometry_factory (TRACK_GEOMETRY_FACTORY): used for creating track
            geometries for the dataset.
        calculator (PandasTrackClassificationCalculator): used for calculating the track
            classification tracks.
    """

    def __init__(
        self,
        track_geometry_factory: TRACK_GEOMETRY_FACTORY,
        calculator: PandasTrackClassificationCalculator,
    ) -> None:
        self.track_geometry_factory = track_geometry_factory
        self.calculator = calculator

    def from_dataset(self, track_dataset: TrackDataset) -> PandasTrackDataset:
        """
        Creates an instance of PandasTrackDataset from a given TrackDataset.

        Args:
            track_dataset: the TrackDataset to create an instance of PandasTrackDataset.

        Returns:
            PandasTrackDataset: A Pandas-based implementation of the track dataset.
        """
        if isinstance(track_dataset, PandasTrackDataset):
            return track_dataset
        else:
            return PandasTrackDataset.from_list(
                track_dataset.as_list(),
                self.track_geometry_factory,
                self.calculator,
            )
