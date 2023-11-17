from typing import Callable

from OTAnalytics.domain.track import TrackDataset, TrackGeometryDataset
from OTAnalytics.plugin_datastore.track_geometry_store.pygeos_store import (
    PygeosTrackGeometryDataset,
)

TRACK_GEOMETRY_DATASET_FACTORY = PygeosTrackGeometryDataset.from_track_dataset
TRACK_GEOMETRY_FACTORY = Callable[[TrackDataset], TrackGeometryDataset]
